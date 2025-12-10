from fastapi import APIRouter

router = APIRouter()

@router.get("/teste-rota")
def teste_rota():
    return {"message": "ok"}

@router.post("/webhook")
async def webhook_whatsapp(payload: dict):
    """
    Esta rota será chamada pelo WhatsApp.
    """
    print(f"Payload recebido: {payload}")
    return {"status": "recebido"}