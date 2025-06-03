def parse_address(address_str):  # Converte endereço de string para inteiro
    try:
        if address_str.startswith("0x") or address_str.startswith("0X"):  # Suporta hexadecimal
            return int(address_str, 16)
        else:
            return int(address_str)  # Suporta decimal
    except ValueError:
        raise ValueError(f"Endereço inválido: {address_str}")

def read_addresses(file_path):  # Lê endereços de um arquivo
    with open(file_path, 'r') as file:
        return [parse_address(line.strip()) for line in file if line.strip()]

def read_memory(file_path):  # Lê conteúdo da memória de um arquivo
    with open(file_path, 'r') as file:
        return [int(line.strip()) for line in file if line.strip()]

def create_backing_store(filename="data/backing_store.txt", num_pages=1024):
    """Cria um arquivo backing_store.txt com dados fictícios para cada página."""
    import os
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            for i in range(num_pages):
                f.write(f"Página {i}: {i}\n")  # Valor fictício (pode ser ajustado)

def load_page_from_backing_store(page_number, filename="data/backing_store.txt"):
    """Lê uma página do backing store."""
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            if page_number < len(lines):
                return int(lines[page_number].strip().split(": ")[1])  # Retorna o valor da página
            else:
                raise ValueError(f"Página {page_number} não encontrada no backing store")
    except FileNotFoundError:
        raise FileNotFoundError("Backing store não encontrado")