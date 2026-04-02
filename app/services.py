from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Agendamento, Barbearia, Cliente, Servico, StatusAgendamento
from app.schemas import AgendamentoCreate


def buscar_cliente_por_telefone(db: Session, telefone: str):
    return db.query(Cliente).filter(Cliente.telefone == telefone).first()


def get_horarios_disponiveis(db: Session, barbearia_id: int, servico_id: int, data_str: str):
    try:
        data_alvo = datetime.strptime(data_str, "%Y-%m-%d").date()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Data invalida. Use YYYY-MM-DD") from exc

    barbearia = db.query(Barbearia).filter(Barbearia.id == barbearia_id).first()
    servico = db.query(Servico).filter(Servico.id == servico_id, Servico.barbearia_id == barbearia_id).first()

    if not barbearia or not servico:
        raise HTTPException(status_code=404, detail="Barbearia ou servico nao encontrado")

    hora_abre = datetime.strptime(barbearia.horario_abertura, "%H:%M").time()
    hora_fecha = datetime.strptime(barbearia.horario_fechamento, "%H:%M").time()

    inicio_dia = datetime.combine(data_alvo, hora_abre)
    fim_dia = datetime.combine(data_alvo, hora_fecha)

    agendamentos_existentes = db.query(Agendamento).filter(
        Agendamento.barbearia_id == barbearia_id,
        Agendamento.status != StatusAgendamento.CANCELADO,
        Agendamento.data_hora_inicio < fim_dia,
        Agendamento.data_hora_fim > inicio_dia,
    ).all()

    horarios_livres = []
    slot_atual = inicio_dia
    duracao_servico = timedelta(minutes=servico.duracao_minutos)
    delta_intervalo = timedelta(minutes=30)

    while slot_atual + duracao_servico <= fim_dia:
        horario_livre = True
        fim_do_slot = slot_atual + duracao_servico

        for agendamento in agendamentos_existentes:
            if slot_atual < agendamento.data_hora_fim and fim_do_slot > agendamento.data_hora_inicio:
                horario_livre = False
                break

        if horario_livre:
            horarios_livres.append(slot_atual.strftime("%H:%M"))

        slot_atual += delta_intervalo

    return horarios_livres


def criar_agendamento(db: Session, dados: AgendamentoCreate):
    cliente = buscar_cliente_por_telefone(db, dados.cliente_telefone)
    if not cliente:
        cliente = Cliente(telefone=dados.cliente_telefone, nome="Novo Cliente")
        db.add(cliente)
        db.commit()
        db.refresh(cliente)

    barbearia = db.query(Barbearia).filter(Barbearia.id == dados.barbearia_id).first()
    servico = db.query(Servico).filter(
        Servico.id == dados.servico_id,
        Servico.barbearia_id == dados.barbearia_id,
    ).first()

    if not barbearia:
        raise HTTPException(status_code=404, detail="Barbearia nao encontrada")
    if not servico:
        raise HTTPException(status_code=404, detail="Servico nao encontrado")

    hora_abre = datetime.strptime(barbearia.horario_abertura, "%H:%M").time()
    hora_fecha = datetime.strptime(barbearia.horario_fechamento, "%H:%M").time()

    inicio = dados.data_hora_inicio
    fim = inicio + timedelta(minutes=servico.duracao_minutos)

    if inicio < datetime.now():
        raise HTTPException(status_code=400, detail="Nao e permitido agendar no passado")

    inicio_funcionamento = datetime.combine(inicio.date(), hora_abre)
    fim_funcionamento = datetime.combine(inicio.date(), hora_fecha)
    if inicio < inicio_funcionamento or fim > fim_funcionamento:
        raise HTTPException(status_code=400, detail="Horario fora do expediente")

    colisao = db.query(Agendamento).filter(
        Agendamento.barbearia_id == dados.barbearia_id,
        Agendamento.status != StatusAgendamento.CANCELADO,
        Agendamento.data_hora_inicio < fim,
        Agendamento.data_hora_fim > inicio,
    ).first()

    if colisao:
        raise HTTPException(status_code=409, detail="Esse horario ja esta ocupado")

    novo_agendamento = Agendamento(
        barbearia_id=dados.barbearia_id,
        cliente_id=cliente.id,
        servico_id=dados.servico_id,
        data_hora_inicio=inicio,
        data_hora_fim=fim,
        status=StatusAgendamento.AGENDADO,
    )

    db.add(novo_agendamento)
    db.commit()
    db.refresh(novo_agendamento)

    return novo_agendamento
