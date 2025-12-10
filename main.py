from fastapi import FastAPI
from app.api import router as api_router

app = FastAPI(
    title="Agendador WhatsApp MVP",
    description="API Profissional modularizada",
    version="1.0.0"
)

# inclui todas as rotas definidas em api.py
app.include_router(api_router)

@app.get("/")
def health_check():
    return {"status": "Sistema online e roteado corretamente"}