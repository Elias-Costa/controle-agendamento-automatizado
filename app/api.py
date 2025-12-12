from fastapi import APIRouter, Depends, HTTPException, Query, Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app import services, schemas, ai_agent, whatsapp_client
import json

router = APIRouter()

# --- AUXILIAR: PROCESSAMENTO ASSÍNCRONO ---
# Usamos BackgroundTasks para responder "200 OK" rápido pro WhatsApp (evita timeout)
# e processar a inteligência depois.

def processar_mensagem_whatsapp(payload: dict, db: Session):
    """
    Função principal que orquestra: Receber -> Pensar -> Agir -> Responder
    """
    try:
        # 1. Extrair dados básicos da mensagem (Lógica de Parse do JSON da Meta)
        entry = payload['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        
        if 'messages' not in value:
            if 'statuses' in value:
                status = value['statuses'][0]
                status_type = status['status']
                print(f"Atualização de Status: {status_type.upper()}")
                
                # Se falhou, mostra o motivo
                if status_type == 'failed':
                    errors = status.get('errors', [])
                    print(f"Motivo da falha: {errors}")
            return

        message = value['messages'][0]
        telefone_cliente = message['from'] # Ex: 551199999999
        texto_usuario = message['text']['body']
        
        print(f"Mensagem de {telefone_cliente}: {texto_usuario}")

        # 2. Inteligência Artificial (AI Agent)
        analise_ia = ai_agent.analisar_mensagem(texto_usuario)
        intencao = analise_ia.get("intencao")
        dados = analise_ia.get("dados", {})
        resposta_final = analise_ia.get("resposta_texto")

        # 3. Lógica de Negócio (Services)
        # Se a IA detectou intenção de AGENDAR e temos data/hora, tentamos efetivar.
        if intencao == "AGENDAR" and dados.get("data") and dados.get("hora"):
            try:
                # Busca IDs (Hardcoded para 1 no MVP, mas viria do contexto em produção)
                barbearia_id = 1 
                # Tenta achar o serviço pelo nome que a IA extraiu (ex: "Corte")
                # Aqui simplificamos usando ID 1 se não achar, para o teste funcionar
                servico_id = 1 
                
                # Monta objeto para criar
                novo_agendamento = schemas.AgendamentoCreate(
                    barbearia_id=barbearia_id,
                    servico_id=servico_id,
                    cliente_telefone=telefone_cliente,
                    data_hora_inicio=f"{dados['data']}T{dados['hora']}:00",
                    data_hora_fim=f"{dados['data']}T{dados['hora']}:00" # O service corrige isso
                )
                
                agendamento = services.criar_agendamento(db, novo_agendamento)
                
                # Se deu certo, sobrescreve a resposta da IA com a confirmação oficial
                resposta_final = f"Agendado com sucesso! Te espero dia {dados['data']} às {dados['hora']}."
            
            except HTTPException as e:
                # Se o horário estiver ocupado (Erro 409), avisa o usuário
                resposta_final = f"Ops! {e.detail}. Tente outro horário."
            except Exception as e:
                print(f"Erro genérico ao agendar: {e}")
                resposta_final = "Tive um erro interno ao tentar salvar seu horário."

        # 4. Enviar Resposta no WhatsApp
        whatsapp_client.enviar_mensagem(telefone_cliente, resposta_final)

    except Exception as e:
        print(f"Erro fatal no processamento: {e}")

# --- ROTAS ---

@router.get("/webhook")
async def verify_webhook(hub_mode: str = Query(alias="hub.mode"), 
                         hub_challenge: str = Query(alias="hub.challenge"), 
                         hub_verify_token: str = Query(alias="hub.verify_token")):
    VERIFY_TOKEN = "testetoken123" 
    if hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Token inválido")

@router.post("/webhook")
async def webhook_whatsapp(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Recebe o JSON, responde 200 OK imediatamente e manda processar em segundo plano.
    """
    payload = await request.json()
    
    # Joga o processamento pesado para background para não travar o WhatsApp
    background_tasks.add_task(processar_mensagem_whatsapp, payload, db)
    
    return {"status": "recebido"}