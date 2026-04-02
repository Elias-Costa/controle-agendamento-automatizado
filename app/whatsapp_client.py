import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERSION = os.getenv("WHATSAPP_GRAPH_VERSION", "v21.0")


def enviar_mensagem(destinatario: str, texto: str):
    if not API_TOKEN or not PHONE_ID:
        print("WHATSAPP_TOKEN/WHATSAPP_PHONE_ID nao configurados. Mensagem nao enviada.")
        return None

    url = f"https://graph.facebook.com/{VERSION}/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": destinatario,
        "type": "text",
        "text": {"body": texto},
    }

    response = None
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        print(f"Erro ao enviar WhatsApp: {exc}")
        if response is not None:
            print(f"Detalhe do erro: {response.text}")
        return None
