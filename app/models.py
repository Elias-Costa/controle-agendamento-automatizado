from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Enum as SqEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
import enum
from datetime import datetime

# Importamos a base do ficheiro database.py (que vamos criar a seguir)
from app.database import Base

# --- ENUMS (Para garantir consistência nos dados) ---

class StatusAgendamento(str, enum.Enum):
    AGENDADO = "AGENDADO"
    CANCELADO = "CANCELADO"
    REALIZADO = "REALIZADO"
    NO_SHOW = "NO_SHOW" # Cliente não apareceu

class StatusConversa(str, enum.Enum):
    LIVRE = "LIVRE"
    AGUARDANDO_DATA = "AGUARDANDO_DATA"
    AGUARDANDO_HORARIO = "AGUARDANDO_HORARIO"
    AGUARDANDO_CONFIRMACAO = "AGUARDANDO_CONFIRMACAO"
    ATENDIMENTO_HUMANO = "ATENDIMENTO_HUMANO"

# --- TABELAS ---

class Barbearia(Base):
    __tablename__ = "barbearias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    telefone_whatsapp = Column(String, unique=True, index=True, nullable=False)
    timezone = Column(String, default="America/Sao_Paulo")
    
    # Horários simples (ex: "09:00", "18:00")
    horario_abertura = Column(String, default="09:00")
    horario_fechamento = Column(String, default="18:00")
    
    # Relações: Uma barbearia tem muitos serviços e agendamentos
    servicos = relationship("Servico", back_populates="barbearia")
    agendamentos = relationship("Agendamento", back_populates="barbearia")

class Servico(Base):
    __tablename__ = "servicos"

    id = Column(Integer, primary_key=True, index=True)
    barbearia_id = Column(Integer, ForeignKey("barbearias.id"))
    
    nome = Column(String, nullable=False) # Ex: "Corte na Tesoura"
    preco = Column(Float, nullable=True)  # Ex: 50.00
    duracao_minutos = Column(Integer, default=30) # Ex: 30
    
    # Relação de volta
    barbearia = relationship("Barbearia", back_populates="servicos")
    agendamentos = relationship("Agendamento", back_populates="servico")

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=True) # Pode começar vazio até ele dizer o nome
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
    
    # Relações para facilitar queries (ex: agendamento.cliente.nome)
    barbearia = relationship("Barbearia", back_populates="agendamentos")
    servico = relationship("Servico", back_populates="agendamentos")
    cliente = relationship("Cliente", back_populates="agendamentos")

class ContextoConversa(Base):
    """
    Tabela para a IA saber onde parou com cada cliente.
    """
    __tablename__ = "contextos_conversa"

    id = Column(Integer, primary_key=True, index=True)
    telefone_cliente = Column(String, unique=True, index=True) # Um contexto por telefone
    barbearia_id = Column(Integer, ForeignKey("barbearias.id")) # Com quem ele está falando?
    
    status = Column(SqEnum(StatusConversa), default=StatusConversa.LIVRE)
    
    # Aqui guardamos o rascunho: {"data_rascunho": "2023-10-10", "servico_rascunho": 1}
    dados_temporarios = Column(JSON, default={}) 
    
    ultimo_update = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)