from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

# Pega a URL do Supabase
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Cria a engine de conexão
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Cria a fábrica de sessões (fazer queries)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria a classe Base que os models herdam
Base = declarative_base()

# Função utilitária para pegar o banco nas rotas (Dependency Injection)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()