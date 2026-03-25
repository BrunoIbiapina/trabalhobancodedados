"""
WhatsApp Bot — DataChat powered by Claude
Recebe mensagens via WhatsApp Business API e responde com Claude.
"""

import os, json, hmac, hashlib
from flask import Flask, request, jsonify
import requests
import anthropic

# ── Configuração ──────────────────────────────────────────────────────────────
WHATSAPP_TOKEN = "EAAR9govZAizQBRASpXZBtiZAI7zB9wqIruz1fwkdlswCG5ElvfjIAXJ2RZAZAosROyJAbsnhKDfC7ZCy4DR7KubGEvdTxey0soOXJzcWMRBQYRhURWaNlJYYBZCwqyXJL8uZBaZBbNEgkr2oLPcwY4kQCZCFRunLBaXRpFCrsr468FTi0RjqN9nIKje0xjiEZAGU80mjDL6vIf1P39uJwhyJxRadUGpfyTZCEw4thygSpmjxPM4MgIlQ4PKOJs2ZBUbtZAEUvkPYc5gr3nczbdZCjViCQZBOtc2zsQZDZD"
PHONE_NUMBER_ID = "1046453415218930"
VERIFY_TOKEN = "datachat_verify_2024"  # Você escolhe — usa na config do webhook

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY")

# ── Clientes ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
claude = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

# Histórico por número (em memória — reseta quando reinicia o servidor)
conversations = {}

SYSTEM_PROMPT = """Você é o DataChat, um assistente de análise de dados no WhatsApp.
Responda sempre em Português do Brasil, de forma concisa e natural.

Você é conversacional — como um colega de trabalho inteligente.
- Cumprimentos → responda naturalmente
- Perguntas sobre capacidades → explique o que pode fazer
- Mantenha respostas curtas (WhatsApp não é lugar de texto longo)
- Use *negrito* e _itálico_ no estilo WhatsApp (não markdown)
- Limite respostas a ~300 palavras no máximo
- Não use emojis em excesso

Você pode ajudar com:
- Análise de dados e estatísticas
- Explicar conceitos de dados/BI
- Sugestões de visualizações
- Dicas de SQL, Python, pandas
- Interpretação de resultados

Nota: No WhatsApp você não tem acesso a datasets — apenas conversa e orienta."""


def send_whatsapp_message(to: str, text: str):
    """Envia mensagem de texto pelo WhatsApp Business API."""
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code == 200:
        print(f"[OK] Mensagem enviada pra {to}")
    else:
        print(f"[ERRO] WhatsApp API: {resp.status_code} — {resp.text}")
    return resp


def get_claude_response(phone: str, user_msg: str) -> str:
    """Envia mensagem pro Claude e retorna a resposta."""
    # Pega ou cria histórico
    if phone not in conversations:
        conversations[phone] = []

    history = conversations[phone]
    history.append({"role": "user", "content": user_msg})

    # Mantém só últimas 20 mensagens pra não estourar contexto
    if len(history) > 20:
        history = history[-20:]
        conversations[phone] = history

    try:
        response = claude.messages.create(
            model="claude-sonnet-4-6",  # Sonnet é mais rápido e barato pro WhatsApp
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history,
        )
        assistant_msg = response.content[0].text
        history.append({"role": "assistant", "content": assistant_msg})
        return assistant_msg

    except Exception as e:
        print(f"[ERRO] Claude API: {e}")
        return "Desculpa, tive um problema técnico. Tenta de novo em alguns segundos."


# ── Webhook: Verificação (GET) ────────────────────────────────────────────────
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Meta envia GET pra verificar o webhook."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("[OK] Webhook verificado!")
        return challenge, 200
    else:
        print("[ERRO] Token de verificação inválido")
        return "Forbidden", 403


# ── Webhook: Mensagens (POST) ─────────────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def receive_message():
    """Recebe mensagens do WhatsApp."""
    data = request.get_json()

    if not data:
        return jsonify({"status": "no data"}), 200

    try:
        # Navega na estrutura do webhook da Meta
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        for msg in messages:
            if msg.get("type") == "text":
                phone = msg["from"]          # Número de quem mandou
                text = msg["text"]["body"]   # Texto da mensagem
                msg_id = msg["id"]

                print(f"[MSG] {phone}: {text}")

                # Marca como lida
                requests.post(
                    f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages",
                    headers={
                        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "messaging_product": "whatsapp",
                        "status": "read",
                        "message_id": msg_id,
                    },
                )

                # Gera resposta com Claude
                response = get_claude_response(phone, text)

                # Envia resposta
                send_whatsapp_message(phone, response)
                print(f"[RESP] {phone}: {response[:100]}...")

    except Exception as e:
        print(f"[ERRO] Processamento: {e}")

    return jsonify({"status": "ok"}), 200


# ── Health check ──────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "DataChat WhatsApp Bot rodando!", "version": "1.0"}), 200


if __name__ == "__main__":
    print("=" * 50)
    print("  DataChat WhatsApp Bot")
    print("  Servidor rodando na porta 5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)
