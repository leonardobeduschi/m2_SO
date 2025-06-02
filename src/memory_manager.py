from collections import OrderedDict
from utils import read_memory

PAGE_SIZE_16B = 256
PAGE_SIZE_32B = 4096

class TLB:
    def __init__(self, capacity=16):
        self.cache = OrderedDict()

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= 16:
            self.cache.popitem(last=False)
        self.cache[key] = value

class MemoryManager:
    def __init__(self, memory_path, backing_store_path):
        self.memory = read_memory(memory_path)
        self.backing_store = [i for i in range(1000, 2000)]  # Simulado
        self.page_table = {}
        self.tlb = TLB()

    def is_16bit(self, address):
        return address <= 0xFFFF

    def extract_16bit(self, address):
        page_number = (address >> 8) & 0xFF
        offset = address & 0xFF
        return page_number, offset

    def extract_32bit(self, address):
        dir_number = (address >> 22) & 0x3FF
        table_number = (address >> 12) & 0x3FF
        offset = address & 0xFFF
        return dir_number, table_number, offset

    def access_16bit(self, address):
        page, offset = self.extract_16bit(address)
        key = (page, )

        frame = self.tlb.get(key)
        tlb_hit = frame is not None

        if not tlb_hit:
            if page not in self.page_table:
                print(f"→ Page Fault: carregando página {page} da backing store.")
                self.page_table[page] = page
            frame = self.page_table[page]
            self.tlb.put(key, frame)

        physical_address = frame * PAGE_SIZE_16B + offset

        if physical_address >= len(self.memory):
            raise ValueError("Endereço físico fora da memória.")

        value = self.memory[physical_address]
        print(f"→ TLB {'Hit' if tlb_hit else 'Miss'} | Page {'Hit' if page in self.page_table else 'Fault'}")
        return page, offset, value

    def access_32bit(self, address):
        dir_num, table_num, offset = self.extract_32bit(address)
        key = (dir_num, table_num)

        frame = self.tlb.get(key)
        tlb_hit = frame is not None

        if not tlb_hit:
            if dir_num not in self.page_table:
                self.page_table[dir_num] = {}
                print(f"→ Page Fault no diretório {dir_num}: criando Page Table.")

            dir_table = self.page_table[dir_num]

            if table_num not in dir_table:
                print(f"→ Page Fault na tabela {dir_num}-{table_num}: carregando da backing store.")
                dir_table[table_num] = (dir_num * 1024 + table_num)  # Simula frame

            frame = dir_table[table_num]
            self.tlb.put(key, frame)

        physical_address = frame * PAGE_SIZE_32B + offset

        if physical_address >= len(self.memory):
            raise ValueError("Endereço físico fora da memória.")

        value = self.memory[physical_address]
        print(f"→ TLB {'Hit' if tlb_hit else 'Miss'} | Page {'Hit' if tlb_hit else 'Fault'}")
        return dir_num, table_num, offset, value
