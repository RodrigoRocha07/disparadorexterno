from src.providers.token_provider import criar_token, criar_token_publico
from src.infra.sqlalchemy.config.database import criar_db, get_db
from src.schemas.erros import ErroPersonalizado, MissingDataError
from src.infra.sqlalchemy.models.models import User, Bases
from src.infra.sqlalchemy.models import models
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.schemas import schemas
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean,func
from src.providers import hash_provider, codificador_5string
from typing import List, Dict
import uuid
from sqlalchemy import or_







class RepositorioUsers():
    def __init__(self, db:Session):
        self.db = db
    
    
    def mostrar_creditos(self, user_id):
        db_usuario = self.db.query(User).filter(User.id == user_id).first()
        return db_usuario.creditos



    def retirar_creditos(self, user_id, creditos):
        db_usuario = self.db.query(User).filter(User.id == user_id).first()
        db_usuario.creditos = db_usuario.creditos - creditos
        self.db.commit()
        self.db.refresh(db_usuario)
        return db_usuario








class RepositorioBases():
    def __init__(self, db:Session):
        self.db = db

    def get_base_id(self, base_id):
        return self.db.query(models.Bases).filter(models.Bases.id == base_id).first()









class RepositorioInfos():
    def __init__(self, db:Session):
        self.db = db

    def count_infos_bases_id(self, base_id):
        count = self.db.query(func.count(models.Infos.id)).filter(models.Infos.bases_id == base_id).scalar()
        return count


    def pegar_lote_ids_infos(self, base_id, inicio, limite):
        lista_db_infos = (
            self.db.query(models.Infos)
            .filter(models.Infos.bases_id == base_id)
            .offset(inicio-1)
            .limit(limite)
            .all()
            )
        lista_ids = []
        for info in lista_db_infos:
            lista_ids.append(info.id)
        return lista_ids
    
    def pegar_infos_entre_ids(self, base_id: int, id_inicio: int, id_fim: int):
        infos = (
            self.db.query(models.Infos)
            .filter(
                models.Infos.bases_id == base_id,
                models.Infos.id >= id_inicio,
                models.Infos.id <= id_fim
            )
            .order_by(models.Infos.id)
            .all()
        )
        return infos



class RepositorioLinksEncurtados():
    def __init__(self, db:Session):
        self.db = db
    
    def criar(self, campanha):


        lista_msg = campanha.message.split(" ")

        for palavra in lista_msg:
            if "http" in palavra or "www" in palavra:
                url_original = palavra


        db_link = models.Links(
            url_original = url_original,
            id_campaign = campanha.id,
            url_encurtada = 'https://www.linksms.me/' + codificador_5string.encode(int(campanha.id),3))
            #url_encurtada = 'http://127.0.0.1:8000/short/' + codificador_5string.encode(int(campanha.id),3))
        
        
        self.db.add(db_link)
        self.db.commit()
        self.db.refresh(db_link)
        return (db_link)

    def listar(self):
        return self.db.query(models.Links).all()

    def linkPeloEncurtado(self, link_encurtado):
        db_link = self.db.query(models.Links).filter(models.Links.url_encurtada == link_encurtado).first()

        return db_link.url_original

class RepositorioCampaign():
    def __init__(self, db:Session):
        self.db = db
        
    def criar(self, campanha:schemas.Campaign):
        try:
            if not campanha.name:
                raise MissingDataError("É necessario colocar o nome da campanha.")
            if not campanha.message:
                raise MissingDataError("É necessario colocar uma mensagem de campanha.")
            if not campanha.base_id:
                raise MissingDataError("Selecione uma base.")
          
            if self.db.query(models.Bases).filter(models.Bases.id == campanha.base_id).first() == None:
                raise MissingDataError("Nenhuma base cadastrada com esse ID")


            db_campanha = models.Campaign(
                name = campanha.name,
                message = campanha.message,
                schedule = campanha.schedule,
                date = campanha.date,
                hour = campanha.hour,
                base_id = campanha.base_id,
                status = campanha.status,
                public_token_id = campanha.public_token_id,
                disparos_de = campanha.disparos_de,
                disparos_ate = self.db.query(func.count(models.Infos.id)).filter(models.Infos.bases_id == campanha.base_id).scalar(),#total de infos
                clicks = campanha.clicks,
                user_id = campanha.user_id,
                disparos_efetuados = campanha.disparos_efetuados
                )

            self.db.add(db_campanha)
            self.db.commit()
            self.db.refresh(db_campanha)

            return db_campanha
        except MissingDataError as e:
            return {'message':e.message, 'severity':'error'}
    
    def listar(self):    #db.query(Item).order_by(Item.id.desc()).all()
        return self.db.query(models.Campaign).order_by(models.Campaign.id.desc()).all()

    
    def  listar_by_user_id(self, user_id):
        return self.db.query(models.Campaign).filter(models.Campaign.user_id == user_id).order_by(models.Campaign.id.desc()).all()
    
    def listar_ids(self):
        campanhas = self.db.query(models.Campaign.id).all()
        return [id[0] for id in campanhas] 
    
    def campanha_por_id(self, campaigns_id):
        campanha = self.db.query(models.Campaign).filter(models.Campaign.id == campaigns_id).first()
        self.db.close()
        return campanha

    def atualizar(self, campaigns_id, campaing:schemas.Campaign):
        db_campaing = self.db.query(models.Campaign).filter(models.Campaign.id == campaigns_id).first()
        db_campaing.name = campaing.name
        db_campaing.message = campaing.message
        db_campaing.schedule = campaing.schedule
        db_campaing.date = campaing.date
        db_campaing.hour = campaing.hour
        db_campaing.base_id = campaing.base_id
        db_campaing.status = campaing.status
        self.db.commit()
        self.db.refresh(db_campaing)
        return db_campaing
    
    def mudar_mensagem(self, id_campanha, url_encurtada):
        db_campaing = self.db.query(models.Campaign).filter(models.Campaign.id == id_campanha).first()

        lista_msg = db_campaing.message.split(" ")
        nova_mensagem = []
        for palavra in lista_msg:
            if "http" in palavra or 'www' in palavra:
                palavra = url_encurtada
            nova_mensagem.append(palavra)

        db_campaing.message  = ' '.join(nova_mensagem)
        self.db.commit()
        self.db.refresh(db_campaing)
        return db_campaing
    
    def deletar(self, campaigns_id):
        db_campaigns = self.db.query(models.Campaign).filter(models.Campaign.id == campaigns_id).first()
        self.db.delete(db_campaigns)
        self.db.commit()
        return 
    
    def ativar(self, id_campanha):
        db_campaing = self.db.query(models.Campaign).filter(models.Campaign.id == id_campanha).first()
        db_campaing.status = '1'
        self.db.commit()
        return {'message':'campanha ativada','severity':'success'}
    

    def desativar(self, id_campanha):
        db_campaing = self.db.query(models.Campaign).filter(models.Campaign.id == id_campanha).first()
        db_campaing.status = '0'
        self.db.commit()
        self.db.close()
        return {'message':'campanha desativada','severity':'success'}
    

    def finalizar(self, id_campanha):
        db_campaing = self.db.query(models.Campaign).filter(models.Campaign.id == id_campanha).first()
        db_campaing.status = '2'
        self.db.commit()
        return {'message':'campanha finalizada','severity':'success'}
    
    def somarDisparos(self,id_campanha,disparados):
        db_campaing = self.db.query(models.Campaign).filter(models.Campaign.id == id_campanha).first()
        db_campaing.disparos_de = disparados
        self.db.commit()
        self.db.refresh(db_campaing)
        print()
        return db_campaing
    
    def somarDisparosEfetuados(self,id_campanha,disparados_efetuados):
        db_campaing = self.db.query(models.Campaign).filter(models.Campaign.id == id_campanha).first()
        db_campaing.disparos_efetuados = disparados_efetuados
        self.db.commit()
        self.db.refresh(db_campaing)
        return db_campaing
    
    def zerarDisparos(self,id_campanha):
        db_campaing = self.db.query(models.Campaign).filter(models.Campaign.id == id_campanha).first()
        db_campaing.disparos_de = 0
        self.db.commit()
        self.db.refresh(db_campaing)
        return db_campaing


    def mostrarDisparos(self,id_campanha):
        db_campaing = self.db.query(models.Campaign).filter(models.Campaign.id == id_campanha).first()
        return db_campaing.disparos_de

    def somarClick(self, id_campanha):
        db_campaing = self.db.query(models.Campaign).filter(models.Campaign.id == id_campanha).first()
        db_campaing.clicks += 1
        self.db.commit()
        self.db.refresh(db_campaing)


    def filtrarMensagem(self, texto):
        db_campanhas_message = self.db.query(models.Campaign).filter(models.Campaign.message.like(f'%{texto}%')).all()
        db_campanhas_name = self.db.query(models.Campaign).filter(models.Campaign.name.like(f'%{texto}%')).all()
        db_campanhas = list(set(db_campanhas_message + db_campanhas_name))
        return db_campanhas
  