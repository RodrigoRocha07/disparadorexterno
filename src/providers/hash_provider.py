from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(schemes=['bcrypt'])

def gerar_hash(texto):
    return pwd_context.hash(texto)

def verificar_hash(texto, texto_hash):
    return pwd_context.verify(texto, texto_hash)


import hashlib
import base64
import secrets
import time

# Função para gerar um link encurtado único
def gerar_link_encurtado(url_original):
    # Adicionar um timestamp atual para garantir unicidade
    timestamp = str(time.time())

    # Concatenar a URL original com o timestamp
    url_com_timestamp = url_original + timestamp

    # Gerar hash SHA-256 da combinação da URL com o timestamp
    hash_obj = hashlib.sha256(url_com_timestamp.encode())
    hash_digest = hash_obj.digest()

    # Codificar o hash em base64
    link_encurtado = base64.urlsafe_b64encode(hash_digest).decode()[:5]

    return link_encurtado