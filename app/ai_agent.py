import google.generativeai as genai
import os
import json
from datetime import datetime
import locale
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para a memória
load_dotenv()

# Tenta configurar para português, se falhar usa padrão
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    pass

# Configuração da API do Google
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise ValueError("ERRO: A variável GEMINI_API_KEY não foi encontrada no .env")

genai.configure(api_key=GEMINI_KEY)

def analisar_mensagem(texto_usuario: str):
    """
    Usa o Gemini 2.5 Flash para ler a mensagem, entender a intenção
    e extrair dados (data, hora, serviço) em formato JSON.
    """
    
    # 1. Pegamos o momento exato de AGORA para a IA entender "hoje", "amanhã", "sexta"
    agora = datetime.now()
    dia_hoje = agora.strftime("%Y-%m-%d")
    dia_semana = agora.strftime("%A") # Ex: "quarta-feira"
    
    # 2. O Prompt do Sistema
    prompt_sistema = f"""
    Você é a recepcionista virtual inteligente da 'Barbearia do Dev'.
    
    CONTEXTO TEMPORAL (IMPORTANTE):
    - Hoje é: {dia_hoje} ({dia_semana}).
    - Hora atual: {agora.strftime("%H:%M")}.
    - Considere este contexto para calcular datas relativas como "amanhã", "depois de amanhã", "sexta-feira".

    SEUS OBJETIVOS:
    1. Classificar a intenção do usuário: AGENDAR, CANCELAR, DUVIDA, OUTROS.
    2. Extrair dados de agendamento se houver (data no formato ISO YYYY-MM-DD, hora HH:MM).
    3. Identificar o serviço desejado (ex: Corte, Barba, Sobrancelha).
    4. Gerar uma resposta curta, simpática e natural em português do Brasil.

    SERVIÇOS DISPONÍVEIS:
    - Corte de Cabelo
    - Barba
    - Combo (Corte + Barba)
    
    REGRAS DE RESPOSTA:
    - Responda ESTRITAMENTE um JSON válido.
    - Se a data não for citada, retorne null.
    - Se a hora não for citada, retorne null.
    - Na resposta_texto, seja breve (estilo WhatsApp). Se faltar data/hora, pergunte.

    FORMATO JSON ESPERADO:
    {{
        "intencao": "AGENDAR" | "CANCELAR" | "DUVIDA" | "OUTROS",
        "dados": {{
            "data": "YYYY-MM-DD" ou null,
            "hora": "HH:MM" ou null,
            "servico": "string" ou null,
            "nome_cliente": "string" ou null
        }},
        "resposta_texto": "Sua resposta amigável aqui"
    }}
    
    MENSAGEM DO USUÁRIO:
    "{texto_usuario}"
    """

    # 3. Chamada ao Modelo (Usando JSON Mode para garantir estrutura)
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )

    try:
        response = model.generate_content(prompt_sistema)
        # O Gemini devolve o JSON em texto, fazemos o parse para Dicionário Python
        return json.loads(response.text)
    except Exception as e:
        # Fallback de segurança caso a IA falhe
        print(f"Erro na IA: {e}")
        return {
            "intencao": "OUTROS",
            "dados": {},
            "resposta_texto": "Desculpe, tive um erro técnico. Pode repetir?"
        }

# --- TESTE RÁPIDO
if __name__ == "__main__":
    # Simulação
    msg = "E aí, tem horário pra cortar o cabelo amanhã às 3 da tarde?"
    print(f"Usuario: {msg}")
    resultado = analisar_mensagem(msg)
    print("IA Respondeu:", json.dumps(resultado, indent=2, ensure_ascii=False))