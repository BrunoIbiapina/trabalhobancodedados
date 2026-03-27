# DataChat — Plataforma de Análise Conversacional de Dados

Sistema completo de análise de dados com IA local, que permite conversar sobre datasets CSV em linguagem natural usando **Ollama** (grátis, roda no seu computador).

## Interfaces

| Interface | Arquivo | Descrição |
|-----------|---------|-----------|
| Web App | `frontend/app_streamlit.py` | Chat interativo com gráficos 2D/3D via Streamlit |
| WhatsApp (Twilio) | `backend/whatsapp_twilio.py` | Bot WhatsApp com análise de dados e envio de gráficos |
| WhatsApp (Meta) | `backend/whatsapp_bot.py` | Bot WhatsApp conversacional via API Meta |
| Terminal/Jupyter | `backend/csv_bot_claude.py` | Bot conversacional para análise rápida |
| Machine Learning | `decision_tree_completo.ipynb` | Pipeline completo de Decision Tree Classifier |

## Tecnologias

- **IA**: Ollama (local, gratuito) — modelo `qwen2.5:7b` (ou llama3.1:8b, mistral)
- **Web**: Streamlit (interface), Flask (webhook)
- **Visualização**: Plotly (2D e 3D interativos)
- **Dados**: Pandas, NumPy
- **ML**: Scikit-learn, Matplotlib, Seaborn
- **WhatsApp**: Twilio SDK, Meta WhatsApp Business API
- **Infra**: ngrok (tunnel), Kaleido (export PNG)

## Como Executar

---

### ✅ Instalação — rode uma única vez

**1. Baixar o Ollama**
Acesse https://ollama.com, instale e depois rode:
```bash
ollama pull qwen2.5:7b
```

**2. Instalar dependências Python**
```bash
pip3 install ollama streamlit flask twilio pandas numpy plotly kaleido requests scikit-learn matplotlib seaborn jupyter networkx python-dotenv --break-system-packages
```

---

### 🌐 App Web (Streamlit)

Abra **1 terminal**:

```bash
streamlit run frontend/app_streamlit.py
```

Acesse em: `http://localhost:8501`

---

### 📱 Bot WhatsApp (Twilio)

Abra **2 terminais**:

```bash
# Terminal 1 — servidor Flask:
python3 backend/whatsapp_twilio.py

# Terminal 2 — túnel ngrok:
ngrok http 5001
```

Depois:
1. Copie a URL gerada pelo ngrok (ex: `https://xxxx.ngrok-free.app`)
2. Cole no **Twilio Console → Sandbox Settings → "When a message comes in"**:
   ```
   https://xxxx.ngrok-free.app/webhook
   ```
3. Clique em **Save**

> ⚠️ A URL do ngrok muda toda vez que você reinicia. Sempre atualize no Twilio.

---

### 📓 Notebook Machine Learning

```bash
jupyter notebook decision_tree_completo.ipynb
```

---

### Notebook Machine Learning (Decision Tree)

```bash
jupyter notebook decision_tree_completo.ipynb
```

## Funcionalidades

- **Chat com IA** — Converse sobre seus dados em português
- **Gráficos 2D** — Histogram, Scatter, Bar, Box, Heatmap, Pie, Line, Violin
- **Gráficos 3D** — Scatter3D, Surface3D, Bar3D, Mesh3D
- **Detecção de anomalias** — IQR e Z-Score com gráficos anotados
- **Consultas pandas** — Linguagem natural → código pandas
- **Geração de dados** — Cria registros sintéticos
- **Streaming** — Respostas letra por letra no Streamlit
- **WhatsApp** — Análise de dados direto pelo celular

## Arquitetura

```
Usuário (Web/WhatsApp)
        ↓
  Ollama — modelo local (Agentic Loop)
        ↓
  Tools: get_data_info | run_query | create_chart | detect_anomalies
        ↓
  Pandas DataFrame + Plotly
        ↓
  Resposta (texto + gráficos)
```

## Dataset

O projeto inclui `sample.csv` — dataset de tráfego de rede (~17MB) com dados de cybersegurança:
- Source/Destination Port, Protocol, Packet Length
- Attack Type (DDoS, Malware, Intrusion)
- Anomaly Scores, Severity Level, Action Taken

## Estrutura

```
TrabalhoBD/
├── frontend/
│   └── app_streamlit.py              # App web principal
├── backend/
│   ├── csv_bot_claude.py             # Bot conversacional terminal
│   ├── whatsapp_bot.py               # Bot WhatsApp (Meta API)
│   ├── whatsapp_twilio.py            # Bot WhatsApp (Twilio)
│   └── gerar_docs.py                 # Script gerador de docs
├── data/
│   └── sample.csv                    # Dataset cybersegurança
├── decision_tree_completo.ipynb      # Notebook ML
├── confusion_matrix.png              # Matriz de confusão
├── feature_importance.png            # Importância das features
├── DataChat_Documentacao.pdf         # Documentação técnica completa
├── .env.example                      # Variáveis de ambiente necessárias
├── .gitignore
└── README.md                         # Este arquivo
```

## Autor

**Bruno Ibiapina** — Março 2026

---

> Documentação técnica completa disponível em `DataChat_Documentacao.pdf`
