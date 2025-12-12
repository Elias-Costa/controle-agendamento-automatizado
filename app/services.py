from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date, time
from app.models import Agendamento, Barbearia, Servico, Cliente, StatusAgendamento
from app.schemas import AgendamentoCreate
from fastapi import HTTPException

def buscar_cliente_por_telefone(db: Session, telefone: str):
    return db.query(Cliente).filter(Cliente.telefone == telefone).first()

def get_horarios_disponiveis(db: Session, barbearia_id: int, servico_id: int, data_str: str):
    """
    Lógica principal: Fatiar o dia em slots de 30min e verificar se o serviço cabe
    sem bater em agendamentos existentes.
    """
    # 1. Converter string "YYYY-MM-DD" para objeto date
    try:
        data_alvo = datetime.strptime(data_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Data inválida. Use YYYY-MM-DD")

    # 2. Buscar dados da Barbearia e Serviço
    barbearia = db.query(Barbearia).filter(Barbearia.id == barbearia_id).first()
    servico = db.query(Servico).filter(Servico.id == servico_id).first()

    if not barbearia or not servico:
        raise HTTPException(status_code=404, detail="Barbearia ou Serviço não encontrado")

    # 3. Transformar horários de string ("09:00") para datetime completo
    # Ex: 2025-12-12 09:00:00
    hora_abre = datetime.strptime(barbearia.horario_abertura, "%H:%M").time()
    hora_fecha = datetime.strptime(barbearia.horario_fechamento, "%H:%M").time()

    inicio_dia = datetime.combine(data_alvo, hora_abre)
    fim_dia = datetime.combine(data_alvo, hora_fecha)

    # 4. Buscar agendamentos JÁ EXISTENTES nesse dia (para evitar colisão)
    # Filtramos apenas os que não estão cancelados
    agendamentos_existentes = db.query(Agendamento).filter(
        Agendamento.barbearia_id == barbearia_id,
        Agendamento.status != StatusAgendamento.CANCELADO,
        Agendamento.data_hora_inicio >= inicio_dia,
        Agendamento.data_hora_inicio < fim_dia
    ).all()

    # 5. O Algoritmo de Varredura (Slotting)
    horarios_livres = []
    slot_atual = inicio_dia
    duracao_servico = timedelta(minutes=servico.duracao_minutos)
    delta_intervalo = timedelta(minutes=30) # Mostra horários a cada 30 min (ex: 14:00, 14:30)

    while slot_atual + duracao_servico <= fim_dia:
        horario_livre = True
        fim_do_slot = slot_atual + duracao_servico

        # Verifica colisão com cada agendamento existente
        for agendamento in agendamentos_existentes:
            inicio_ocupado = agendamento.data_hora_inicio
            fim_ocupado = agendamento.data_hora_fim

            # Lógica de Colisão:
            # (Novo começa antes do Velho terminar) E (Novo termina depois do Velho começar)
            # Ex: Quero 14:00-14:30. Já existe 13:45-14:15.
            # 14:00 < 14:15 (Sim) E 14:30 > 13:45 (Sim) -> COLISÃO!
            if slot_atual < fim_ocupado and fim_do_slot > inicio_ocupado:
                horario_livre = False
                break
        
        if horario_livre:
            # Adiciona na lista formatado bonito (ex: "14:30")
            horarios_livres.append(slot_atual.strftime("%H:%M"))

        # Avança para o próximo teste (ex: de 09:00 vai para 09:30)
        slot_atual += delta_intervalo

    return horarios_livres

def criar_agendamento(db: Session, dados: AgendamentoCreate):
    """
    Cria o agendamento, mas também gerencia o cliente (cria se não existir).
    """
    # 1. Verifica/Cria Cliente
    cliente = buscar_cliente_por_telefone(db, dados.cliente_telefone)
    if not cliente:
        # Se é a primeira vez, cria o cliente só com o telefone
        cliente = Cliente(telefone=dados.cliente_telefone, nome="Novo Cliente")
        db.add(cliente)
        db.commit()
        db.refresh(cliente)

    # 2. Busca o Serviço para saber a duração e calcular o fim
    servico = db.query(Servico).filter(Servico.id == dados.servico_id).first()
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    # Calcula horário final
    # Nota: dados.data_hora_inicio já vem como datetime graças ao Pydantic
    data_fim = dados.data_hora_inicio + timedelta(minutes=servico.duracao_minutos)

    # 3. Validação Final de Disponibilidade (Double Check)
    # É importante verificar de novo para garantir que ninguém agendou no milissegundo anterior
    colisao = db.query(Agendamento).filter(
        Agendamento.barbearia_id == dados.barbearia_id,
        Agendamento.status != StatusAgendamento.CANCELADO,
        Agendamento.data_hora_inicio < data_fim,
        Agendamento.data_hora_fim > dados.data_hora_inicio
    ).first()

    if colisao:
        raise HTTPException(status_code=409, detail="Ops! Esse horário acabou de ser ocupado.")

    # 4. Salva o Agendamento
    novo_agendamento = Agendamento(
        barbearia_id=dados.barbearia_id,
        cliente_id=cliente.id,
        servico_id=dados.servico_id,
        data_hora_inicio=dados.data_hora_inicio,
        data_hora_fim=data_fim,
        status=StatusAgendamento.AGENDADO
    )

    db.add(novo_agendamento)
    db.commit()
    db.refresh(novo_agendamento)
    
    return novo_agendamento