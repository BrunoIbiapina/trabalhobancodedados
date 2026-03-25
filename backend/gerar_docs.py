"""
Gera documentação completa do projeto DataChat em PDF e README.md
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, HRFlowable, ListFlowable, ListItem
)
from reportlab.pdfgen import canvas
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(OUTPUT_DIR, "DataChat_Documentacao.pdf")
README_PATH = os.path.join(OUTPUT_DIR, "README.md")

# ── Cores ────────────────────────────────────────────────────────────────────
COR_PRIMARIA = HexColor("#c96442")
COR_ESCURA = HexColor("#2c2c2c")
COR_CINZA = HexColor("#666666")
COR_BG_CODE = HexColor("#f5f1eb")
COR_BORDA = HexColor("#d6cfc5")
COR_FUNDO_HEADER = HexColor("#c96442")

# ── Estilos ──────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

titulo_capa = ParagraphStyle(
    "TituloCapa", parent=styles["Title"],
    fontSize=36, leading=42, textColor=white,
    alignment=TA_CENTER, spaceAfter=10,
    fontName="Helvetica-Bold"
)

subtitulo_capa = ParagraphStyle(
    "SubtituloCapa", parent=styles["Normal"],
    fontSize=14, leading=20, textColor=HexColor("#ffe0d0"),
    alignment=TA_CENTER, spaceAfter=6,
    fontName="Helvetica"
)

h1 = ParagraphStyle(
    "H1Custom", parent=styles["Heading1"],
    fontSize=22, leading=28, textColor=COR_PRIMARIA,
    spaceBefore=24, spaceAfter=12,
    fontName="Helvetica-Bold",
    borderWidth=0, borderPadding=0,
)

h2 = ParagraphStyle(
    "H2Custom", parent=styles["Heading2"],
    fontSize=16, leading=22, textColor=COR_ESCURA,
    spaceBefore=18, spaceAfter=8,
    fontName="Helvetica-Bold"
)

h3 = ParagraphStyle(
    "H3Custom", parent=styles["Heading3"],
    fontSize=13, leading=18, textColor=COR_CINZA,
    spaceBefore=12, spaceAfter=6,
    fontName="Helvetica-Bold"
)

corpo = ParagraphStyle(
    "Corpo", parent=styles["Normal"],
    fontSize=10.5, leading=15, textColor=COR_ESCURA,
    alignment=TA_JUSTIFY, spaceAfter=8,
    fontName="Helvetica"
)

codigo = ParagraphStyle(
    "Codigo", parent=styles["Code"],
    fontSize=8.5, leading=12, textColor=HexColor("#333333"),
    backColor=COR_BG_CODE, borderColor=COR_BORDA,
    borderWidth=0.5, borderPadding=8,
    spaceAfter=10, spaceBefore=4,
    fontName="Courier",
    leftIndent=10, rightIndent=10,
)

bullet = ParagraphStyle(
    "Bullet", parent=corpo,
    leftIndent=20, bulletIndent=8,
    spaceBefore=2, spaceAfter=2,
)

tabela_header = ParagraphStyle(
    "TabelaHeader", parent=styles["Normal"],
    fontSize=9.5, textColor=white,
    fontName="Helvetica-Bold", alignment=TA_CENTER,
)

tabela_cell = ParagraphStyle(
    "TabelaCell", parent=styles["Normal"],
    fontSize=9, textColor=COR_ESCURA,
    fontName="Helvetica", alignment=TA_LEFT,
    leading=13,
)


# ── Helpers ──────────────────────────────────────────────────────────────────
def hr():
    return HRFlowable(width="100%", thickness=0.5, color=COR_BORDA, spaceBefore=12, spaceAfter=12)

def bullet_list(items):
    return ListFlowable(
        [ListItem(Paragraph(item, bullet), bulletColor=COR_PRIMARIA) for item in items],
        bulletType="bullet", bulletFontSize=8, leftIndent=15,
    )

def code_block(text):
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(safe.replace("\n", "<br/>"), codigo)

def make_table(headers, rows):
    header_paras = [Paragraph(h, tabela_header) for h in headers]
    row_paras = [[Paragraph(str(c), tabela_cell) for c in row] for row in rows]
    data = [header_paras] + row_paras
    n_cols = len(headers)
    col_w = (A4[0] - 3 * cm) / n_cols

    t = Table(data, colWidths=[col_w] * n_cols)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COR_PRIMARIA),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("BACKGROUND", (0, 1), (-1, -1), HexColor("#faf8f5")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#faf8f5"), white]),
        ("GRID", (0, 0), (-1, -1), 0.4, COR_BORDA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


# ── Capa customizada ─────────────────────────────────────────────────────────
class CoverPage:
    @staticmethod
    def draw(c_canvas, doc):
        c_canvas.saveState()
        w, h = A4
        # Fundo gradiente
        c_canvas.setFillColor(COR_FUNDO_HEADER)
        c_canvas.rect(0, h * 0.45, w, h * 0.55, fill=True, stroke=False)
        c_canvas.setFillColor(HexColor("#f9f7f4"))
        c_canvas.rect(0, 0, w, h * 0.45, fill=True, stroke=False)
        # Linha decorativa
        c_canvas.setStrokeColor(HexColor("#e07a5a"))
        c_canvas.setLineWidth(3)
        c_canvas.line(w * 0.1, h * 0.45, w * 0.9, h * 0.45)
        c_canvas.restoreState()


def footer(c_canvas, doc):
    c_canvas.saveState()
    c_canvas.setFont("Helvetica", 8)
    c_canvas.setFillColor(COR_CINZA)
    c_canvas.drawCentredString(A4[0] / 2, 1.2 * cm, f"DataChat — Documentacao Tecnica  |  Pagina {doc.page}")
    c_canvas.restoreState()


# ── Conteúdo ─────────────────────────────────────────────────────────────────
def build_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH, pagesize=A4,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.5 * cm, bottomMargin=2 * cm,
    )

    story = []

    # ════════════════════════════════════════════════════════════════════════
    # CAPA
    # ════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 6 * cm))
    story.append(Paragraph("DataChat", titulo_capa))
    story.append(Paragraph("Plataforma de Analise Conversacional de Dados", subtitulo_capa))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Documentacao Tecnica Completa", subtitulo_capa))
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph("Web App (Streamlit) + WhatsApp Bot (Twilio) + Decision Tree ML", subtitulo_capa))
    story.append(Spacer(1, 3 * cm))

    info_capa = ParagraphStyle("InfoCapa", parent=corpo, alignment=TA_CENTER, textColor=COR_CINZA, fontSize=10)
    story.append(Paragraph("Autor: Bruno Ibiapina", info_capa))
    story.append(Paragraph("Data: Marco 2026", info_capa))
    story.append(Paragraph("Versao: 1.0", info_capa))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════════
    # SUMÁRIO
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Sumario", h1))
    story.append(hr())
    sumario_items = [
        "1. Visao Geral do Projeto",
        "2. Arquitetura do Sistema",
        "3. Tecnologias e Ferramentas",
        "4. Configuracao do Ambiente",
        "5. App Streamlit (app_streamlit.py)",
        "6. Bot WhatsApp via Twilio (whatsapp_twilio.py)",
        "7. Bot WhatsApp via Meta (whatsapp_bot.py)",
        "8. Bot CSV Conversacional (csv_bot_claude.py)",
        "9. Decision Tree Classifier (Notebook)",
        "10. Integracao com API Claude (Anthropic)",
        "11. Sistema de Tools (Agentic Loop)",
        "12. Estrutura de Arquivos",
        "13. Como Executar",
        "14. Fluxo de Dados",
        "15. Proximos Passos",
    ]
    story.append(bullet_list(sumario_items))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════════
    # 1. VISÃO GERAL
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("1. Visao Geral do Projeto", h1))
    story.append(hr())
    story.append(Paragraph(
        "O <b>DataChat</b> e uma plataforma de analise conversacional de dados que permite ao usuario "
        "interagir com datasets CSV usando linguagem natural. O sistema utiliza a API do Claude (Anthropic) "
        "como motor de inteligencia artificial, combinado com ferramentas de visualizacao (Plotly) e "
        "analise de dados (Pandas/NumPy) para fornecer insights automaticos.",
        corpo
    ))
    story.append(Paragraph(
        "O projeto possui <b>tres interfaces</b> de uso: um aplicativo web interativo via Streamlit, "
        "um bot para WhatsApp via Twilio, e um bot WhatsApp via API direta da Meta. Alem disso, inclui "
        "um notebook de Machine Learning com Decision Tree Classifier e um bot conversacional de terminal.",
        corpo
    ))

    story.append(Paragraph("Funcionalidades Principais", h2))
    story.append(bullet_list([
        "<b>Chat com IA</b> — Converse sobre seus dados em portugues brasileiro",
        "<b>Graficos interativos</b> — 2D (bar, scatter, line, pie, box, heatmap, violin) e 3D (scatter3d, surface3d, bar3d, mesh3d)",
        "<b>Deteccao de anomalias</b> — Metodos IQR e Z-Score com graficos anotados",
        "<b>Consultas em linguagem natural</b> — Traduzidas para Pandas automaticamente",
        "<b>Geracao de dados sinteticos</b> — Cria novos registros baseados em padroes",
        "<b>Exportacao CSV</b> — Salva resultados processados",
        "<b>Streaming de respostas</b> — Texto aparece letra por letra no Streamlit",
        "<b>WhatsApp Bot</b> — Analise de dados direto pelo WhatsApp com envio de graficos como imagem",
        "<b>Machine Learning</b> — Pipeline completo de Decision Tree com GridSearchCV",
    ]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════════
    # 2. ARQUITETURA
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("2. Arquitetura do Sistema", h1))
    story.append(hr())
    story.append(Paragraph(
        "A arquitetura segue o padrao <b>Agentic Loop</b> (loop agentivo), onde o Claude atua como "
        "cerebro central que decide quais ferramentas (tools) usar com base na mensagem do usuario. "
        "O fluxo e iterativo: o usuario faz uma pergunta, o Claude analisa, executa tools se necessario, "
        "recebe os resultados, e formula uma resposta final.",
        corpo
    ))

    story.append(Paragraph("Diagrama de Fluxo", h2))
    story.append(code_block(
        "Usuario (Streamlit/WhatsApp)\n"
        "        |\n"
        "        v\n"
        "  [Mensagem em linguagem natural]\n"
        "        |\n"
        "        v\n"
        "  Claude API (claude-sonnet-4-6 / claude-opus-4-6)\n"
        "        |\n"
        "        |-- Precisa de dados? --> Tool: get_data_info()\n"
        "        |-- Precisa calcular? --> Tool: run_query()\n"
        "        |-- Precisa grafico?  --> Tool: create_chart()\n"
        "        |-- Anomalias?        --> Tool: detect_anomalies()\n"
        "        |-- Gerar dados?      --> Tool: generate_data()\n"
        "        |-- Salvar CSV?       --> Tool: save_csv()\n"
        "        |\n"
        "        v\n"
        "  [Resultado da tool]\n"
        "        |\n"
        "        v\n"
        "  Claude formula resposta final\n"
        "        |\n"
        "        v\n"
        "  Usuario recebe texto + graficos"
    ))

    story.append(Paragraph("Camadas do Sistema", h2))
    story.append(make_table(
        ["Camada", "Componente", "Funcao"],
        [
            ["Interface", "Streamlit / WhatsApp", "Recebe input do usuario e exibe resultados"],
            ["IA", "Claude API (Anthropic)", "Processa linguagem natural e decide acoes"],
            ["Tools", "Python functions", "Executam analises, graficos, queries"],
            ["Dados", "Pandas DataFrame", "Armazena e manipula o dataset CSV"],
            ["Visualizacao", "Plotly", "Gera graficos interativos 2D e 3D"],
            ["ML", "Scikit-learn", "Decision Tree Classifier com GridSearchCV"],
        ]
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════════
    # 3. TECNOLOGIAS
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("3. Tecnologias e Ferramentas", h1))
    story.append(hr())

    story.append(Paragraph("Linguagem e Runtime", h2))
    story.append(make_table(
        ["Tecnologia", "Versao", "Uso"],
        [
            ["Python", "3.11+", "Linguagem principal de todo o projeto"],
            ["pip", "24+", "Gerenciador de pacotes"],
        ]
    ))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Bibliotecas Python", h2))
    story.append(make_table(
        ["Biblioteca", "Uso no Projeto"],
        [
            ["anthropic", "SDK oficial da Anthropic para acessar a API do Claude"],
            ["streamlit", "Framework web para criar o app interativo (app_streamlit.py)"],
            ["plotly", "Graficos interativos 2D e 3D (scatter, bar, surface, etc.)"],
            ["pandas", "Manipulacao e analise de dados tabulares (DataFrames)"],
            ["numpy", "Operacoes numericas, calculos estatisticos"],
            ["flask", "Servidor web leve para os webhooks do WhatsApp"],
            ["twilio", "SDK do Twilio para enviar/receber mensagens WhatsApp"],
            ["scikit-learn", "Machine Learning — Decision Tree, GridSearchCV, metricas"],
            ["matplotlib", "Visualizacoes estaticas no notebook (arvore de decisao)"],
            ["seaborn", "Graficos estatisticos (matriz de confusao)"],
            ["kaleido", "Exporta graficos Plotly como imagens PNG"],
            ["requests", "Chamadas HTTP (API Meta, deteccao ngrok)"],
        ]
    ))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Servicos e APIs", h2))
    story.append(make_table(
        ["Servico", "Uso"],
        [
            ["Anthropic Claude API", "Motor de IA — modelos claude-sonnet-4-6 e claude-opus-4-6"],
            ["Twilio WhatsApp Sandbox", "Envio e recebimento de mensagens WhatsApp"],
            ["Meta WhatsApp Business API", "API direta do WhatsApp (alternativa ao Twilio)"],
            ["ngrok", "Tunnel HTTP para expor servidor local na internet"],
        ]
    ))
    story.append(Spacer(1, 12))

    story.append(Paragraph("IDEs e Ferramentas de Desenvolvimento", h2))
    story.append(make_table(
        ["Ferramenta", "Uso"],
        [
            ["VS Code / PyCharm", "Edicao de codigo Python"],
            ["Claude Code (CLI)", "Assistente de desenvolvimento com IA no terminal"],
            ["Jupyter Notebook", "Desenvolvimento do pipeline de ML (Decision Tree)"],
            ["Terminal / Warp", "Execucao de comandos, servidores, ngrok"],
            ["Git", "Controle de versao"],
            ["Meta for Developers", "Configuracao do WhatsApp Business API"],
            ["Twilio Console", "Configuracao do sandbox WhatsApp"],
        ]
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════════
    # 4. CONFIGURAÇÃO DO AMBIENTE
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("4. Configuracao do Ambiente", h1))
    story.append(hr())

    story.append(Paragraph("Pre-requisitos", h2))
    story.append(bullet_list([
        "Python 3.11 ou superior instalado",
        "Conta na Anthropic com API key ativa",
        "Conta no Twilio (para WhatsApp bot)",
        "ngrok instalado (para WhatsApp webhook)",
        "Google Chrome (para exportar graficos como PNG via Kaleido)",
    ]))

    story.append(Paragraph("Instalacao de Dependencias", h2))
    story.append(code_block(
        "# Instalar todas as dependencias\n"
        "pip install anthropic streamlit plotly pandas numpy flask twilio\n"
        "pip install scikit-learn matplotlib seaborn kaleido requests\n\n"
        "# Instalar Chrome para Kaleido (exportar graficos)\n"
        "python3 -c \"import kaleido; kaleido.get_chrome_sync()\"\n\n"
        "# Instalar ngrok (macOS)\n"
        "brew install ngrok\n"
        "ngrok config add-authtoken SEU_TOKEN_NGROK"
    ))

    story.append(Paragraph("Variaveis de Configuracao", h2))
    story.append(make_table(
        ["Variavel", "Onde", "Descricao"],
        [
            ["ANTHROPIC_KEY", "Todos os arquivos .py", "Chave da API Anthropic (sk-ant-...)"],
            ["TWILIO_ACCOUNT_SID", "whatsapp_twilio.py", "SID da conta Twilio"],
            ["TWILIO_AUTH_TOKEN", "whatsapp_twilio.py", "Token de autenticacao Twilio"],
            ["WHATSAPP_TOKEN", "whatsapp_bot.py", "Token da API Meta WhatsApp"],
            ["PHONE_NUMBER_ID", "whatsapp_bot.py", "ID do numero de telefone Meta"],
            ["VERIFY_TOKEN", "whatsapp_bot.py", "Token de verificacao do webhook"],
        ]
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════════
    # 5. APP STREAMLIT
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("5. App Streamlit (app_streamlit.py)", h1))
    story.append(hr())
    story.append(Paragraph(
        "O aplicativo web principal, construido com Streamlit. Oferece uma interface de chat "
        "semelhante ao Claude, com input na parte inferior, sidebar com opcoes, e area central "
        "para mensagens e graficos.",
        corpo
    ))

    story.append(Paragraph("Como Executar", h2))
    story.append(code_block("streamlit run app_streamlit.py"))

    story.append(Paragraph("Estrutura do Codigo", h2))
    story.append(make_table(
        ["Secao", "Linhas (aprox.)", "Descricao"],
        [
            ["CSS e Estilos", "24-80", "Customizacao visual (cores, fontes, layout estilo Claude)"],
            ["Configuracao", "80-120", "API key, cliente Anthropic, session state"],
            ["Tool Functions", "120-500", "get_data_info, run_query, create_chart, detect_anomalies, generate_data, save_csv"],
            ["Tools Definition", "500-560", "Lista JSON das tools para a API do Claude"],
            ["System Prompt", "560-600", "Instrucoes para o comportamento do Claude"],
            ["Agentic Loop", "600-680", "run_agent_streaming() — loop com streaming e tool use"],
            ["Interface", "680-740", "Sidebar, chat, historico, renderizacao de graficos"],
        ]
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Tools Disponiveis", h2))
    story.append(make_table(
        ["Tool", "Parametros", "Retorno"],
        [
            ["get_data_info", "sample_rows (int)", "Shape, colunas, tipos, estatisticas, amostra"],
            ["run_query", "code (string pandas)", "Resultado da expressao executada no DataFrame"],
            ["create_chart", "chart_type, x_col, y_col, z_col, color_col, title", "Grafico Plotly renderizado na interface"],
            ["detect_anomalies", "column, method (iqr/zscore)", "Grafico com outliers destacados + estatisticas"],
            ["generate_data", "n_rows", "Novos registros sinteticos adicionados ao DataFrame"],
            ["save_csv", "filename", "Arquivo CSV para download"],
        ]
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Tipos de Graficos Suportados", h2))
    story.append(make_table(
        ["Tipo", "Dimensao", "Descricao"],
        [
            ["histogram", "2D", "Distribuicao de frequencia de uma variavel"],
            ["scatter", "2D", "Dispersao entre duas variaveis"],
            ["bar", "2D", "Barras com agregacao (mean, sum, count)"],
            ["box", "2D", "Box plot — quartis e outliers"],
            ["heatmap", "2D", "Matriz de correlacao entre variaveis numericas"],
            ["pie", "2D", "Grafico de pizza com proporcoes"],
            ["line", "2D", "Linha temporal ou sequencial"],
            ["violin", "2D", "Distribuicao com densidade"],
            ["scatter3d", "3D", "Dispersao tridimensional interativa"],
            ["surface3d", "3D", "Superficie interpolada (mapa de relevo)"],
            ["bar3d", "3D", "Barras tridimensionais"],
            ["mesh3d", "3D", "Malha triangulada 3D"],
        ]
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Streaming de Respostas", h2))
    story.append(Paragraph(
        "O app utiliza <b>streaming</b> via <font face='Courier'>client.messages.stream()</font> da API Anthropic. "
        "O texto aparece letra por letra com um cursor piscante, similar ao ChatGPT/Claude. "
        "Durante a execucao de tools, um indicador de status mostra qual ferramenta esta sendo usada "
        "(ex: 'Analisando dados...', 'Gerando grafico...').",
        corpo
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════════
    # 6. BOT WHATSAPP TWILIO
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("6. Bot WhatsApp via Twilio (whatsapp_twilio.py)", h1))
    story.append(hr())
    story.append(Paragraph(
        "Bot que funciona no WhatsApp via Twilio Sandbox. Recebe mensagens, processa com Claude "
        "usando o mesmo sistema de tools do Streamlit, e envia respostas de texto e graficos como "
        "imagens PNG.",
        corpo
    ))

    story.append(Paragraph("Arquitetura", h2))
    story.append(code_block(
        "WhatsApp (usuario)\n"
        "      |\n"
        "      v\n"
        "Twilio Sandbox --> Webhook POST /webhook\n"
        "      |\n"
        "      v\n"
        "Flask Server (porta 5000)\n"
        "      |\n"
        "      v\n"
        "Claude API (tool use loop)\n"
        "      |\n"
        "      v\n"
        "Twilio API (envia resposta + imagens)\n"
        "      |\n"
        "      v\n"
        "WhatsApp (usuario recebe)"
    ))

    story.append(Paragraph("Como Executar", h2))
    story.append(code_block(
        "# Terminal 1: Servidor Flask\n"
        "python3 whatsapp_twilio.py\n\n"
        "# Terminal 2: Tunnel ngrok\n"
        "ngrok http 5000\n\n"
        "# Configurar no Twilio Console:\n"
        "# Sandbox Settings > When a message comes in:\n"
        "# https://SEU-NGROK-URL/webhook"
    ))

    story.append(Paragraph("Envio de Graficos", h2))
    story.append(Paragraph(
        "Graficos sao gerados com Plotly, exportados como PNG via Kaleido, servidos "
        "como arquivos estaticos pelo Flask (<font face='Courier'>/images/filename.png</font>), "
        "e enviados pro WhatsApp via media_url do Twilio. O ngrok fornece a URL publica.",
        corpo
    ))

    story.append(Paragraph("Processamento Assincrono", h2))
    story.append(Paragraph(
        "As mensagens sao processadas em threads separadas para evitar timeout do Twilio "
        "(que espera resposta em ate 15 segundos). O webhook retorna 200 imediatamente e "
        "processa a mensagem em background.",
        corpo
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════════
    # 7. BOT META
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("7. Bot WhatsApp via Meta (whatsapp_bot.py)", h1))
    story.append(hr())
    story.append(Paragraph(
        "Versao alternativa do bot usando a API direta da Meta (WhatsApp Business Platform). "
        "Mais simples que a versao Twilio — funciona apenas com texto conversacional, sem tool use. "
        "Utilizado como fallback ou para testes da API da Meta.",
        corpo
    ))

    story.append(Paragraph("Configuracao na Meta", h2))
    story.append(bullet_list([
        "Criar app em developers.facebook.com",
        "Adicionar produto WhatsApp",
        "Gerar token de acesso temporario (valido 24h)",
        "Configurar webhook com URL do ngrok + token de verificacao",
        "Assinar campo 'messages' no webhook",
        "Adicionar numero de teste na lista de destinatarios",
    ]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════════
    # 8. BOT CSV
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("8. Bot CSV Conversacional (csv_bot_claude.py)", h1))
    story.append(hr())
    story.append(Paragraph(
        "Script Python para terminal/Jupyter que permite conversar sobre dados CSV. "
        "Possui o mesmo sistema de tools do app Streamlit, mas roda em ambiente de notebook "
        "ou terminal interativo. Ideal para analise rapida sem interface web.",
        corpo
    ))
    story.append(Paragraph(
        "Utiliza o modelo <b>claude-opus-4-6</b> com adaptive thinking (extended thinking) "
        "para analises mais profundas e detalhadas.",
        corpo
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════════
    # 9. DECISION TREE
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("9. Decision Tree Classifier (Notebook)", h1))
    story.append(hr())
    story.append(Paragraph(
        "Notebook Jupyter com pipeline completo de Machine Learning usando Arvore de Decisao. "
        "Inclui geracao de dados sinteticos, pre-processamento, treinamento com busca de "
        "hiperparametros, avaliacao e visualizacoes.",
        corpo
    ))

    story.append(Paragraph("Pipeline", h2))
    story.append(make_table(
        ["Etapa", "Detalhe"],
        [
            ["1. Dados", "300 amostras sinteticas, 3 features (X, Y, Z), 3 classes balanceadas"],
            ["2. Pre-processamento", "Verificacao de nulos, separacao train/test (70/30), StandardScaler"],
            ["3. Treinamento", "GridSearchCV com 5-fold CV, busca em max_depth, min_samples_split/leaf, criterion"],
            ["4. Avaliacao", "Accuracy, Precision, Recall, F1-Score, Matriz de Confusao"],
            ["5. Visualizacoes", "Arvore de decisao, Feature Importance, Scatter 3D interativo"],
            ["6. Interpretabilidade", "Regras exportadas em texto legivel"],
        ]
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Bibliotecas Usadas", h2))
    story.append(bullet_list([
        "<b>scikit-learn</b> — DecisionTreeClassifier, GridSearchCV, train_test_split, StandardScaler, metricas",
        "<b>matplotlib</b> — Visualizacao da arvore de decisao e feature importance",
        "<b>seaborn</b> — Matriz de confusao com heatmap",
        "<b>plotly</b> — Scatter 3D interativo das amostras",
        "<b>pandas/numpy</b> — Manipulacao de dados",
    ]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════════
    # 10. API CLAUDE
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("10. Integracao com API Claude (Anthropic)", h1))
    story.append(hr())

    story.append(Paragraph("Modelos Utilizados", h2))
    story.append(make_table(
        ["Modelo", "Onde", "Motivo"],
        [
            ["claude-opus-4-6", "app_streamlit.py, csv_bot_claude.py", "Maior capacidade de raciocinio, adaptive thinking"],
            ["claude-sonnet-4-6", "whatsapp_twilio.py, whatsapp_bot.py", "Mais rapido, ideal para respostas no WhatsApp"],
        ]
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Exemplo de Chamada com Tool Use", h2))
    story.append(code_block(
        "import anthropic\n\n"
        "client = anthropic.Anthropic(api_key=\"sk-ant-...\")\n\n"
        "response = client.messages.create(\n"
        "    model=\"claude-sonnet-4-6\",\n"
        "    max_tokens=4096,\n"
        "    system=\"Voce e um assistente de dados...\",\n"
        "    tools=[  # Lista de tools disponiveis\n"
        "        {\"name\": \"run_query\",\n"
        "         \"description\": \"Executa pandas...\",\n"
        "         \"input_schema\": {\n"
        "             \"type\": \"object\",\n"
        "             \"properties\": {\"code\": {\"type\": \"string\"}},\n"
        "             \"required\": [\"code\"]\n"
        "         }}\n"
        "    ],\n"
        "    messages=historico_conversa,\n"
        ")"
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Streaming (Streamlit)", h2))
    story.append(code_block(
        "with client.messages.stream(\n"
        "    model=\"claude-opus-4-6\",\n"
        "    max_tokens=16000,\n"
        "    system=SYSTEM_PROMPT,\n"
        "    tools=TOOLS,\n"
        "    messages=history,\n"
        ") as stream:\n"
        "    for event in stream:\n"
        "        if event.type == \"content_block_delta\":\n"
        "            if event.delta.type == \"text_delta\":\n"
        "                texto += event.delta.text\n"
        "                placeholder.markdown(texto + \" |\")"
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════════
    # 11. SISTEMA DE TOOLS
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("11. Sistema de Tools (Agentic Loop)", h1))
    story.append(hr())
    story.append(Paragraph(
        "O sistema de tools e o coracao do DataChat. Ele permite que o Claude execute codigo Python "
        "real para analisar dados, gerar graficos e detectar anomalias. O loop agentivo funciona assim:",
        corpo
    ))

    story.append(code_block(
        "1. Usuario envia mensagem\n"
        "2. Claude recebe mensagem + lista de tools disponiveis\n"
        "3. Claude decide:\n"
        "   a) Responder diretamente (sem tools) --> FIM\n"
        "   b) Chamar uma ou mais tools\n"
        "4. Se chamou tools:\n"
        "   - Executa cada tool com os parametros que Claude forneceu\n"
        "   - Envia os resultados de volta pro Claude\n"
        "   - Claude analisa os resultados\n"
        "   - Volta pro passo 3 (pode chamar mais tools)\n"
        "5. Max 5 iteracoes para evitar loop infinito"
    ))

    story.append(Paragraph("Formato de uma Tool", h2))
    story.append(code_block(
        "{\n"
        "    \"name\": \"create_chart\",\n"
        "    \"description\": \"Cria grafico interativo\",\n"
        "    \"input_schema\": {\n"
        "        \"type\": \"object\",\n"
        "        \"properties\": {\n"
        "            \"chart_type\": {\"type\": \"string\"},\n"
        "            \"x_col\": {\"type\": \"string\"},\n"
        "            \"y_col\": {\"type\": \"string\"}\n"
        "        },\n"
        "        \"required\": [\"chart_type\"]\n"
        "    }\n"
        "}"
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════════
    # 12. ESTRUTURA DE ARQUIVOS
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("12. Estrutura de Arquivos", h1))
    story.append(hr())
    story.append(make_table(
        ["Arquivo", "Tipo", "Descricao"],
        [
            ["app_streamlit.py", "App Web", "Interface principal — chat interativo com graficos"],
            ["whatsapp_twilio.py", "Bot WhatsApp", "Bot com Twilio, tool use e envio de graficos"],
            ["whatsapp_bot.py", "Bot WhatsApp", "Bot com API Meta, conversacional simples"],
            ["csv_bot_claude.py", "Bot Terminal", "Bot conversacional para terminal/Jupyter"],
            ["decision_tree_completo.ipynb", "Notebook ML", "Pipeline de Decision Tree Classifier"],
            ["sample.csv", "Dataset", "Dados de trafego de rede (~17MB, cyberseguranca)"],
            ["confusion_matrix.png", "Imagem", "Matriz de confusao do modelo Decision Tree"],
            ["decision_tree.png", "Imagem", "Visualizacao da arvore de decisao treinada"],
            ["feature_importance.png", "Imagem", "Grafico de importancia das features"],
            ["gerar_docs.py", "Script", "Gera este PDF e o README.md"],
            ["README.md", "Docs", "Documentacao do projeto para GitHub"],
        ]
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════════
    # 13. COMO EXECUTAR
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("13. Como Executar", h1))
    story.append(hr())

    story.append(Paragraph("App Streamlit (Interface Web)", h2))
    story.append(code_block(
        "cd ~/Downloads/TrabalhoBD\n"
        "streamlit run app_streamlit.py\n"
        "# Acesse: http://localhost:8501"
    ))

    story.append(Paragraph("Bot WhatsApp (Twilio)", h2))
    story.append(code_block(
        "# Terminal 1:\n"
        "cd ~/Downloads/TrabalhoBD\n"
        "python3 whatsapp_twilio.py\n\n"
        "# Terminal 2:\n"
        "ngrok http 5000\n\n"
        "# No Twilio Console:\n"
        "# 1. Ativar sandbox: mande 'join xxx-xxx' pro +14155238886\n"
        "# 2. Sandbox Settings > When a message comes in:\n"
        "#    https://SEU-NGROK-URL/webhook\n"
        "# 3. Mande mensagem pro +14155238886 no WhatsApp"
    ))

    story.append(Paragraph("Bot WhatsApp (Meta)", h2))
    story.append(code_block(
        "# Terminal 1:\n"
        "python3 whatsapp_bot.py\n\n"
        "# Terminal 2:\n"
        "ngrok http 5000\n\n"
        "# No Meta for Developers:\n"
        "# WhatsApp > Configuracao > Webhook:\n"
        "#   URL: https://SEU-NGROK-URL/webhook\n"
        "#   Token: datachat_verify_2024"
    ))

    story.append(Paragraph("Notebook Decision Tree", h2))
    story.append(code_block(
        "jupyter notebook decision_tree_completo.ipynb\n"
        "# Ou no VS Code: abra o arquivo e execute celula por celula"))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════════
    # 14. FLUXO DE DADOS
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("14. Fluxo de Dados", h1))
    story.append(hr())

    story.append(Paragraph("Dataset: sample.csv", h2))
    story.append(Paragraph(
        "O dataset principal contem dados de trafego de rede para analise de cyberseguranca. "
        "Possui aproximadamente 17MB com as seguintes colunas:",
        corpo
    ))
    story.append(make_table(
        ["Coluna", "Tipo", "Exemplo"],
        [
            ["Source Port", "Numerico", "1027 - 65530"],
            ["Destination Port", "Numerico", "1024 - 65535"],
            ["Protocol", "Categorico", "TCP, UDP, ICMP"],
            ["Packet Length", "Numerico", "64 - 1500 bytes"],
            ["Packet Type", "Categorico", "Data, Control"],
            ["Traffic Type", "Categorico", "HTTP, DNS, FTP"],
            ["Attack Type", "Categorico", "DDoS, Malware, Intrusion"],
            ["Anomaly Scores", "Numerico", "0 - 100"],
            ["Severity Level", "Categorico", "Low, Medium, High"],
            ["Action Taken", "Categorico", "Logged, Blocked, Allowed"],
        ]
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════════
    # 15. PRÓXIMOS PASSOS
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("15. Proximos Passos", h1))
    story.append(hr())
    story.append(bullet_list([
        "<b>Banco de dados remoto</b> — Conectar PostgreSQL/MySQL em vez de CSV local",
        "<b>Autenticacao</b> — Login de usuarios no app Streamlit",
        "<b>WhatsApp producao</b> — Numero proprio com API oficial (sem sandbox)",
        "<b>Deploy na nuvem</b> — Railway, Render ou AWS para o app ficar online 24/7",
        "<b>Mais modelos ML</b> — Random Forest, XGBoost, redes neurais",
        "<b>Dashboard automatico</b> — Gerar relatorio completo com um comando",
        "<b>Historico persistente</b> — Salvar conversas em banco de dados",
        "<b>Multi-dataset</b> — Suportar multiplos CSVs simultaneamente",
    ]))

    # ════════════════════════════════════════════════════════════════════════
    # BUILD
    # ════════════════════════════════════════════════════════════════════════
    doc.build(story, onFirstPage=CoverPage.draw, onLaterPages=footer)
    print(f"[OK] PDF gerado: {PDF_PATH}")


# ── README.md ────────────────────────────────────────────────────────────────
def build_readme():
    readme = """# DataChat — Plataforma de Análise Conversacional de Dados

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
"""
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(readme)
    print(f"[OK] README gerado: {README_PATH}")


if __name__ == "__main__":
    build_pdf()
    build_readme()
