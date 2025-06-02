import sys
from memory_manager import MemoryManager
from utils import parse_address, read_addresses

def main():
    if len(sys.argv) != 2:
        print("Uso: python src/main.py <endereço_decimal_hexadecimal> ou <arquivo_de_endereços>")
        return

    input_arg = sys.argv[1]
    memory_manager = MemoryManager('data/data_memory.txt', 'data/backing_store.txt')

    try:
        addresses = []
        if input_arg.endswith('.txt'):
            addresses = read_addresses(input_arg)
        else:
            addresses = [parse_address(input_arg)]
    except Exception as e:
        print(e)
        return

    for address in addresses:
        print(f"\nEndereço virtual: {address} ({hex(address)})")

        if memory_manager.is_16bit(address):
            try:
                page, offset, value = memory_manager.access_16bit(address)
                print(f"→ Página: {page} | Offset: {offset}")
                print(f"→ Valor lido da memória: {value}")
            except Exception as e:
                print(f"Erro: {e}")

        else:
            try:
                dir_num, table_num, offset, value = memory_manager.access_32bit(address)
                print(f"→ Diretório: {dir_num} | Tabela: {table_num} | Offset: {offset}")
                print(f"→ Valor lido da memória: {value}")
            except Exception as e:
                print(f"Erro: {e}")

if __name__ == "__main__":
    main()
