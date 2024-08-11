import string

# Definindo os caracteres permitidos para a codificação
ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits  # 62 caracteres

def encode(number,n):
    # Certifica-se de que o número não é maior do que o que pode ser representado com 5 caracteres
    if number >= len(ALPHABET) ** n:
        raise ValueError("Número muito grande para ser codificado em 5 caracteres.")
    
    encoded = []
    for _ in range(n):
        number, rem = divmod(number, len(ALPHABET))
        encoded.append(ALPHABET[rem])
    
    return ''.join(reversed(encoded))

def decode(encoded_str):
    number = 0
    for char in encoded_str:
        number = number * len(ALPHABET) + ALPHABET.index(char)
    return number
