from sqlalchemy import Column, Integer, String, ForeignKey, Boolean,func,DateTime
from src.infra.sqlalchemy.config.database import Base
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
import pytz
from datetime import datetime

BRASILIA_TZ = pytz.timezone('America/Sao_Paulo')

def now_in_brasilia():
    return datetime.now(BRASILIA_TZ)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), unique=False, nullable=False)
    password = Column(String(50), nullable=False)
    token = Column(String(255))
    admin = Column(Boolean,nullable=False)
    creditos = Column(Integer,nullable=False)
    createdAt = Column(DateTime, default=now_in_brasilia)    
    updatedAt = Column(DateTime, default=now_in_brasilia, onupdate=now_in_brasilia)
 

    
class Bases(Base):
    __tablename__ = 'bases'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    chaves = Column(String(255), nullable=False)
    infos = relationship('Infos', back_populates='base', cascade='all, delete-orphan')
    campaigns = relationship('Campaign', back_populates='base')
    user_id = Column(Integer, ForeignKey('users.id'))
    createdAt = Column(DateTime, default=now_in_brasilia)    
    updatedAt = Column(DateTime, default=now_in_brasilia, onupdate=now_in_brasilia)

class Infos(Base):
    __tablename__ = 'infos'
    id = Column(Integer, primary_key=True, index=True)
    infos = Column(JSON, nullable=False)
    bases_id = Column(Integer, ForeignKey('bases.id'), nullable=False)
    base = relationship('Bases', back_populates='infos')
    createdAt = Column(DateTime, default=now_in_brasilia)    
    updatedAt = Column(DateTime, default=now_in_brasilia, onupdate=now_in_brasilia)
 


    @staticmethod
    def count_infos(session: Session):
        return session.query(func.count(Infos.id)).scalar()



class Campaign(Base):
    __tablename__ = 'campaigns'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    message = Column(String(255), nullable=False)
    schedule = Column(Boolean, nullable=False)
    date = Column(String(50), nullable=False)
    hour = Column(String(50), nullable=False)
    base_id = Column(Integer, ForeignKey('bases.id'), nullable=False)
    status = Column(String(50), nullable=False)
    base = relationship('Bases', back_populates='campaigns')
    public_token_id = Column(Integer, ForeignKey('public_tokens.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    disparos_efetuados = Column(Integer, nullable=False)
    disparos_de = Column(Integer, nullable=False)
    disparos_ate = Column(Integer, nullable=False)
    clicks = Column(Integer, nullable=False)
    createdAt = Column(DateTime, default=now_in_brasilia)    
    updatedAt = Column(DateTime, default=now_in_brasilia, onupdate=now_in_brasilia)
    links = relationship('Links', back_populates='campaign', cascade="all, delete-orphan")


class Links(Base):
    __tablename__ = 'links'
    id = Column(Integer, primary_key=True, index=True)
    url_original = Column(String(50), nullable=False)
    url_encurtada = Column(String(50), nullable=False)
    id_campaign = Column(Integer, ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False)
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
    campaign = relationship('Campaign', back_populates='links')

class PublicTokens(Base):
    __tablename__ = 'public_tokens'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    token = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    createdAt = Column(DateTime, default=now_in_brasilia)    
    updatedAt = Column(DateTime, default=now_in_brasilia, onupdate=now_in_brasilia)



class TabelaTeste(Base):
    __tablename__ = 'tabela_teste'
    id = Column(Integer, primary_key=True, index=True)
    contador = Column(Integer)
    teste = Column(Integer)
    createdAt = Column(DateTime, default=now_in_brasilia)    
    updatedAt = Column(DateTime, default=now_in_brasilia, onupdate=now_in_brasilia)
 

