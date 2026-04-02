import json
import os
from datetime import datetime

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)


def _fallback_resposta() -> dict:
    return {
        "intencao": "OUTROS",
        "dados": {"data": None, "hora": None, "servico": None, "nome_cliente": None},
        "resposta_texto": "Nao consegui processar agora. Pode repetir de forma mais objetiva?",
    }


def analisar_mensagem(texto_usuario: str):
    if not GEMINI_KEY:
        print("GEMINI_API_KEY nao configurada. Usando fallback.")
        return _fallback_resposta()

    agora = datetime.now()
    dia_hoje = agora.strftime("%Y-%m-%d")
    dia_semana = agora.strftime("%A")

    prompt_sistema = f"""
    Voce e a recepcionista virtual inteligente da 'Barbearia do Dev'.

    CONTEXTO TEMPORAL:
    - Hoje e: {dia_hoje} ({dia_semana}).
    - Hora atual: {agora.strftime("%H:%M")}.

    OBJETIVOS:
    1. Classificar a intencao do usuario: AGENDAR, CANCELAR, DUVIDA, OUTROS.
    2. Extrair data ISO (YYYY-MM-DD), hora (HH:MM), servico e nome_cliente.
    3. Gerar resposta curta em portugues do Brasil.

    SERVICOS DISPONIVEIS:
    - Corte de Cabelo
    - Barba
    - Combo (Corte + Barba)

    REGRAS:
    - Retorne estritamente JSON valido.
    - Se nao houver data/hora explicita, use null.

    FORMATO:
    {{
      "intencao": "AGENDAR" | "CANCELAR" | "DUVIDA" | "OUTROS",
      "dados": {{
        "data": "YYYY-MM-DD" ou null,
        "hora": "HH:MM" ou null,
        "servico": "string" ou null,
        "nome_cliente": "string" ou null
      }},
      "resposta_texto": "texto"
    }}

    Mensagem do usuario: "{texto_usuario}"
    """

    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config={"response_mime_type": "application/json"},
    )

    try:
        response = model.generate_content(prompt_sistema)
        resposta = response.text.strip()
        if resposta.startswith("```"):
            resposta = resposta.strip("`")
            resposta = resposta.replace("json", "", 1).strip()
        return json.loads(resposta)
    except Exception as exc:
        print(f"Erro na IA: {exc}")
        return _fallback_resposta()


if __name__ == "__main__":
    msg = "Tem horario para amanha as 15:00 para corte?"
    print(json.dumps(analisar_mensagem(msg), indent=2, ensure_ascii=False))
