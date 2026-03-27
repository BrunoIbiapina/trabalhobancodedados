# DataChat — Plataforma de Análise Conversacional de Dados

Sistema completo de análise de dados com IA, que permite conversar sobre datasets CSV em linguagem natural usando Claude (Anthropic).

## Interfaces

| Interface | Arquivo | Descrição |
|-----------|---------|-----------|
| Web App | `frontend/app_streamlit.py` | Chat interativo com gráficos 2D/3D via Streamlit |
| WhatsApp (Twilio) | `backend/whatsapp_twilio.py` | Bot WhatsApp com análise de dados e envio de gráficos |
| WhatsApp (Meta) | `backend/whatsapp_bot.py` | Bot WhatsApp conversacional via API Meta |
| Terminal/Jupyter | `backend/csv_bot_claude.py` | Bot conversacional para análise rápida |
| Machine Learning | `decision_tree_completo.ipynb` | Pipeline completo de Decision Tree Classifier |

## Tecnologias

- **IA**: Claude API (Anthropic) — modelos `claude-opus-4-6` e `claude-sonnet-4-6`
- **Web**: Streamlit (interface), Flask (webhook)
- **Visualização**: Plotly (2D e 3D interativos)
- **Dados**: Pandas, NumPy
- **ML**: Scikit-learn, Matplotlib, Seaborn
- **WhatsApp**: Twilio SDK, Meta WhatsApp Business API
- **Infra**: ngrok (tunnel), Kaleido (export PNG)

## Como Executar

### 1. Instalar dependências (rode uma vez)

```bash
pip install anthropic streamlit flask twilio pandas numpy plotly kaleido requests scikit-learn matplotlib seaborn jupyter networkx --break-system-packages
```

### 2. Configurar a chave da API

Crie um arquivo `.env` na raiz do projeto ou exporte a variável no terminal:

```bash
export ANTHROPIC_API_KEY="sua-chave-aqui"
```

---

### App Web (Streamlit)

```bash
streamlit run frontend/app_streamlit.py
```

Abre automaticamente em `http://localhost:8501`

---

### Bot WhatsApp via Twilio

Requer 2 terminais abertos ao mesmo tempo:

```bash
# Terminal 1 — inicia o servidor Flask na porta 5001:
python3 backend/whatsapp_twilio.py

# Terminal 2 — expõe o servidor para a internet:
ngrok http 5001
```

Depois copie a URL gerada pelo ngrok (ex: `https://xxxx.ngrok-free.app`) e cole no **Twilio Console > Sandbox Settings > Webhook URL**, adicionando `/webhook` no final.

---

### Bot WhatsApp via Meta API

```bash
python3 backend/whatsapp_bot.py
```

---

### Bot conversacional no terminal

```bash
python3 backend/csv_bot_claude.py
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
  Claude API (Agentic Loop)
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
