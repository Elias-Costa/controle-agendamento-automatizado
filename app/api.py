import os
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request

from app import ai_agent, schemas, services, whatsapp_client
from app.database import SessionLocal

router = APIRouter()

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "testetoken123")
DEFAULT_BARBEARIA_ID = int(os.getenv("DEFAULT_BARBEARIA_ID", "1"))
DEFAULT_SERVICO_ID = int(os.getenv("DEFAULT_SERVICO_ID", "1"))


def _extrair_mensagem_texto(payload: dict) -> tuple[str, str] | tuple[None, None]:
    entry = payload.get("entry", [{}])[0]
    changes = entry.get("changes", [{}])[0]
    value = changes.get("value", {})

    if "messages" not in value:
        status = value.get("statuses", [{}])[0]
        status_type = status.get("status")
        if status_type:
            print(f"Atualizacao de status: {status_type.upper()}")
            if status_type == "failed":
                print(f"Motivo da falha: {status.get('errors', [])}")
        return None, None

    message = value["messages"][0]
    if message.get("type") != "text":
        return None, None

    telefone_cliente = message.get("from")
    texto_usuario = message.get("text", {}).get("body")
    if not telefone_cliente or not texto_usuario:
        return None, None

    return telefone_cliente, texto_usuario


def processar_mensagem_whatsapp(payload: dict) -> None:
    db = SessionLocal()
    try:
        telefone_cliente, texto_usuario = _extrair_mensagem_texto(payload)
        if not telefone_cliente or not texto_usuario:
            return

        print(f"Mensagem de {telefone_cliente}: {texto_usuario}")

        analise_ia = ai_agent.analisar_mensagem(texto_usuario)
        intencao = analise_ia.get("intencao")
        dados = analise_ia.get("dados", {})
        resposta_final = analise_ia.get("resposta_texto") or "Entendi. Pode me passar mais detalhes?"

        if intencao == "AGENDAR" and dados.get("data") and dados.get("hora"):
            try:
                inicio = datetime.fromisoformat(f"{dados['data']}T{dados['hora']}:00")
                novo_agendamento = schemas.AgendamentoCreate(
                    barbearia_id=DEFAULT_BARBEARIA_ID,
                    servico_id=DEFAULT_SERVICO_ID,
                    cliente_telefone=telefone_cliente,
                    data_hora_inicio=inicio,
                    data_hora_fim=inicio,
                )
                services.criar_agendamento(db, novo_agendamento)
                resposta_final = f"Agendado com sucesso! Te espero dia {dados['data']} as {dados['hora']}."
            except HTTPException as exc:
                resposta_final = f"Ops! {exc.detail}. Tente outro horario."
            except ValueError:
                resposta_final = "Nao consegui entender data/hora. Pode enviar no formato DD/MM as HH:MM?"
            except Exception as exc:
                print(f"Erro generico ao agendar: {exc}")
                resposta_final = "Tive um erro interno ao tentar salvar seu horario."

        whatsapp_client.enviar_mensagem(telefone_cliente, resposta_final)

    except Exception as exc:
        print(f"Erro fatal no processamento: {exc}")
    finally:
        db.close()


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Token invalido")


@router.post("/webhook")
async def webhook_whatsapp(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    background_tasks.add_task(processar_mensagem_whatsapp, payload)
    return {"status": "recebido"}
