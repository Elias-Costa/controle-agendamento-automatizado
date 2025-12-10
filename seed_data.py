from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import Barbearia, Servico

def seed_data():
    db = SessionLocal()
    
    # Verifica se já existe barbearia para não duplicar
    existe = db.query(Barbearia).first()
    if existe:
        print("O banco já possui dados. Pulando seed.")
        return

    print("Criando dados iniciais...")

    # Cria a Barbearia Exemplo
    barbearia = Barbearia(
        nome="Barbearia do Dev",
        telefone_whatsapp="5511999999999",
        horario_abertura="09:00",
        horario_fechamento="19:00"
    )
    db.add(barbearia)
    db.commit() # Salva para gerar o ID
    db.refresh(barbearia)

    # Serviços para essa barbearia
    servicos = [
        Servico(nome="Corte Clássico", preco=45.00, duracao_minutos=45, barbearia_id=barbearia.id),
        Servico(nome="Barba", preco=35.00, duracao_minutos=30, barbearia_id=barbearia.id),
        Servico(nome="Combo (Corte + Barba)", preco=70.00, duracao_minutos=60, barbearia_id=barbearia.id),
    ]
    
    db.add_all(servicos)
    db.commit()
    
    print("Dados inseridos com sucesso!")
    print(f"Barbearia ID: {barbearia.id}")
    print("Serviços criados.")
    
    db.close()

if __name__ == "__main__":
    seed_data()