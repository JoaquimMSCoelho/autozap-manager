from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Nome do arquivo do banco de dados (será criado automaticamente)
SQLALCHEMY_DATABASE_URL = "sqlite:///./autozap.db"

# Criação do motor de conexão (check_same_thread=False é necessário apenas para SQLite)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Sessão local para interagir com o banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base para nossos modelos (tabelas) herdarem
Base = declarative_base()

# Dependência para injetar a sessão nas rotas da API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
