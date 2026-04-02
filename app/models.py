import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum as SqEnum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from app.database import Base


class StatusAgendamento(str, enum.Enum):
    AGENDADO = "AGENDADO"
    CANCELADO = "CANCELADO"
    REALIZADO = "REALIZADO"
    NO_SHOW = "NO_SHOW"


class StatusConversa(str, enum.Enum):
    LIVRE = "LIVRE"
    AGUARDANDO_DATA = "AGUARDANDO_DATA"
    AGUARDANDO_HORARIO = "AGUARDANDO_HORARIO"
    AGUARDANDO_CONFIRMACAO = "AGUARDANDO_CONFIRMACAO"
    ATENDIMENTO_HUMANO = "ATENDIMENTO_HUMANO"


class Barbearia(Base):
    __tablename__ = "barbearias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    telefone_whatsapp = Column(String, unique=True, index=True, nullable=False)
    timezone = Column(String, default="America/Sao_Paulo")
    horario_abertura = Column(String, default="09:00")
    horario_fechamento = Column(String, default="18:00")

    servicos = relationship("Servico", back_populates="barbearia")
    agendamentos = relationship("Agendamento", back_populates="barbearia")


class Servico(Base):
    __tablename__ = "servicos"

    id = Column(Integer, primary_key=True, index=True)
    barbearia_id = Column(Integer, ForeignKey("barbearias.id"))
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=True)
    duracao_minutos = Column(Integer, default=30)

    barbearia = relationship("Barbearia", back_populates="servicos")
    agendamentos = relationship("Agendamento", back_populates="servico")


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=True)
    telefone = Column(String, unique=True, index=True, nullable=False)

    agendamentos = relationship("Agendamento", back_populates="cliente")


class Agendamento(Base):
    __tablename__ = "agendamentos"

    id = Column(Integer, primary_key=True, index=True)
    barbearia_id = Column(Integer, ForeignKey("barbearias.id"))
    servico_id = Column(Integer, ForeignKey("servicos.id"))
    cliente_id = Column(Integer, ForeignKey("clientes.id"))

    data_hora_inicio = Column(DateTime, nullable=False)
    data_hora_fim = Column(DateTime, nullable=False)
    status = Column(SqEnum(StatusAgendamento), default=StatusAgendamento.AGENDADO)

    barbearia = relationship("Barbearia", back_populates="agendamentos")
    servico = relationship("Servico", back_populates="agendamentos")
    cliente = relationship("Cliente", back_populates="agendamentos")


class ContextoConversa(Base):
    __tablename__ = "contextos_conversa"

    id = Column(Integer, primary_key=True, index=True)
    telefone_cliente = Column(String, unique=True, index=True)
    barbearia_id = Column(Integer, ForeignKey("barbearias.id"))
    status = Column(SqEnum(StatusConversa), default=StatusConversa.LIVRE)
    dados_temporarios = Column(JSON, default=dict)
    ultimo_update = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
