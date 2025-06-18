import os
import time

class Page:

    def __init__(self, page_id, size, allocated=0, file_name=""):
        self.id = page_id
        self.size = size
        self.allocated = allocated
        self.file_name = file_name

class Memory:

    def __init__(self, max_size): 
        self.max_size = max_size
        self.allocated = 0
        self.pages = []
        self.next_id = 1
        self.stats = {
            'worst_fit': {'success': 0, 'attempts': 0, 'time_total': 0.0},
        }

    def _generate_id(self):
        page_id = self.next_id
        self.next_id += 1
        return page_id

    def create_file(self, file_name, size):
        if size <= 0:
            return
        with open(file_name, 'wb') as f:
            f.write(b'\0' * size)

    def _allocate_multi_pages(self, file_size, file_name, strategy): #filtra, organiza, atualiza, tentar preencher espaços se não cria outra
        start = time.time()
        free_pages = [p for p in self.pages if p.file_name == ""]

        if strategy == 'worst_fit':
            free_pages.sort(key=lambda p: p.size, reverse=True)
        

        remaining = file_size
        for page in free_pages:
            if remaining <= 0:
                break
            alloc = min(page.size, remaining)
            page.allocated = alloc
            page.file_name = file_name
            if page.id is None:
                page.id = self._generate_id()
            remaining -= alloc
            self.allocated += alloc

        while remaining > 0 and self.allocated + remaining <= self.max_size:
            new_page = Page(self._generate_id(), remaining, remaining, file_name)
            self.pages.append(new_page)
            self.allocated += remaining
            remaining = 0

        success = remaining == 0
        self._track(strategy, start, success)
        return success

    def allocate_file_worst_fit(self, file_name):
        if not os.path.exists(file_name):
            return False
        file_size = os.path.getsize(file_name)
        if self.allocated + file_size > self.max_size:
            return False
        return self._allocate_multi_pages(file_size, file_name, 'worst_fit')

    def deallocate_page_by_id(self, page_id):
        for page in self.pages:
            if page.id == page_id:
                self.allocated -= page.allocated
                page.allocated = 0
                page.file_name = ""
                page.id = None
                return True
        return False

    def compact_memory(self):
        total_free = sum(p.size for p in self.pages if p.allocated == 0)
        new_pages = [Page(self._generate_id(), p.allocated, p.allocated, p.file_name) 
                     for p in self.pages if p.allocated > 0]

        if total_free > 0:
            new_pages.append(Page(None, total_free, 0, ""))  # Única página vazia

        self.pages = new_pages
        print("Compactação concluída.")

    def _track(self, strategy, start_time, success): #Atualiza estatísticas (quantas vezes tentou alocar, tempo gasto, quantas vezes teve sucesso)
        self.stats[strategy]['attempts'] += 1
        self.stats[strategy]['time_total'] += time.time() - start_time
        if success:
            self.stats[strategy]['success'] += 1
