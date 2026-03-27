"""
WhatsApp Bot — DataChat powered by Claude (via Twilio)
Com acesso a CSV, gráficos como imagem, e análise de dados completa.
"""

import os, json, io, tempfile, glob, threading, time
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask import Flask, request
from twilio.rest import Client as TwilioClient
from twilio.twiml.messaging_response import MessagingResponse
import ollama
import requests as req
from dotenv import load_dotenv
load_dotenv()

# ── Configuração ─────────────────────────────────────────────────────────────
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP    = os.environ.get("TWILIO_WHATSAPP", "whatsapp:+14155238886")

MODEL    = "qwen2.5:7b"   # modelo local Ollama
DATA_DIR = os.path.expanduser("~/Downloads/TrabalhoBD")
NGROK_URL = None  # Preenchido automaticamente

# ── Clientes ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Estado por número
conversations = {}
user_data = {}  # phone -> DataFrame

# ── Carregar CSV automaticamente ─────────────────────────────────────────────
def load_default_csv():
    """Carrega o sample.csv como dataset padrão."""
    path = os.path.join(DATA_DIR, "sample.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    # Tenta qualquer CSV na pasta
    csvs = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    csvs = [c for c in csvs if ".venv" not in c]
    if csvs:
        return pd.read_csv(csvs[0])
    return None

DEFAULT_DF = load_default_csv()
if DEFAULT_DF is not None:
    print(f"[CSV] Dataset carregado: {DEFAULT_DF.shape[0]} linhas x {DEFAULT_DF.shape[1]} colunas")
else:
    print("[CSV] Nenhum dataset encontrado")


def get_df(phone):
    """Retorna o DataFrame do usuário ou o padrão."""
    if phone in user_data:
        return user_data[phone]
    return DEFAULT_DF


# ══════════════════════════════════════════════════════════════════════════════
# TOOLS (mesmas do Streamlit, adaptadas pro WhatsApp)
# ══════════════════════════════════════════════════════════════════════════════
def get_data_info(phone, sample_rows=5):
    d = get_df(phone)
    if d is None: return "Nenhum dataset carregado."
    num = d.select_dtypes(include=np.number).columns.tolist()
    cat = d.select_dtypes(include=["object","bool"]).columns.tolist()
    info = {
        "shape": {"rows": len(d), "columns": len(d.columns)},
        "columns": {
            col: {
                "dtype": str(d[col].dtype),
                "nulls": int(d[col].isnull().sum()),
                "unique": int(d[col].nunique()),
                "top5": d[col].value_counts().head(5).to_dict() if col in cat else None,
                "min":  float(d[col].min())  if col in num else None,
                "max":  float(d[col].max())  if col in num else None,
                "mean": float(d[col].mean()) if col in num else None,
            } for col in d.columns
        },
        "sample": d.sample(min(sample_rows, len(d)), random_state=42).to_dict(orient="records"),
    }
    return json.dumps(info, ensure_ascii=False, default=str, indent=2)


def run_query(phone, code):
    d = get_df(phone)
    if d is None: return "Nenhum dataset carregado."
    try:
        ns, local = {"df": d.copy(), "pd": pd, "np": np}, {}
        exec(f"_r=({code})", ns, local)
        r = local["_r"]
        if isinstance(r, pd.DataFrame): return f"DataFrame {r.shape}:\n{r.head(20).to_string()}"
        if isinstance(r, pd.Series):    return f"Series ({len(r)}):\n{r.head(20).to_string()}"
        return str(r)[:3000]
    except Exception as e:
        return f"Erro: {type(e).__name__}: {e}"


def create_chart(phone, chart_type, x_col=None, y_col=None, z_col=None, color_col=None, title=None, aggregation="mean"):
    d = get_df(phone)
    if d is None: return None, "Nenhum dataset carregado."
    title = title or f"{chart_type} — {x_col or ''}"
    ct = chart_type.lower().strip()
    num = d.select_dtypes(include=np.number).columns.tolist()
    cat = d.select_dtypes(include=["object","bool"]).columns.tolist()
    TEMPLATE = "plotly_white"
    COLORS = px.colors.qualitative.Set2

    try:
        fig = None
        if ct in ("histogram","histograma"):
            col = x_col or (num[0] if num else d.columns[0])
            fig = px.histogram(d, x=col, color=color_col, title=title, nbins=35,
                               template=TEMPLATE, color_discrete_sequence=COLORS)

        elif ct in ("scatter","dispersão","dispersao"):
            x = x_col or (num[0] if num else d.columns[0])
            y = y_col or (num[1] if len(num)>1 else num[0])
            fig = px.scatter(d, x=x, y=y, color=color_col, title=title,
                             template=TEMPLATE, opacity=0.65, color_discrete_sequence=COLORS)

        elif ct in ("scatter3d","scatter_3d","dispersao3d","3d_scatter"):
            x = x_col or (num[0] if num else d.columns[0])
            y = y_col or (num[1] if len(num)>1 else num[0])
            z = z_col or (num[2] if len(num)>2 else num[0])
            fig = px.scatter_3d(d, x=x, y=y, z=z, color=color_col or (cat[0] if cat else None),
                                title=title, template=TEMPLATE, opacity=0.75,
                                color_discrete_sequence=COLORS)

        elif ct in ("surface","surface3d","superficie","3d_surface"):
            x = x_col or (num[0] if num else d.columns[0])
            y = y_col or (num[1] if len(num)>1 else num[0])
            z = z_col or (num[2] if len(num)>2 else num[0])
            pivot = d.pivot_table(values=z, index=y, columns=x, aggfunc="mean")
            fig = go.Figure(data=[go.Surface(z=pivot.values, x=pivot.columns, y=pivot.index, colorscale="Viridis")])
            fig.update_layout(title=title, scene=dict(xaxis_title=x, yaxis_title=y, zaxis_title=z))

        elif ct in ("bar","barras","barra"):
            agg = aggregation if aggregation in ["mean","sum","count","max","min"] else "mean"
            if x_col and y_col:
                data = d.groupby(x_col)[y_col].agg(agg).reset_index()
                fig = px.bar(data.sort_values(y_col, ascending=False), x=x_col, y=y_col, title=title,
                             color=color_col or x_col, template=TEMPLATE, color_discrete_sequence=COLORS)
            elif x_col:
                counts = d[x_col].value_counts().reset_index()
                counts.columns = [x_col, "contagem"]
                fig = px.bar(counts, x=x_col, y="contagem", title=title,
                             color=x_col, template=TEMPLATE, color_discrete_sequence=COLORS)

        elif ct in ("box","boxplot"):
            col = y_col or (num[0] if num else d.columns[0])
            fig = px.box(d, x=color_col or x_col, y=col, title=title, template=TEMPLATE)

        elif ct in ("heatmap","correlação","correlacao"):
            corr = d[num].corr().round(3)
            fig = px.imshow(corr, title=title, template=TEMPLATE, color_continuous_scale="RdBu_r", text_auto=True)

        elif ct in ("pie","pizza"):
            col = x_col or (cat[0] if cat else d.columns[0])
            counts = d[col].value_counts()
            fig = px.pie(values=counts.values, names=counts.index, title=title,
                         template=TEMPLATE, hole=0.38, color_discrete_sequence=COLORS)

        elif ct in ("line","linha"):
            x = x_col or d.columns[0]
            y = y_col or (num[0] if num else d.columns[1])
            fig = px.line(d.sort_values(x), x=x, y=y, color=color_col, title=title,
                          template=TEMPLATE, markers=True, color_discrete_sequence=COLORS)
        else:
            return None, f"Tipo '{chart_type}' não reconhecido."

        if fig:
            fig.update_layout(height=500, width=800, font=dict(size=13),
                              margin=dict(l=50, r=30, t=60, b=50))
            # Salva como PNG
            img_path = os.path.join(tempfile.gettempdir(), f"chart_{abs(hash(title))}_{os.getpid()}.png")
            try:
                fig.write_image(img_path, scale=2, engine="kaleido")
            except Exception as img_err:
                print(f"[WARN] Kaleido falhou: {img_err}, tentando sem scale...")
                try:
                    fig.write_image(img_path)
                except Exception as img_err2:
                    print(f"[ERRO] write_image falhou: {img_err2}")
                    return None, f"Gráfico criado mas não consegui gerar a imagem: {img_err2}"
            return img_path, f"Gráfico '{title}' gerado."

    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"Erro ao criar gráfico: {e}"

    return None, "Não foi possível criar o gráfico."


def detect_anomalies(phone, column, method="iqr"):
    d = get_df(phone)
    if d is None: return None, "Nenhum dataset carregado."
    if column not in d.columns: return None, f"Coluna '{column}' não encontrada."

    s = d[column].dropna()
    if method == "zscore":
        z = np.abs((s - s.mean()) / s.std())
        mask = z > 3
        threshold_info = f"Z-score > 3σ"
    else:
        Q1, Q3 = s.quantile(0.25), s.quantile(0.75)
        IQR = Q3 - Q1
        lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        mask = (s < lower) | (s > upper)
        threshold_info = f"IQR: [{lower:.2f}, {upper:.2f}]"

    full_mask = mask.reindex(d.index, fill_value=False)
    anomalies = d[full_mask]
    normal = d[~full_mask]
    n_anom = len(anomalies)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=normal.index, y=normal[column], mode="markers", name="Normal",
                             marker=dict(color="#6b9bd2", size=5, opacity=0.55)))
    if n_anom > 0:
        fig.add_trace(go.Scatter(x=anomalies.index, y=anomalies[column], mode="markers", name="Anomalia",
                                 marker=dict(color="#e05c5c", size=9, symbol="x", line=dict(width=2, color="#c93030"))))
        top = anomalies.nlargest(min(5, n_anom), column)
        for idx, row in top.iterrows():
            fig.add_annotation(x=idx, y=row[column], text=f"{row[column]:.1f}",
                               showarrow=True, arrowhead=2, arrowcolor="#c93030",
                               font=dict(size=10, color="#c93030"), bgcolor="white",
                               bordercolor="#e05c5c", borderwidth=1, ax=0, ay=-36)

    fig.update_layout(title=f"Anomalias — '{column}' ({method.upper()}) · {n_anom} detectadas",
                      height=500, width=800, font=dict(size=13),
                      margin=dict(l=50, r=30, t=60, b=50))

    img_path = os.path.join(tempfile.gettempdir(), f"anomaly_{column}_{os.getpid()}.png")
    try:
        fig.write_image(img_path, scale=2, engine="kaleido")
    except Exception:
        try:
            fig.write_image(img_path)
        except Exception as e:
            print(f"[ERRO] write_image anomalias: {e}")
            img_path = None

    result = {
        "column": column, "method": method, "threshold": threshold_info,
        "n_anomalies": n_anom, "pct": round(n_anom / len(d) * 100, 2),
    }
    return img_path, json.dumps(result, ensure_ascii=False, default=str)


# ── Tools definition ─────────────────────────────────────────────────────────
TOOLS_OLLAMA = [
    {"type":"function","function":{"name":"get_data_info","description":"Obtém shape, colunas, tipos, estatísticas e amostra do dataset carregado.","parameters":{"type":"object","properties":{"sample_rows":{"type":"integer","default":5}}}}},
    {"type":"function","function":{"name":"run_query","description":"Executa expressão pandas no DataFrame 'df'. Ex: df.groupby('col')['val'].mean()","parameters":{"type":"object","properties":{"code":{"type":"string"}},"required":["code"]}}},
    {"type":"function","function":{"name":"create_chart","description":"Cria gráfico e envia como imagem. Tipos: histogram, scatter, scatter3d, surface3d, bar, box, heatmap, pie, line","parameters":{"type":"object","properties":{"chart_type":{"type":"string"},"x_col":{"type":"string"},"y_col":{"type":"string"},"z_col":{"type":"string"},"color_col":{"type":"string"},"title":{"type":"string"},"aggregation":{"type":"string","default":"mean"}},"required":["chart_type"]}}},
    {"type":"function","function":{"name":"detect_anomalies","description":"Detecta anomalias em coluna numérica e gera gráfico com outliers destacados.","parameters":{"type":"object","properties":{"column":{"type":"string"},"method":{"type":"string","enum":["iqr","zscore"],"default":"iqr"}},"required":["column"]}}},
]

SYSTEM_PROMPT = """Você é o DataChat, um assistente de análise de dados no WhatsApp.
Responda em Português do Brasil, de forma concisa e natural.

Você é conversacional — converse antes de executar.
- Se o usuário pedir algo vago ("faz um gráfico", "analisa"), PERGUNTE detalhes primeiro
- Se o pedido for claro e específico, execute direto
- Cumprimentos → responda naturalmente, sem executar tools
- Mantenha respostas curtas (max ~200 palavras no WhatsApp)
- Use *negrito* e _itálico_ no estilo WhatsApp

Você tem um dataset de tráfego de rede/cybersegurança carregado com colunas como:
Source Port, Destination Port, Protocol, Packet Length, Packet Type, Traffic Type,
Attack Type, Anomaly Scores, Severity Level, Action Taken, etc.

Tools disponíveis:
- *get_data_info*: ver info do dataset
- *run_query*: executar pandas no DataFrame
- *create_chart*: gerar gráficos (histogram, scatter, scatter3d, surface3d, bar, box, heatmap, pie, line)
- *detect_anomalies*: detectar outliers com gráfico

Gráficos são enviados como imagem PNG no WhatsApp."""


def run_agent(phone, user_msg):
    """Executa o loop agentic com tool use via Ollama."""
    if phone not in conversations:
        conversations[phone] = []

    history = conversations[phone]

    # Limita histórico a 20 mensagens
    if len(history) > 20:
        history = history[-20:]
        conversations[phone] = history

    # Monta mensagens com system prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [m for m in history if m["role"] != "system"]
    messages.append({"role": "user", "content": user_msg})

    images = []

    try:
        for _ in range(5):  # Max 5 iterações
            resp = ollama.chat(
                model=MODEL,
                messages=messages,
                tools=TOOLS_OLLAMA,
                stream=False,
            )

            msg = resp.message

            # Adiciona resposta ao histórico
            assistant_entry = {"role": "assistant", "content": msg.content or ""}
            if msg.tool_calls:
                assistant_entry["tool_calls"] = msg.tool_calls
            messages.append(assistant_entry)

            # Sem tool calls → resposta final
            if not msg.tool_calls:
                final_text = msg.content or ""
                # Salva histórico sem system
                conversations[phone] = [m for m in messages if m["role"] != "system"]
                return final_text, images

            # Executa cada tool
            for tc in msg.tool_calls:
                name = tc.function.name
                args = tc.function.arguments if isinstance(tc.function.arguments, dict) else {}
                print(f"[TOOL] {name}({json.dumps(args, ensure_ascii=False)[:100]})")

                if name == "get_data_info":
                    result = get_data_info(phone, args.get("sample_rows", 5))

                elif name == "run_query":
                    result = run_query(phone, args.get("code", ""))

                elif name == "create_chart":
                    img_path, result = create_chart(
                        phone, args.get("chart_type", "bar"),
                        args.get("x_col"), args.get("y_col"), args.get("z_col"),
                        args.get("color_col"), args.get("title"), args.get("aggregation", "mean")
                    )
                    if img_path:
                        images.append(img_path)

                elif name == "detect_anomalies":
                    img_path, result = detect_anomalies(phone, args.get("column",""), args.get("method","iqr"))
                    if img_path:
                        images.append(img_path)

                else:
                    result = f"Ferramenta '{name}' não encontrada."

                messages.append({"role": "tool", "content": str(result)[:4000]})

        conversations[phone] = [m for m in messages if m["role"] != "system"]
        return "Desculpa, a análise ficou complexa demais. Tenta reformular?", images

    except Exception as e:
        print(f"[ERRO] Ollama: {e}")
        return f"Tive um problema técnico: {e}", images


# ── Typing indicator ─────────────────────────────────────────────────────────
def send_typing(phone, duration=25):
    """Envia indicador de 'digitando...' no WhatsApp via Twilio."""
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    stop_event = threading.Event()

    def _keep_typing():
        while not stop_event.is_set():
            try:
                # Twilio não tem typing nativo pra WhatsApp sandbox,
                # mas podemos usar o Content-Type action
                twilio_client.messages.create(
                    from_=TWILIO_WHATSAPP,
                    to=phone,
                    content_sid=None,
                    body=None,
                    status_callback=None,
                )
            except:
                pass
            stop_event.wait(3)

    # Como Twilio sandbox não suporta typing indicator diretamente,
    # enviamos uma reação rápida de "processando"
    return stop_event


def send_processing(phone):
    """Envia msg rápida de status enquanto processa."""
    try:
        twilio_client.messages.create(
            from_=TWILIO_WHATSAPP,
            to=phone,
            body="⏳",
        )
    except Exception as e:
        print(f"[WARN] Status msg: {e}")


# ── Webhook ──────────────────────────────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def receive_message():
    phone = request.form.get("From", "")
    text = request.form.get("Body", "").strip()

    if not text:
        return str(MessagingResponse()), 200

    phone_clean = phone.replace("whatsapp:", "")
    print(f"[MSG] {phone_clean}: {text}")

    # Responde 200 imediatamente pro Twilio não dar timeout
    # e processa em background
    def process_and_reply():
        # Envia indicador de processando
        try:
            twilio_client.messages.create(
                from_=TWILIO_WHATSAPP,
                to=phone,
                body="_digitando..._",
            )
        except:
            pass

        # Executa o agente
        response_text, images = run_agent(phone_clean, text)
        print(f"[RESP] {phone_clean}: {response_text[:100]}...")

        try:
            # Envia texto
            if response_text:
                parts = [response_text[i:i+1600] for i in range(0, len(response_text), 1600)]
                for part in parts:
                    twilio_client.messages.create(
                        from_=TWILIO_WHATSAPP,
                        to=phone,
                        body=part,
                    )

            # Envia imagens (gráficos)
            for img_path in images:
                if img_path and os.path.exists(img_path) and NGROK_URL:
                    filename = os.path.basename(img_path)
                    media_url = f"{NGROK_URL}/images/{filename}"
                    twilio_client.messages.create(
                        from_=TWILIO_WHATSAPP,
                        to=phone,
                        body="📊",
                        media_url=[media_url],
                    )
                    print(f"[IMG] Enviada: {media_url}")

        except Exception as e:
            print(f"[ERRO] Envio: {e}")

    threading.Thread(target=process_and_reply, daemon=True).start()
    return str(MessagingResponse()), 200


# ── Servir imagens ───────────────────────────────────────────────────────────
@app.route("/images/<filename>")
def serve_image(filename):
    from flask import send_from_directory
    return send_from_directory(tempfile.gettempdir(), filename)


@app.route("/", methods=["GET"])
def health():
    return "DataChat WhatsApp Bot (Twilio) com dados!", 200


if __name__ == "__main__":
    import sys

    # Detecta URL do ngrok automaticamente
    try:
        import requests as req
        r = req.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
        tunnels = r.json().get("tunnels", [])
        for t in tunnels:
            if t.get("proto") == "https":
                NGROK_URL = t["public_url"]
                break
        if NGROK_URL:
            print(f"[NGROK] URL detectada: {NGROK_URL}")
        else:
            print("[NGROK] Nenhum tunnel HTTPS encontrado. Gráficos não serão enviados como imagem.")
    except:
        print("[NGROK] ngrok não detectado. Rode: ngrok http 5000")

    print()
    print("=" * 50)
    print("  DataChat WhatsApp Bot (Twilio)")
    print("  Com análise de dados e gráficos")
    print("  Servidor rodando na porta 5000")
    print("=" * 50)
    print()
    app.run(host="0.0.0.0", port=5001, debug=True)
