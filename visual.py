import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

#o tkinder é a tela e o mat... é para os gráficos

class MemoryGUI:
    def __init__(self, master, mem):
        self.master = master
        self.mem = mem
        self.master.title("Visualização de Memória")

        self.plots = [
            self.plot_memory_usage,
            self.plot_pages
        ]
        self.current_plot = 0

        self.figure = Figure(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack()

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master) #é a barra onde mexe o grafico
        self.toolbar.update()
        self.toolbar.pack()

        nav_frame = tk.Frame(master)
        nav_frame.pack(pady=5)

        self.prev_button = tk.Button(nav_frame, text="Anterior", command=self.show_prev_plot)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.next_button = tk.Button(nav_frame, text="Próximo", command=self.show_next_plot)
        self.next_button.pack(side=tk.LEFT, padx=5)

        action_frame = tk.Frame(master)
        action_frame.pack(pady=10)

        self.file_var = tk.StringVar(value="file4")
        self.file_selector = tk.OptionMenu(action_frame, self.file_var, "file2", "file4", "file8")
        self.file_selector.pack(side=tk.LEFT, padx=5)

        self.alloc_button = tk.Button(action_frame, text="Alocar (Worst Fit)", command=self.allocate_selected_file)
        self.alloc_button.pack(side=tk.LEFT, padx=5)

        self.dealloc_button = tk.Button(action_frame, text="Desalocar", command=self.deallocate_selected_file)
        self.dealloc_button.pack(side=tk.LEFT, padx=5)

        self.id_entry = tk.Entry(action_frame, width=5)
        self.id_entry.pack(side=tk.LEFT, padx=5)

        self.dealloc_id_button = tk.Button(action_frame, text="Desalocar ID", command=self.deallocate_by_id)
        self.dealloc_id_button.pack(side=tk.LEFT, padx=5)

        self.compact_button = tk.Button(action_frame, text="Compactar", command=self.compact_memory)
        self.compact_button.pack(side=tk.LEFT, padx=5)

        self.message_label = tk.Label(master, text="", fg="blue")
        self.message_label.pack(pady=5)

        self.show_plot()

    def show_message(self, message, color="blue"):
        self.message_label.config(text=message, fg=color)

    def show_plot(self): #atualização
        self.figure.clf()
        plot_func = self.plots[self.current_plot]
        plot_func(self.figure)
        self.canvas.draw()

    def show_next_plot(self): 
        self.current_plot = (self.current_plot + 1) % len(self.plots)
        self.show_plot()

    def show_prev_plot(self):
        self.current_plot = (self.current_plot - 1) % len(self.plots)
        self.show_plot()

    def plot_memory_usage(self, fig): #chama o grafico colorido
        total = self.mem.max_size
        used = self.mem.allocated
        free = total - used
        labels = ['Alocado', 'Livre']
        sizes = [used, free]
        colors = ['red', 'green']  

        ax = fig.add_subplot(111)
        ax.bar(labels, sizes, color=colors)
        ax.set_title('Uso da Memória')
        ax.set_ylabel('Bytes')

    def plot_pages(self, fig): #mostra o grafico colorido
        ax = fig.add_subplot(111)
        for i, page in enumerate(self.mem.pages):
            color = 'green' if page.allocated > 0 else 'gray'
            label = f"{page.file_name or 'vazio'} ({page.allocated}/{page.size})"
            ax.barh(i, page.size, color='lightgray', edgecolor='black')
            ax.barh(i, page.allocated, color=color)
            ax.text(page.size + 0.2, i, f"ID {page.id if page.id else 'N/A'} - {label}", va='center')
        ax.set_title('Páginas de Memória')
        ax.set_xlabel('Tamanho da Página (bytes)')
        ax.set_yticks([])

    def allocate_selected_file(self):
        file_name = self.file_var.get()
        success = self.mem.allocate_file_worst_fit(file_name)
        if success:
            self.show_message(f"{file_name} alocado com sucesso!", color="green")
        else:
            messagebox.showerror("Erro", f"Memória cheia")
        self.show_plot()

    def deallocate_selected_file(self):
        file_name = self.file_var.get()
        found = False
        for page in self.mem.pages:
            if page.file_name == file_name:
                self.mem.deallocate_page_by_id(page.id)
                found = True
        if found:
            self.show_message(f"{file_name} desalocado com sucesso!", color="green")
        else:
            messagebox.showwarning("Aviso", f"{file_name} não está alocado.")
        self.show_plot()

    def deallocate_by_id(self):
        try:
            page_id = int(self.id_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "ID inválido")
            return
        if self.mem.deallocate_page_by_id(page_id):
            self.show_message(f"Pág. {page_id} desalocada com sucesso.", color="green")
        else:
            messagebox.showwarning("Aviso", f"Pág. {page_id} não encontrada.")
        self.show_plot()

    def compact_memory(self):
        self.mem.compact_memory()
        self.show_message("Memória compactada!", color="green")
        self.show_plot()
