from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models import StatusAgendamento # para validar o status

# --- BASES ---
# Classes base para evitar repetição de código.
# Contêm os campos comuns entre criar, ler e atualizar.

class ServicoBase(BaseModel):
    nome: str
    preco: Optional[float] = None
    duracao_minutos: int = 30

class BarbeariaBase(BaseModel):
    nome: str
    telefone_whatsapp: str
    horario_abertura: str = "09:00"
    horario_fechamento: str = "18:00"

class ClienteBase(BaseModel):
    nome: Optional[str] = None
    telefone: str

class AgendamentoBase(BaseModel):
    data_hora_inicio: datetime
    data_hora_fim: datetime

# --- CRIAÇÃO (Inputs) ---
# O que a API precisa receber para criar um registro novo.
# Geralmente não pedimos o ID aqui, pois o banco gera automático.

class BarbeariaCreate(BarbeariaBase):
    pass # Igual à base

class ServicoCreate(ServicoBase):
    pass

class ClienteCreate(ClienteBase):
    pass

class AgendamentoCreate(AgendamentoBase):
    # Para agendar, preciso saber quem, onde e o quê.
    barbearia_id: int
    servico_id: int
    cliente_telefone: str # Usamos telefone para achar ou criar o cliente na hora

# --- LEITURA (Outputs/Responses) ---
# O que a API devolve para o frontend/usuário.
# Aqui incluímos o ID e convertemos objetos do banco para JSON.

class ServicoResponse(ServicoBase):
    id: int
    barbearia_id: int

    class Config:
        from_attributes = True # Essencial: permite ler dados direto do SQLAlchemy

class BarbeariaResponse(BarbeariaBase):
    id: int
    servicos: List[ServicoResponse] = [] # Posso devolver os serviços junto!

    class Config:
        from_attributes = True

class ClienteResponse(ClienteBase):
    id: int

    class Config:
        from_attributes = True

class AgendamentoResponse(AgendamentoBase):
    id: int
    status: StatusAgendamento
    # Posso devolver o objeto completo do serviço e cliente aninhado
    servico: Optional[ServicoResponse] = None 
    cliente: Optional[ClienteResponse] = None

    class Config:
        from_attributes = True

# Webhook

class WebhookPayload(BaseModel):
    # Schema simples para validar se o que chega do WhatsApp é JSON válido
    object: str
    entry: list