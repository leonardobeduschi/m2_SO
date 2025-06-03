from collections import OrderedDict
from utils import read_memory, load_page_from_backing_store

PAGE_SIZE_16B = 256  # Tamanho da página para endereços de 16 bits
PAGE_SIZE_32B = 4096  # Tamanho da página para endereços de 32 bits

class PageTableEntry:
    def __init__(self, physical_address=None):
        self.valid = False
        self.accessed = False
        self.dirty = False
        self.physical_address = physical_address

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
        self.backing_store_path = backing_store_path  # Caminho do backing store
        self.page_table = {}  # Tabela de páginas (dicionário para 16 e 32 bits)
        self.tlb = TLB()  # Instancia TLB
        self.physical_memory_counter = 0  # Contador para alocar endereços físicos

    def is_16bit(self, address):  # Verifica se endereço é de 16 bits
        return address <= 0xFFFF

    def extract_16bit(self, address):  # Extrai número da página e offset (16 bits)
        if address > 0xFFFF:
            raise ValueError("Endereço fora do limite para 16 bits")
        page_number = (address >> 8) & 0xFF
        offset = address & 0xFF
        return page_number, offset

    def extract_32bit(self, address):  # Extrai diretório, tabela e offset (32 bits)
        if address > 0xFFFFFFFF:
            raise ValueError("Endereço fora do limite para 32 bits")
        dir_number = (address >> 22) & 0x3FF
        table_number = (address >> 12) & 0x3FF
        offset = address & 0xFFF
        return dir_number, table_number, offset

    def access_16bit(self, address):  # Acessa memória para endereços de 16 bits
        page, offset = self.extract_16bit(address)
        key = (page,)  # Chave para TLB
        output = {"tlb_hit": False, "page_hit": False, "loaded_from_backing_store": False}

        frame = self.tlb.get(key)  # Consulta TLB
        output["tlb_hit"] = frame is not None

        if not output["tlb_hit"]:
            if page not in self.page_table:
                self.page_table[page] = PageTableEntry()
            entry = self.page_table[page]
            if not entry.valid:
                output["page_hit"] = False
                output["loaded_from_backing_store"] = True
                # Carrega do backing store
                value = load_page_from_backing_store(page, self.backing_store_path)
                entry.physical_address = self.physical_memory_counter
                self.memory.append(value)  # Adiciona à memória física
                self.physical_memory_counter += 1
                entry.valid = True
                entry.accessed = True
                print(f"→ Page Fault: carregando página {page} da backing store.")
            else:
                output["page_hit"] = True
                entry.accessed = True
            frame = entry.physical_address
            self.tlb.put(key, frame)

        physical_address = frame * PAGE_SIZE_16B + offset  # Calcula endereço físico
        if physical_address >= len(self.memory):
            raise ValueError("Endereço físico fora da memória.")

        value = self.memory[physical_address]  # Lê valor da memória
        output["page_number"] = page
        output["offset"] = offset
        output["value"] = value
        return output

    def access_32bit(self, address):  # Acessa memória para endereços de 32 bits
        dir_num, table_num, offset = self.extract_32bit(address)
        key = (dir_num, table_num)  # Chave para TLB
        output = {"tlb_hit": False, "page_hit": False, "loaded_from_backing_store": False}

        frame = self.tlb.get(key)  # Consulta TLB
        output["tlb_hit"] = frame is not None

        if not output["tlb_hit"]:
            if dir_num not in self.page_table:
                self.page_table[dir_num] = {}
            dir_table = self.page_table[dir_num]
            if table_num not in dir_table:
                dir_table[table_num] = PageTableEntry()
            entry = dir_table[table_num]
            if not entry.valid:
                output["page_hit"] = False
                output["loaded_from_backing_store"] = True
                # Carrega do backing store
                page_number = (dir_num << 10) | table_num
                value = load_page_from_backing_store(page_number, self.backing_store_path)
                entry.physical_address = self.physical_memory_counter
                self.memory.append(value)  # Adiciona à memória física
                self.physical_memory_counter += 1
                entry.valid = True
                entry.accessed = True
                print(f"→ Page Fault na tabela {dir_num}-{table_num}: carregando da backing store.")
            else:
                output["page_hit"] = True
                entry.accessed = True
            frame = entry.physical_address
            self.tlb.put(key, frame)

        physical_address = frame * PAGE_SIZE_32B + offset  # Calcula endereço físico
        if physical_address >= len(self.memory):
            raise ValueError("Endereço físico fora da memória.")

        value = self.memory[physical_address]  # Lê valor da memória
        output["page_number"] = (dir_num, table_num)
        output["offset"] = offset
        output["value"] = value
        return output