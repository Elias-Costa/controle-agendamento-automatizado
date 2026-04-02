from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models import StatusAgendamento


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


class BarbeariaCreate(BarbeariaBase):
    pass


class ServicoCreate(ServicoBase):
    pass


class ClienteCreate(ClienteBase):
    pass


class AgendamentoCreate(AgendamentoBase):
    barbearia_id: int
    servico_id: int
    cliente_telefone: str


class ServicoResponse(ServicoBase):
    id: int
    barbearia_id: int

    model_config = ConfigDict(from_attributes=True)


class BarbeariaResponse(BarbeariaBase):
    id: int
    servicos: List[ServicoResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ClienteResponse(ClienteBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AgendamentoResponse(AgendamentoBase):
    id: int
    status: StatusAgendamento
    servico: Optional[ServicoResponse] = None
    cliente: Optional[ClienteResponse] = None

    model_config = ConfigDict(from_attributes=True)


class WebhookPayload(BaseModel):
    object: str
    entry: list
