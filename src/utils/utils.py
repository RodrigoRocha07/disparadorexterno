from src.infra.sqlalchemy.repositorios.repositorio import RepositorioCampaign, RepositorioUsers
from sqlalchemy.orm import sessionmaker
from joblib import Parallel, delayed
import numpy as np
import threading
import requests
import json
import time
from src.providers import codificador_5string

contador_global = [0]  # Variável global para contar o número de mensagens enviadas
n_mensagens_enviadas = [0]  # Variável global para contar o número de mensagens com sucesso (status 200)

def send_sms(phone, msg):
    url = 'http://0.0.0.0:8002/api_send_sms'
    #url = 'https://api.isendme.com/api?i=1184&token=095d9847-ed43-4486-ba15-45abce76447b' 
    #url = 'http://3.140.194.29:32007/fake_sendspeed'  # Url da api fake
    #url = 'http://0.0.0.0:8002/fake_sendspeed'

    
    
    headers = {
        'content-type': 'application/json'
    }
    data = {
        'user_phone': phone,
        'txt': msg
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code >= 200 and response.status_code < 300:
            print(f'Retorno da API - {response.json()}')
            return {"message": f"Envio de '{msg}' para {phone}", "severity": "success", "status_code": response.status_code}
        else:

            print(f"Erro ao enviar SMS: {response.status_code}, {response.text}")
            return {"message": f"Erro ao enviar SMS", "severity": "error", "status_code": response.status_code}
    except Exception as e:
        print(msg)
        print(f"Erro ao enviar SMS: {e}")
        return {"message": f"Erro ao enviar SMS: {e}", "severity": "error", "status_code": None}

# Função para dividir a lista
def dividir_lista(lista, n):
    array = np.array(lista)
    sublistas = np.array_split(array, n)
    matriz = [sublista.tolist() for sublista in sublistas]
    return matriz

# Função para preparar dados url única
def preparar_dados(mensagem, infos, id_campaign):
    lista_msg = []
    lista_telefones = []

    for info in infos:
        lista_telefones.append(info.infos['telefone'])
        msg = mensagem
        for key in info.infos:
            if key == 'url':
                hash_id_campanha = codificador_5string.encode(int(id_campaign), 3)
                hash_id_cliente = codificador_5string.encode(int(info.id), 5)
                msg = msg.replace(f"[{key}]", f'linksms.me/{hash_id_campanha}{hash_id_cliente}')
                #msg = msg.replace(f"[{key}]", f'http://127.0.0.1:8000/short/{hash_id_campanha}{hash_id_cliente}')

            else:
                msg = msg.replace(f"[{key}]", info.infos[key])
        lista_msg.append(msg)
    return lista_msg, lista_telefones

# Função para enviar mensagens
def enviar_mensagens(lista_telefones, lista_msg, lock):
    global contador_global, n_mensagens_enviadas
    for indice, mensagem in enumerate(lista_msg):
        try:
            response = send_sms(lista_telefones[indice], mensagem)
            with lock:
                contador_global[0] += 1
                if response['status_code'] >= 200 and response['status_code'] < 300:
                    n_mensagens_enviadas[0] += 1
            print(f"{response} - Mensagens enviadas: {contador_global[0]}")
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")

# Função principal para disparar SMS
def disparo_sms(mensagem, infos, id_campaign, n: int = 200):
    inicio = time.time()
    
    lista_msg, lista_telefones = preparar_dados(mensagem, infos, id_campaign)

    matriz_telefone = dividir_lista(lista_telefones, n)
    matriz_mensagem = dividir_lista(lista_msg, n)

    lock = threading.Lock()

    try:
        with Parallel(n_jobs=min(n, len(lista_telefones)), backend='threading') as parallel:
            parallel(delayed(enviar_mensagens)(matriz_telefone[i], matriz_mensagem[i], lock) for i in range(len(matriz_telefone)))
    except Exception as e:
        print(f"Erro no processamento paralelo: {e}")

    fim = time.time()
    tempo_execucao = fim - inicio

    return contador_global[0], tempo_execucao

def disparo_mt(infos, db, id_campaign):
    global contador_global, n_mensagens_enviadas
    contador_global = [0]  # Reinicializa o contador global antes de iniciar o processo
    n_mensagens_enviadas = [0]  # Reinicializa o contador de mensagens enviadas com sucesso

    n_enviados = 0
    tempo_envio = 0
    tamanho_parte = len(infos) // 1
    partes = [infos[i:i + tamanho_parte] for i in range(0, len(infos), tamanho_parte)]
    
    if len(partes) > 10:
        partes[9].extend([item for sublist in partes[10:] for item in sublist])
        partes = partes[:10]

    for parte in partes:
        campanha = RepositorioCampaign(db).campanha_por_id(id_campaign)
        if campanha.status != '0':
            contador, tempo = disparo_sms(campanha.message, parte, id_campaign)
            n_enviados = contador
            tempo_envio += tempo
            tempo_minutos = tempo_envio / 60
            velocidade = contador_global[0] / tempo_minutos
            print(150 * '/')
            print(f'Quantidade de envios: {n_enviados}')
            print(f'Quantidade de mensagens com sucesso: {n_mensagens_enviadas[0]}')
        else:
            print('Campanha pausada!')
            break
        RepositorioCampaign(db).somarDisparos(id_campaign, int(n_enviados))

    campanha = RepositorioCampaign(db).campanha_por_id(id_campaign)
    RepositorioCampaign(db).somarDisparosEfetuados(id_campaign,int(n_mensagens_enviadas[0]))
    RepositorioUsers(db).retirar_creditos(campanha.user_id,int(n_mensagens_enviadas[0]))



    print(f'Tempo de execução: {tempo_envio:.2f} segundos')
    print(f'Tempo de execução: {tempo_minutos:.2f} minutos')
    print(f'Velocidade de disparo: {velocidade:.2f} mensagens/minuto')

    Session = sessionmaker(bind=db.bind)
    with Session() as new_session:
        RepositorioCampaign(new_session).finalizar(id_campaign)
