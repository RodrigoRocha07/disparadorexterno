from sqlalchemy.exc import OperationalError, DisconnectionError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
import logging
import time
import os
from mysql.connector.errors import DatabaseError, InterfaceError

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Carregar URL do banco de dados
database_url = "mysql+mysqlconnector://crm_impulse_user:dBVd(PlP]Z)3@crm-impulse.c7a0kiga29ky.us-east-2.rds.amazonaws.com/crm-impulse"

# Configurar o motor do SQLAlchemy com pool_pre_ping para verificar a conexão antes de usá-la
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=10,        # Tamanho do pool de conexões
    max_overflow=20,     # Número máximo de conexões adicionais
    pool_recycle=3600,   # Reciclar conexões após 3600 segundos (1 hora)
    pool_timeout=30,     # Tempo máximo de espera para uma conexão do pool (30 segundos)
    connect_args={"connect_timeout": 1000}  # Timeout de conexão do MySQL aumentado para um valor muito alto
)

# Configurar SessionLocal para criar sessões de banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para mapeamento das tabelas
Base = declarative_base()

def criar_db():
    # Criar todas as tabelas no banco de dados
    Base.metadata.create_all(bind=engine)

def get_db():
    retries = 3  # Número de tentativas de reconexão
    for attempt in range(retries):
        db = None
        try:
            db = SessionLocal()
            logger.info(f"Tentativa {attempt + 1}: Conexão ao banco de dados estabelecida.")
            yield db
            break  # Conexão bem-sucedida, sair do loop
        except (OperationalError, DisconnectionError, DatabaseError, InterfaceError) as e:
            logger.warning(f"Tentativa {attempt + 1} falhou com erro: {e}")
            if attempt < retries - 1:
                time.sleep(5)  # Esperar antes de tentar novamente
            else:
                logger.error("Todas as tentativas de conexão falharam. Levantando exceção.")
                raise e  # Levantar exceção se todas as tentativas falharem
        finally:
            if db:
                db.close()
                logger.info("Conexão ao banco de dados fechada.")
