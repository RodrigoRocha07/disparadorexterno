import jwt
from datetime import datetime, timezone, timedelta

SECRET_KEY = "IMPULSEMAX"
ALGORITHM = 'HS256'
TIME_EXP = 60*24*366
TIME_EXP_anual = 60*24*366


def criar_token(data: dict):
    dados = data.copy()
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=TIME_EXP)
    dados.update({'exp': expiracao.timestamp()})

    token_jwt = jwt.encode(dados, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt

def criar_token_publico(data: dict):
    dados = data.copy()
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=TIME_EXP_anual)
    dados.update({'exp': expiracao.timestamp()})

    token_jwt = jwt.encode(dados, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt


def verificar_token(token):
    try:
        dados = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if 'exp' in dados:
            expiracao = datetime.utcfromtimestamp(dados['exp']).replace(tzinfo=timezone.utc)
            if expiracao > datetime.now(timezone.utc):
                return True
        return False
    except jwt.PyJWTError:
        return False

def tempo_validade_restante(token):
    try:
        dados = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if 'exp' in dados:
            expiracao = datetime.utcfromtimestamp(dados['exp']).replace(tzinfo=timezone.utc)
            agora = datetime.now(timezone.utc)
            if expiracao > agora:
                tempo_restante = expiracao - agora
                minutos, segundos = divmod(tempo_restante.total_seconds(), 60)
                return f'{int(minutos)} Minutos {int(segundos)} Segundos'
        return '0 Minutos 0 Segundos'
    except jwt.PyJWTError:
        return '0 Minutos 0 Segundos'
