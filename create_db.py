from app.database import engine, Base
from app.models import Barbearia, Servico, Cliente, Agendamento, ContextoConversa

def create_tables():
    print("Conectando ao banco de dados...")
    
    # pega todas as classes que herdam de 'Base' e cria as tabelas correspondentes
    # se elas não existirem.
    Base.metadata.create_all(bind=engine)
    
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    create_tables()