import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Configurações carregadas do .env
API_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERSION = "v21.0" # Versão atual da Graph API

def enviar_mensagem(destinatario: str, texto: str):
    """
    Envia uma mensagem de texto simples para o WhatsApp do usuário.
    """
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": destinatario,
        "type": "text",
        "text": {"body": texto}
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # Levanta erro se não for 200 OK
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar WhatsApp: {e}")
        if response is not None:
            print(f"Detalhe do erro: {response.text}")
        return None