import os
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("DATABASE_URL", "sqlite://")

from app.models import Agendamento, Barbearia, Cliente, Servico, StatusAgendamento
from app.schemas import AgendamentoCreate
from app.services import criar_agendamento


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Session = sessionmaker(bind=engine)

    Barbearia.__table__.create(bind=engine)
    Servico.__table__.create(bind=engine)
    Cliente.__table__.create(bind=engine)
    Agendamento.__table__.create(bind=engine)

    session = Session()
    try:
        barbearia = Barbearia(
            nome="Barbearia Teste",
            telefone_whatsapp="5511999999999",
            horario_abertura="09:00",
            horario_fechamento="18:00",
        )
        session.add(barbearia)
        session.flush()

        servico = Servico(
            barbearia_id=barbearia.id,
            nome="Corte",
            preco=40.0,
            duracao_minutos=30,
        )
        session.add(servico)
        session.commit()

        yield session
    finally:
        session.close()


def _create_payload(inicio: datetime) -> AgendamentoCreate:
    return AgendamentoCreate(
        barbearia_id=1,
        servico_id=1,
        cliente_telefone="5511988887777",
        data_hora_inicio=inicio,
        data_hora_fim=inicio,
    )


def test_criar_agendamento_rejeita_colisao(db_session):
    cliente = Cliente(nome="Cliente 1", telefone="5511911111111")
    db_session.add(cliente)
    db_session.flush()

    inicio_existente = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    agendamento_existente = Agendamento(
        barbearia_id=1,
        servico_id=1,
        cliente_id=cliente.id,
        data_hora_inicio=inicio_existente,
        data_hora_fim=inicio_existente + timedelta(minutes=30),
        status=StatusAgendamento.AGENDADO,
    )
    db_session.add(agendamento_existente)
    db_session.commit()

    payload = _create_payload(inicio_existente + timedelta(minutes=15))

    with pytest.raises(HTTPException) as exc_info:
        criar_agendamento(db_session, payload)

    assert exc_info.value.status_code == 409
    assert "ocupado" in exc_info.value.detail


def test_criar_agendamento_rejeita_fora_do_expediente(db_session):
    inicio = (datetime.now() + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    payload = _create_payload(inicio)

    with pytest.raises(HTTPException) as exc_info:
        criar_agendamento(db_session, payload)

    assert exc_info.value.status_code == 400
    assert "expediente" in exc_info.value.detail


def test_criar_agendamento_rejeita_passado(db_session):
    inicio = (datetime.now() - timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    payload = _create_payload(inicio)

    with pytest.raises(HTTPException) as exc_info:
        criar_agendamento(db_session, payload)

    assert exc_info.value.status_code == 400
    assert "passado" in exc_info.value.detail
