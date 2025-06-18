from memoria import Memory
import tkinter as tk
from visual import MemoryGUI

def main():
    mem = Memory(max_size=32)

    mem.create_file("file2", 2)
    mem.create_file("file4", 4)
    mem.create_file("file8", 8)

    mem.allocate_file_worst_fit("file2")
    mem.allocate_file_worst_fit("file8")

    root = tk.Tk() #chama só a interface
    app = MemoryGUI(root, mem) #inicializa a interface com a memoria
    root.mainloop() #Isso mantém a janela aberta esperando as interações do usuário (clicar botões etc).

if __name__ == "__main__": 
    main() 
