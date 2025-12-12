# 💈 AI Scheduler - Agendamento Inteligente via WhatsApp

![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Moderno-green)
![AI](https://img.shields.io/badge/AI-Gemini_Flash-orange)

Um sistema SaaS de agendamento automático para barbearias e clínicas que utiliza **Inteligência Artificial Generativa (LLM)** para conversar naturalmente com clientes via WhatsApp, interpretando intenções e gerenciando horários em tempo real.

## 🚀 Funcionalidades

- **Processamento de Linguagem Natural (NLP):** O sistema entende mensagens informais como *"Quero marcar um corte para amanhã à tarde"* e extrai data/hora automaticamente usando o **Google Gemini 2.5 Flash**.
- **Gestão de Conflitos:** Algoritmo de slotting que verifica a disponibilidade real de horários, considerando a duração variável de cada serviço (ex: Corte demora 30min, Barba 15min).
- **Integração WhatsApp:** Webhook em tempo real usando a API oficial da Meta (WhatsApp Cloud API).
- **Backend Assimétrico:** Utiliza `BackgroundTasks` do FastAPI para processar a inteligência artificial em segundo plano, garantindo resposta imediata (200 OK) ao servidor do WhatsApp.
- **Persistência Robusta:** Banco de dados Relacional (PostgreSQL) para garantir integridade dos agendamentos.

## 🛠️ Stack Tecnológica

- **Linguagem:** Python 3.10+
- **Framework Web:** FastAPI + Uvicorn
- **Banco de Dados:** PostgreSQL (via Supabase)
- **ORM:** SQLAlchemy
- **IA/LLM:** Google Gemini 2.5 Flash (via JSON Mode)
- **Integração:** WhatsApp Business Cloud API
- **Validação de Dados:** Pydantic
- **Ferramentas de Dev:** Ngrok (Tunneling)

## 🧠 Arquitetura da Solução

O sistema opera em um fluxo de 4 etapas:
1. **Webhook:** O FastAPI recebe o payload do WhatsApp e valida a segurança.
2. **AI Agent:** Analisa a mensagem do usuário, injeta o contexto temporal (data de hoje) e extrai a intenção (AGENDAR, CANCELAR, DUVIDA).
3. **Service Layer:** Verifica as regras de negócio no banco de dados (horário de funcionamento, colisões de agenda).
4. **Response:** Executa a ação (cria o agendamento ou retorna erro) e envia a resposta final ao usuário via API da Meta.

## 📦 Como Rodar Localmente

### Pré-requisitos
- Python 3.10 ou superior
- Conta no Google AI Studio (para chave da API Gemini)
- Conta na Meta for Developers (para API do WhatsApp)
- Conta no Supabase (ou Postgres local)

### Passo a Passo

1. **Clone o repositório**

2. **Crie e ative o ambiente virtual:**
   ```
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate

3. **Instale as dependências:**
    ```
    pip install -r requirements.txt

4. **Configure as Variáveis de Ambiente: Crie um arquivo .env na raiz do projeto e preencha conforme o examplo abaixo:**
    ```
    DATABASE_URL="postgresql://usuario:senha@host:5432/db"
    GEMINI_API_KEY="SuaChaveAqui"
    WHATSAPP_TOKEN="SeuTokenMeta"
    WHATSAPP_PHONE_ID="SeuPhoneID"

5. **Inicialize o Banco de Dados: Execute o script para criar as tabelas e popular com dados de teste:**
    ```
    python create_db.py
    python seed.py

6. **Execute o servidor:**
   ```
   uvicorn main:app --reload


## Próximos passos

- [ ] Implementar sistema de lembretes automáticos (Cron Jobs).

- [ ] Criar Dashboard Web para o dono da barbearia visualizar a agenda.

- [ ] Suporte a multitenancy (múltiplas barbearias no mesmo sistema).

- [ ] Deploy em produção (Railway/Render).