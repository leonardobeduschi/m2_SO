def parse_address(address_str):
    try:
        if address_str.startswith("0x") or address_str.startswith("0X"):
            return int(address_str, 16)
        else:
            return int(address_str)
    except ValueError:
        raise ValueError(f"Endereço inválido: {address_str}")

def read_addresses(file_path):
    with open(file_path, 'r') as file:
        return [parse_address(line.strip()) for line in file if line.strip()]

def read_memory(file_path):
    with open(file_path, 'r') as file:
        return [int(line.strip()) for line in file if line.strip()]
