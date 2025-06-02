from collections import OrderedDict
from utils import read_memory

PAGE_SIZE_16B = 256  # Tamanho da página para endereços de 16 bits
PAGE_SIZE_32B = 4096  # Tamanho da página para endereços de 32 bits

class TLB:
    def __init__(self, capacity=16):  # Inicializa TLB com capacidade padrão de 16 entradas
        self.cache = OrderedDict()  # Cache LRU para armazenar mapeamentos

    def get(self, key):  # Busca entrada na TLB
        if key in self.cache:
            self.cache.move_to_end(key)  # Move para o final (LRU)
            return self.cache[key]
        return None  # TLB miss

    def put(self, key, value):  # Insere ou atualiza entrada na TLB
        if key in self.cache:
            self.cache.move_to_end(key)  # Move para o final se já existe
        elif len(self.cache) >= 16:
            self.cache.popitem(last=False)  # Remove entrada mais antiga (LRU)
        self.cache[key] = value  # Adiciona nova entrada

class MemoryManager:
    def __init__(self, memory_path, backing_store_path):  # Inicializa gerenciador de memória
        self.memory = read_memory(memory_path)  # Carrega memória do arquivo
        self.backing_store = [i for i in range(1000, 2000)]  # Simula backing store
        self.page_table = {}  # Tabela de páginas
        self.tlb = TLB()  # Instancia TLB

    def is_16bit(self, address):  # Verifica se endereço é de 16 bits
        return address <= 0xFFFF

    def extract_16bit(self, address):  # Extrai número da página e offset (16 bits)
        page_number = (address >> 8) & 0xFF
        offset = address & 0xFF
        return page_number, offset

    def extract_32bit(self, address):  # Extrai diretório, tabela e offset (32 bits)
        dir_number = (address >> 22) & 0x3FF
        table_number = (address >> 12) & 0x3FF
        offset = address & 0xFFF
        return dir_number, table_number, offset

    def access_16bit(self, address):  # Acessa memória para endereços de 16 bits
        page, offset = self.extract_16bit(address)
        key = (page, )  # Chave para TLB

        frame = self.tlb.get(key)  # Consulta TLB
        tlb_hit = frame is not None

        if not tlb_hit:  # Se TLB miss
            if page not in self.page_table:  # Verifica page fault
                print(f"→ Page Fault: carregando página {page} da backing store.")
                self.page_table[page] = page  # Simula carregamento
            frame = self.page_table[page]
            self.tlb.put(key, frame)  # Atualiza TLB

        physical_address = frame * PAGE_SIZE_16B + offset  # Calcula endereço físico

        if physical_address >= len(self.memory):  # Verifica limite de memória
            raise ValueError("Endereço físico fora da memória.")

        value = self.memory[physical_address]  # Lê valor da memória
        print(f"→ TLB {'Hit' if tlb_hit else 'Miss'} | Page {'Hit' if page in self.page_table else 'Fault'}")
        return page, offset, value

    def access_32bit(self, address):  # Acessa memória para endereços de 32 bits
        dir_num, table_num, offset = self.extract_32bit(address)
        key = (dir_num, table_num)  # Chave para TLB

        frame = self.tlb.get(key)  # Consulta TLB
        tlb_hit = frame is not None

        if not tlb_hit:  # Se TLB miss
            if dir_num not in self.page_table:  # Verifica diretório
                self.page_table[dir_num] = {}  # Cria novo diretório
                print(f"→ Page Fault no diretório {dir_num}: criando Page Table.")

            dir_table = self.page_table[dir_num]

            if table_num not in dir_table:  # Verifica tabela
                print(f"→ Page Fault na tabela {dir_num}-{table_num}: carregando da backing store.")
                dir_table[table_num] = (dir_num * 1024 + table_num)  # Simula frame

            frame = dir_table[table_num]
            self.tlb.put(key, frame)  # Atualiza TLB

        physical_address = frame * PAGE_SIZE_32B + offset  # Calcula endereço físico

        if physical_address >= len(self.memory):  # Verifica limite de memória
            raise ValueError("Endereço físico fora da memória.")

        value = self.memory[physical_address]  # Lê valor da memória
        print(f"→ TLB {'Hit' if tlb_hit else 'Miss'} | Page {'Hit' if tlb_hit else 'Fault'}")
        return dir_num, table_num, offset, value