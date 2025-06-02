import sys
from memory_manager import MemoryManager
from utils import parse_address, read_addresses

def main():  # Função principal
    if len(sys.argv) != 2:  # Verifica argumento de entrada
        print("Uso: python src/main.py <endereço_decimal_hexadecimal> ou <arquivo_de_endereços>")
        return

    input_arg = sys.argv[1]  # Obtém argumento
    memory_manager = MemoryManager('data/data_memory.txt', 'data/backing_store.txt')  # Inicializa gerenciador

    try:
        addresses = []
        if input_arg.endswith('.txt'):  # Se entrada for arquivo
            addresses = read_addresses(input_arg)
        else:
            addresses = [parse_address(input_arg)]  # Se entrada for endereço único
    except Exception as e:
        print(e)
        return

    for address in addresses:  # Processa cada endereço
        print(f"\nEndereço virtual: {address} ({hex(address)})")

        if memory_manager.is_16bit(address):  # Endereço de 16 bits
            try:
                page, offset, value = memory_manager.access_16bit(address)
                print(f"→ página: {page} | Offset: {offset}")
                print(f"→ Valor lido da memória: {value}")
            except Exception as e:
                print(f"Erro: {e}")

        else:  # Endereço de 32 bits
            try:
                dir_num, table_num, offset, value = memory_manager.access_32bit(address)
                print(f"→ Diretório: {dir_num} | Tabela: {table_num} | Offset: {offset}")
                print(f"→ Valor lido da memória: {value}")
            except Exception as e:
                print(f"Erro: {e}")

if __name__ == "__main__":
    main()  # Executa programa