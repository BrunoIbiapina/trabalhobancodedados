# DataChat — Plataforma de Análise Conversacional de Dados

Sistema completo de análise de dados com IA, que permite conversar sobre datasets CSV em linguagem natural usando Claude (Anthropic).

## Interfaces

| Interface | Arquivo | Descrição |
|-----------|---------|-----------|
| Web App | `app_streamlit.py` | Chat interativo com gráficos 2D/3D via Streamlit |
| WhatsApp (Twilio) | `whatsapp_twilio.py` | Bot WhatsApp com análise de dados e envio de gráficos |
| WhatsApp (Meta) | `whatsapp_bot.py` | Bot WhatsApp conversacional via API Meta |
| Terminal/Jupyter | `csv_bot_claude.py` | Bot conversacional para análise rápida |
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

### App Streamlit
```bash
pip install anthropic streamlit plotly pandas numpy
streamlit run app_streamlit.py
```

### Bot WhatsApp (Twilio)
```bash
pip install anthropic flask twilio pandas numpy plotly kaleido requests

# Terminal 1:
python3 whatsapp_twilio.py

# Terminal 2:
ngrok http 5000

# Configure a URL do ngrok no Twilio Console > Sandbox Settings
```

### Notebook Decision Tree
```bash
pip install scikit-learn matplotlib seaborn plotly pandas numpy
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
├── app_streamlit.py              # App web principal
├── whatsapp_twilio.py            # Bot WhatsApp (Twilio)
├── whatsapp_bot.py               # Bot WhatsApp (Meta API)
├── csv_bot_claude.py             # Bot conversacional terminal
├── decision_tree_completo.ipynb  # Notebook ML
├── sample.csv                    # Dataset cybersegurança
├── confusion_matrix.png          # Matriz de confusão
├── decision_tree.png             # Visualização da árvore
├── feature_importance.png        # Importância das features
├── DataChat_Documentacao.pdf     # Documentação técnica completa
├── README.md                     # Este arquivo
└── gerar_docs.py                 # Script gerador de docs
```

## Autor

**Bruno Ibiapina** — Março 2026

---

> Documentação técnica completa disponível em `DataChat_Documentacao.pdf`
