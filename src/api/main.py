from fastapi import FastAPI, Depends, Request, HTTPException, Depends,BackgroundTasks
from src.infra.sqlalchemy.repositorios.repositorio import *
from src.infra.sqlalchemy.config.database import get_db
from fastapi.middleware.cors import CORSMiddleware
from src.providers import token_provider
from src.utils.utils import send_sms
from src.utils import utils


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,  # Permite envio de credenciais (cookies, headers de autorização, etc)
    allow_methods=["*"],  # Permite todos os métodos HTTP (GET, POST, PUT, DELETE, etc)
    allow_headers=["*"],  # Permite todos os headers
)

@app.get('/')
async def home():
    return "Disparador externo"


async def token_authentication_in_header(request: Request):
    header = request.headers
    if 'authorization' in header:
        token = header['authorization'].split(' ')[1]
        if token_provider.verificar_token(token):
            return
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    raise HTTPException(status_code=401, detail="Credenciais não fornecidas")



#disparador interno
@app.post('/disparo_fracionado/{id_campaign}/{id_inicio}/{id_fim}')
async def envio_teste(request: Request,id_campaign,id_inicio,id_fim, background_tasks: BackgroundTasks,db=Depends(get_db),authenticated: None = Depends(token_authentication_in_header)):
    RepositorioCampaign(db).ativar(id_campaign)
    campanha = RepositorioCampaign(db).campanha_por_id(id_campaign)
    creditos_disponiveis = RepositorioUsers(db).mostrar_creditos(campanha.user_id)
    
    if creditos_disponiveis >= campanha.disparos_ate:
        base = RepositorioBases(db).get_base_id(campanha.base_id)
        infos = RepositorioInfos(db).pegar_infos_entre_ids(base.id,id_inicio, id_fim)
        background_tasks.add_task(utils.disparo_mt, infos,db, id_campaign)
  
        return {'message':'disparo iniciado','severity':'success'}
    else:
        return {'message':'Creditos insuficientes','severity':'success'}




