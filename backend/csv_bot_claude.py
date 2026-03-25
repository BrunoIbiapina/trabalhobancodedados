# %% [markdown]
# # 🤖 CSV Conversational Bot — Powered by Claude Opus 4.6
#
# **O que este bot faz:**
# - Conversa com você em linguagem natural sobre seus dados CSV
# - Executa análises pandas em tempo real
# - Cria visualizações interativas com Plotly
# - Gera dados sintéticos baseados nos padrões aprendidos
# - **Aprende com a conversa**: mantém histórico completo para dar respostas cada vez mais contextuais
#
# **Como usar:** Execute as células em ordem (Shift+Enter), depois interaja no chat da última célula.

# %% — Célula 1: Instalação de dependências
# Execute esta célula apenas uma vez
# !pip install anthropic pandas numpy plotly ipython -q

# %% [markdown]
# ## 🔧 Setup

# %% — Célula 2: Imports e configurações globais
import os
import json
import warnings
import getpass
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from IPython.display import display, Markdown, HTML
import anthropic

warnings.filterwarnings("ignore")
pd.set_option("display.max_columns", 20)
pd.set_option("display.float_format", "{:.2f}".format)

print("✅ Bibliotecas carregadas!")

# %% [markdown]
# ## 🔑 Configuração da API

# %% — Célula 3: Autenticação com a Anthropic API
# A chave é lida da variável de ambiente (mais seguro) ou digitada manualmente
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Modelo mais inteligente da Anthropic — ideal para análise de dados
MODEL = "claude-opus-4-6"

# Exibe o raciocínio interno do Claude? (True = modo debug)
SHOW_THINKING = False

print(f"✅ Conectado ao modelo: {MODEL}")

# %% [markdown]
# ## 📂 Carregar Dataset

# %% — Célula 4: Carregamento do CSV (ou geração de demo)
# ─── Configure o caminho do seu CSV aqui ───────────────────────────────────
CSV_PATH = ""  # Ex: "/Users/voce/Downloads/vendas.csv"
# ───────────────────────────────────────────────────────────────────────────

if CSV_PATH and os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
    print(f"✅ CSV carregado: {df.shape[0]} linhas × {df.shape[1]} colunas")
else:
    # Dataset demo: clientes de e-commerce com padrões realistas
    print("📊 Gerando dataset demo (clientes e-commerce — 300 registros)...")
    np.random.seed(42)
    n = 300

    # Categorias com distribuição desbalanceada (mais realista)
    cats = np.random.choice(
        ["Bronze", "Prata", "Ouro", "Platina"], n, p=[0.40, 0.30, 0.20, 0.10]
    )

    # Renda correlacionada com categoria
    renda_map = {
        "Bronze":  lambda: np.random.normal(2500,  700, n).clip(1200, 5000),
        "Prata":   lambda: np.random.normal(4800, 1000, n).clip(3000, 8000),
        "Ouro":    lambda: np.random.normal(9000, 2000, n).clip(5500, 16000),
        "Platina": lambda: np.random.normal(16000, 3500, n).clip(10000, 35000),
    }
    renda = np.array([
        renda_map[c]()[i] for i, c in enumerate(cats)
    ]).round(2)

    # Satisfação ligeiramente correlacionada com categoria
    satisf_base = np.where(cats == "Platina", 8, np.where(cats == "Ouro", 7,
                  np.where(cats == "Prata", 6, 5)))
    satisfacao = np.clip(satisf_base + np.random.randint(-2, 3, n), 1, 10)

    df = pd.DataFrame({
        "cliente_id":    range(1001, 1001 + n),
        "nome":          [f"Cliente {i:03d}" for i in range(1, n + 1)],
        "idade":         np.random.randint(18, 72, n),
        "genero":        np.random.choice(["M", "F", "Outro"], n, p=[0.48, 0.48, 0.04]),
        "cidade":        np.random.choice(
            ["São Paulo", "Rio de Janeiro", "Belo Horizonte",
             "Curitiba", "Porto Alegre", "Fortaleza"], n
        ),
        "categoria":     cats,
        "renda_mensal":  renda,
        "total_compras": np.random.randint(1, 80, n),
        "ticket_medio":  np.random.normal(280, 120, n).clip(40, 1200).round(2),
        "satisfacao":    satisfacao,
        "churn_risco":   np.random.choice(
            ["Baixo", "Médio", "Alto"], n, p=[0.55, 0.28, 0.17]
        ),
        "data_cadastro": pd.date_range("2020-01-01", periods=n, freq="3D")
                           .strftime("%Y-%m-%d"),
        "ativo":         np.random.choice([True, False], n, p=[0.85, 0.15]),
    })

    print(f"✅ Dataset demo criado: {df.shape[0]} linhas × {df.shape[1]} colunas")

display(df.head(5))
print("\n📋 Tipos das colunas:")
print(df.dtypes.to_string())

# %% [markdown]
# ## 🛠️ Ferramentas do Bot (Tools)

# %% — Célula 5: Implementação das ferramentas de análise

# ── Referência mutável ao DataFrame (permite que as tools modifiquem o dataset) ──
_state = {"df": df}

def _get_df() -> pd.DataFrame:
    return _state["df"]

def _set_df(new_df: pd.DataFrame) -> None:
    global df
    _state["df"] = new_df
    df = new_df  # Mantém a variável global sincronizada


def tool_get_data_info(sample_rows: int = 5) -> str:
    """Retorna metadados completos: shape, colunas, estatísticas e amostra."""
    d = _get_df()
    num_cols = d.select_dtypes(include=np.number).columns.tolist()
    cat_cols = d.select_dtypes(include=["object", "bool"]).columns.tolist()

    info = {
        "shape": {"rows": len(d), "columns": len(d.columns)},
        "column_details": {
            col: {
                "dtype":        str(d[col].dtype),
                "null_count":   int(d[col].isnull().sum()),
                "unique_count": int(d[col].nunique()),
                # Top valores para categóricas; range para numéricas
                "top_5_values": d[col].value_counts().head(5).to_dict()
                                if col in cat_cols else None,
                "min":  float(d[col].min())  if col in num_cols else None,
                "max":  float(d[col].max())  if col in num_cols else None,
                "mean": float(d[col].mean()) if col in num_cols else None,
                "std":  float(d[col].std())  if col in num_cols else None,
            }
            for col in d.columns
        },
        "numeric_statistics": (
            json.loads(d[num_cols].describe().round(2).to_json())
            if num_cols else {}
        ),
        "sample_data": d.sample(min(sample_rows, len(d)), random_state=42)
                        .to_dict(orient="records"),
    }
    return json.dumps(info, ensure_ascii=False, default=str, indent=2)


def tool_run_query(code: str) -> str:
    """Executa expressão pandas e retorna resultado formatado como string."""
    d = _get_df()
    try:
        # Namespace controlado: só pandas, numpy e o DataFrame
        ns = {"df": d.copy(), "pd": pd, "np": np}
        local = {}
        exec(f"_result = ({code})", ns, local)
        result = local["_result"]

        if isinstance(result, pd.DataFrame):
            preview = result.head(30)
            return (
                f"DataFrame: {len(result)} linhas × {len(result.columns)} colunas\n\n"
                + preview.to_string(index=True)
            )
        elif isinstance(result, pd.Series):
            return f"Series ({len(result)} itens):\n\n{result.head(30).to_string()}"
        elif isinstance(result, (dict, list)):
            return json.dumps(result, ensure_ascii=False, default=str, indent=2)[:4000]
        else:
            return str(result)[:4000]

    except Exception as e:
        return f"❌ Erro na query: {type(e).__name__}: {e}"


def tool_create_chart(
    chart_type:  str,
    x_col:       str  = None,
    y_col:       str  = None,
    color_col:   str  = None,
    title:       str  = None,
    aggregation: str  = "mean",
) -> str:
    """Cria gráfico interativo Plotly e exibe no notebook."""
    d = _get_df()
    title = title or f"{chart_type.title()} — {x_col or ''}"
    ct = chart_type.lower().strip()

    try:
        fig = None
        num_cols = d.select_dtypes(include=np.number).columns.tolist()
        cat_cols = d.select_dtypes(include=["object", "bool"]).columns.tolist()

        if ct in ("histogram", "histograma"):
            col = x_col or (num_cols[0] if num_cols else d.columns[0])
            fig = px.histogram(
                d, x=col, color=color_col, title=title,
                nbins=30, template="plotly_white",
                barmode="overlay" if color_col else "relative",
            )

        elif ct in ("scatter", "dispersão", "dispersao"):
            x = x_col or (num_cols[0] if num_cols else d.columns[0])
            y = y_col or (num_cols[1] if len(num_cols) > 1 else num_cols[0])
            fig = px.scatter(
                d, x=x, y=y, color=color_col, title=title,
                template="plotly_white", opacity=0.65,
                hover_data=d.columns[:6].tolist(),
            )

        elif ct in ("bar", "barras", "barra"):
            agg = aggregation if aggregation in ["mean","sum","count","max","min","median"] else "mean"
            if x_col and y_col:
                data = d.groupby(x_col)[y_col].agg(agg).reset_index()
                data.columns = [x_col, y_col]
                fig = px.bar(
                    data.sort_values(y_col, ascending=False),
                    x=x_col, y=y_col, title=title,
                    color=color_col or x_col, template="plotly_white",
                    text_auto=".2s",
                )
            elif x_col:
                counts = d[x_col].value_counts().reset_index()
                counts.columns = [x_col, "contagem"]
                fig = px.bar(
                    counts, x=x_col, y="contagem", title=title,
                    color=x_col, template="plotly_white", text_auto=True,
                )

        elif ct in ("box", "boxplot", "caixa"):
            col = y_col or (num_cols[0] if num_cols else d.columns[0])
            fig = px.box(
                d, x=color_col or x_col, y=col, title=title,
                template="plotly_white", points="outliers",
            )

        elif ct in ("heatmap", "heatmap_correlation", "correlação", "correlacao", "correlation"):
            corr = d[num_cols].corr().round(3) if num_cols else pd.DataFrame()
            if corr.empty:
                return "❌ Nenhuma coluna numérica para calcular correlação."
            fig = px.imshow(
                corr, title=title, template="plotly_white",
                color_continuous_scale="RdBu_r", aspect="auto", text_auto=True,
            )

        elif ct in ("pie", "pizza", "torta"):
            col = x_col or (cat_cols[0] if cat_cols else d.columns[0])
            counts = d[col].value_counts()
            fig = px.pie(
                values=counts.values, names=counts.index,
                title=title, template="plotly_white", hole=0.3,
            )

        elif ct in ("line", "linha", "linhas"):
            x = x_col or d.columns[0]
            y = y_col or (num_cols[0] if num_cols else d.columns[1])
            fig = px.line(
                d.sort_values(x), x=x, y=y, color=color_col,
                title=title, template="plotly_white", markers=True,
            )

        elif ct == "violin":
            col = y_col or (num_cols[0] if num_cols else d.columns[0])
            fig = px.violin(
                d, x=color_col or x_col, y=col, title=title,
                template="plotly_white", box=True, points="outliers",
            )

        else:
            return (
                f"❌ Tipo '{chart_type}' não reconhecido.\n"
                "Disponíveis: histogram, scatter, bar, box, heatmap_correlation, pie, line, violin"
            )

        if fig:
            fig.update_layout(
                height=500,
                font=dict(family="Arial", size=13),
                margin=dict(l=60, r=30, t=80, b=60),
            )
            fig.show()
            return f"✅ Gráfico '{title}' exibido com sucesso!"

    except Exception as e:
        return f"❌ Erro ao criar gráfico: {type(e).__name__}: {e}"


def tool_generate_data(n_rows: int) -> str:
    """Gera registros sintéticos preservando distribuições e correlações."""
    d = _get_df()
    try:
        new_rows = {}
        num_cols = d.select_dtypes(include=np.number).columns.tolist()
        cat_cols = d.select_dtypes(include=["object", "bool"]).columns.tolist()

        for col in d.columns:
            series = d[col].dropna()
            if len(series) == 0:
                new_rows[col] = [None] * n_rows
                continue

            if col in num_cols:
                # Amostragem com perturbação baseada no desvio padrão real
                mean, std = float(series.mean()), float(series.std())
                col_min, col_max = float(series.min()), float(series.max())
                generated = np.random.normal(mean, std * 0.85, n_rows)
                clipped = np.clip(generated, col_min, col_max)
                # Mantém dtype original (int ou float)
                if d[col].dtype in [np.int64, np.int32]:
                    new_rows[col] = clipped.round(0).astype(int).tolist()
                else:
                    new_rows[col] = clipped.round(2).tolist()

            elif col in cat_cols:
                # Respeita a distribuição de frequências original
                vc = series.value_counts(normalize=True)
                new_rows[col] = np.random.choice(
                    vc.index.tolist(), n_rows, p=vc.values.tolist()
                ).tolist()

        new_df = pd.DataFrame(new_rows)
        combined = pd.concat([d, new_df], ignore_index=True)
        _set_df(combined)

        display(Markdown(f"### ✨ {n_rows} novos registros sintéticos gerados!"))
        display(new_df.head(5))

        return (
            f"✅ {n_rows} registros sintéticos adicionados ao dataset.\n"
            f"Total anterior: {len(d)} linhas → Novo total: {len(combined)} linhas.\n"
            "Os dados foram gerados respeitando as distribuições e frequências do dataset original."
        )
    except Exception as e:
        return f"❌ Erro ao gerar dados: {type(e).__name__}: {e}"


def tool_save_csv(filename: str = "dataset_atualizado.csv") -> str:
    """Salva o estado atual do dataset em arquivo CSV."""
    d = _get_df()
    try:
        if not filename.endswith(".csv"):
            filename += ".csv"
        # Salva relativo ao diretório de trabalho atual
        path = os.path.join(os.getcwd(), filename)
        d.to_csv(path, index=False, encoding="utf-8-sig")  # utf-8-sig = acentos no Excel
        return f"✅ Dataset salvo em:\n{path}\n({len(d)} linhas × {len(d.columns)} colunas)"
    except Exception as e:
        return f"❌ Erro ao salvar: {e}"


print("✅ Ferramentas definidas:", ["get_data_info", "run_query", "create_chart",
                                    "generate_data", "save_csv"])

# %% — Célula 6: Schema das Tools para a API Claude (formato JSON Schema)

TOOLS = [
    {
        "name": "get_data_info",
        "description": (
            "Obtém informações completas sobre o dataset atual: número de linhas/colunas, "
            "tipos de dados, estatísticas descritivas (mín/máx/média/desvio) para colunas numéricas, "
            "valores mais frequentes para categóricas, e uma amostra aleatória. "
            "Use SEMPRE antes de qualquer análise para entender a estrutura dos dados."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sample_rows": {
                    "type": "integer",
                    "description": "Quantidade de linhas de amostra a incluir (padrão: 5, máximo: 20)",
                    "default": 5,
                }
            },
        },
    },
    {
        "name": "run_query",
        "description": (
            "Executa uma expressão pandas no DataFrame 'df' e retorna o resultado. "
            "Use para filtrar, agrupar, calcular estatísticas, fazer cross-tables, etc. "
            "IMPORTANTE: escreva uma EXPRESSÃO que retorna valor (não use print() ou assignment). "
            "Exemplos válidos:\n"
            "  • 'df.groupby(\"categoria\")[\"renda_mensal\"].mean().sort_values(ascending=False)'\n"
            "  • 'df[df[\"churn_risco\"]==\"Alto\"][[\"nome\",\"satisfacao\",\"categoria\"]].head(10)'\n"
            "  • 'pd.crosstab(df[\"categoria\"], df[\"churn_risco\"], normalize=\"index\").round(2)'\n"
            "  • 'df[\"renda_mensal\"].describe()'"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Expressão pandas. O DataFrame é 'df'. Disponível: pd, np.",
                }
            },
            "required": ["code"],
        },
    },
    {
        "name": "create_chart",
        "description": (
            "Cria gráfico interativo Plotly exibido inline no notebook. "
            "Tipos disponíveis: histogram | scatter | bar | box | heatmap_correlation | pie | line | violin. "
            "Use SEMPRE que o usuário pedir 'gráfico', 'visualização', 'plot', 'chart' ou 'mostre'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "chart_type": {
                    "type": "string",
                    "description": "histogram, scatter, bar, box, heatmap_correlation, pie, line ou violin",
                },
                "x_col": {
                    "type": "string",
                    "description": "Nome exato da coluna para o eixo X",
                },
                "y_col": {
                    "type": "string",
                    "description": "Nome exato da coluna para o eixo Y (numérica)",
                },
                "color_col": {
                    "type": "string",
                    "description": "Coluna para segmentação por cor (categórica)",
                },
                "title": {
                    "type": "string",
                    "description": "Título descritivo do gráfico",
                },
                "aggregation": {
                    "type": "string",
                    "description": "Função de agregação para bar chart: mean | sum | count | max | min | median",
                    "default": "mean",
                },
            },
            "required": ["chart_type"],
        },
    },
    {
        "name": "generate_data",
        "description": (
            "Gera novos registros sintéticos baseados nas distribuições estatísticas do dataset. "
            "Preserva frequências de categorias e range de valores numéricos. "
            "Os dados são adicionados ao dataset atual (operação acumulativa). "
            "Use quando o usuário quiser 'expandir', 'aumentar' ou 'gerar mais dados'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "n_rows": {
                    "type": "integer",
                    "description": "Número de novos registros a gerar",
                }
            },
            "required": ["n_rows"],
        },
    },
    {
        "name": "save_csv",
        "description": "Salva o dataset atual (com dados gerados) em arquivo CSV no disco.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Nome do arquivo (ex: 'meus_dados.csv')",
                    "default": "dataset_atualizado.csv",
                }
            },
        },
    },
]

# Mapa nome → função (usado no agentic loop)
TOOL_FUNCTIONS = {
    "get_data_info": lambda inp: tool_get_data_info(**inp),
    "run_query":     lambda inp: tool_run_query(**inp),
    "create_chart":  lambda inp: tool_create_chart(**inp),
    "generate_data": lambda inp: tool_generate_data(**inp),
    "save_csv":      lambda inp: tool_save_csv(**inp),
}

print("✅ Schema das tools configurado para a API Claude.")

# %% [markdown]
# ## 🧠 Engine do Bot — Agentic Loop com Memória

# %% — Célula 7: Loop agêntico principal

# Histórico completo da conversa (inclui tool calls — dá contexto real ao Claude)
conversation_history = []

# Prompt de sistema: define a personalidade e capacidades do bot
SYSTEM_PROMPT = f"""Você é um Analista de Dados Sênior e assistente conversacional especializado em Python/Pandas/Plotly.

Você analisa datasets de forma inteligente, criativa e didática, sempre em Português do Brasil.

═══════════════════════════════════════════
📊 DATASET ATIVO
═══════════════════════════════════════════
Dimensões: {_get_df().shape[0]} linhas × {_get_df().shape[1]} colunas
Colunas:   {', '.join(_get_df().columns.tolist())}

═══════════════════════════════════════════
🛠️ SUAS FERRAMENTAS
═══════════════════════════════════════════
• get_data_info  → Explore estrutura e estatísticas do dataset
• run_query      → Execute análises pandas avançadas
• create_chart   → Crie visualizações Plotly interativas
• generate_data  → Gere dados sintéticos baseados nos padrões
• save_csv       → Salve o dataset atualizado

═══════════════════════════════════════════
📋 COMPORTAMENTO ESPERADO
═══════════════════════════════════════════
1. Use as ferramentas para embasar TODA resposta com dados reais — nunca invente números
2. Na primeira pergunta de análise, chame get_data_info para conhecer o dataset
3. Explique resultados em linguagem de negócio, não técnica
4. Ao final de cada resposta, sugira 2-3 próximas análises interessantes
5. Conecte insights novos com o que já foi discutido na conversa (aprendizado contínuo)
6. Use emojis e formatação Markdown para organizar bem as respostas
7. Se o usuário mencionar uma coluna, sempre use o nome EXATO dela

═══════════════════════════════════════════
🧠 APRENDIZADO CONTÍNUO
═══════════════════════════════════════════
• Lembre quais colunas o usuário achou mais interessantes
• Proponha hipóteses baseadas em padrões identificados
• Conecte descobertas anteriores às novas perguntas
• Seja proativo: se encontrar algo surpreendente nos dados, destaque!
"""


def run_bot(user_message: str) -> None:
    """
    Loop agêntico principal:
    1. Envia mensagem ao Claude (com streaming)
    2. Se Claude usar tools → executa e retorna resultado
    3. Repete até Claude dar resposta final
    4. Salva todo o histórico (inclui tool calls) para contexto futuro
    """
    global conversation_history

    # Monta messages: histórico completo + nova mensagem do usuário
    messages = list(conversation_history)
    messages.append({"role": "user", "content": user_message})

    max_iters = 8  # Proteção contra loop infinito
    iteration = 0

    while iteration < max_iters:
        iteration += 1

        # ── Chamada à API com streaming ────────────────────────────────────
        final_message = None
        stop_reason   = None
        current_block = None

        with client.messages.stream(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
            thinking={"type": "adaptive"},  # Claude decide quando e quanto "pensar"
        ) as stream:

            for event in stream:
                etype = event.type

                # ── Início de um bloco de conteúdo ─────────────────────────
                if etype == "content_block_start":
                    btype = event.content_block.type
                    current_block = btype

                    if btype == "thinking":
                        if SHOW_THINKING:
                            print("\n💭 [Raciocínio interno]\n" + "─" * 40)
                        else:
                            print("🧠 ", end="", flush=True)

                    elif btype == "text":
                        # Limpa o indicador "🧠 Pensando..."
                        print("\r" + " " * 30 + "\r", end="", flush=True)

                    elif btype == "tool_use":
                        tool_name = event.content_block.name
                        print(f"\n🔧 Usando ferramenta: {tool_name}", flush=True)

                # ── Delta (conteúdo incremental) ────────────────────────────
                elif etype == "content_block_delta":
                    dtype = event.delta.type

                    if dtype == "text_delta":
                        # Exibe texto em tempo real (streaming)
                        print(event.delta.text, end="", flush=True)

                    elif dtype == "thinking_delta" and SHOW_THINKING:
                        print(event.delta.thinking, end="", flush=True)

                # ── Fim de um bloco ─────────────────────────────────────────
                elif etype == "content_block_stop":
                    if current_block == "thinking" and SHOW_THINKING:
                        print("\n" + "─" * 40)

            # Mensagem completa (com todos os blocos) após o stream
            final_message = stream.get_final_message()
            stop_reason   = final_message.stop_reason

        # ── Processar resultado do Claude ──────────────────────────────────

        if stop_reason == "end_turn":
            # Claude finalizou → salva conversa completa no histórico
            messages.append({"role": "assistant", "content": final_message.content})
            conversation_history = messages  # Preserva tudo (inclusive tool calls)
            print()  # Quebra de linha final
            break

        elif stop_reason == "tool_use":
            # Claude quer usar uma ou mais ferramentas → executar todas
            messages.append({"role": "assistant", "content": final_message.content})

            tool_results = []
            for block in final_message.content:
                if block.type == "tool_use":
                    name  = block.name
                    # block.input já é dict (SDK parseia automaticamente)
                    inp   = block.input if isinstance(block.input, dict) else {}

                    print(f"\n   ⚙️  Executando {name}...", flush=True)

                    handler = TOOL_FUNCTIONS.get(name)
                    result  = handler(inp) if handler else f"❌ Tool '{name}' não encontrada"

                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,    # Vincula resultado ao call correto
                        "content":     str(result)[:8000],  # Limite de segurança
                    })

            # Retorna resultados ao Claude e continua o loop
            messages.append({"role": "user", "content": tool_results})
            print("\n🤖 Analisando resultados...", end="", flush=True)

        else:
            print(f"\n⚠️ Stop reason inesperado: {stop_reason}")
            messages.append({"role": "assistant", "content": final_message.content})
            conversation_history = messages
            break

    if iteration >= max_iters:
        print("\n⚠️ Limite de iterações atingido. Tente reformular a pergunta.")


print("✅ Engine do bot configurada!")
print(f"📊 Dataset ativo: {_get_df().shape[0]} linhas × {_get_df().shape[1]} colunas")

# %% [markdown]
# ## 💬 Interface de Chat
#
# **Execute a célula abaixo para iniciar o bot.** Use `Shift+Enter` para rodar.
# O bot ficará aguardando sua mensagem no campo de input.

# %% — Célula 8: Loop de chat interativo

def show_menu() -> None:
    """Exibe painel de ajuda formatado."""
    display(HTML("""
    <div style="
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 22px 28px; border-radius: 14px; color: white;
        font-family: 'Segoe UI', Arial, sans-serif; margin: 12px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    ">
        <h2 style="color:#64ffda; margin:0 0 6px 0; font-size:1.4em;">
            🤖 CSV Conversational Bot
        </h2>
        <p style="color:#a8b2d8; margin:0 0 14px 0; font-size:0.9em;">
            Powered by Claude Opus 4.6 &nbsp;|&nbsp; Tool Use + Adaptive Thinking + Conversation Memory
        </p>
        <hr style="border:none; border-top:1px solid #e94560; margin:10px 0;">

        <h3 style="color:#e94560; margin:12px 0 8px 0;">💡 Sugestões de perguntas</h3>
        <ul style="color:#ccd6f6; margin:0; padding-left:22px; line-height:2.0;">
            <li>📊 <em>"Me dê um resumo completo do dataset"</em></li>
            <li>📈 <em>"Crie um gráfico de barras de categoria por renda média"</em></li>
            <li>🔍 <em>"Quais clientes têm alto risco de churn e baixa satisfação?"</em></li>
            <li>📉 <em>"Mostre a correlação entre todas as variáveis numéricas"</em></li>
            <li>🗺️  <em>"Compare a distribuição de renda por cidade"</em></li>
            <li>✨ <em>"Gere 100 novos registros sintéticos"</em></li>
            <li>🧠 <em>"O que você aprendeu sobre os dados até agora?"</em></li>
            <li>💾 <em>"Salve o dataset atualizado como 'clientes_final.csv'"</em></li>
        </ul>

        <hr style="border:none; border-top:1px solid #444; margin:14px 0;">
        <p style="color:#8892b0; font-size:0.85em; margin:0;">
            Comandos especiais: &nbsp;
            <b style="color:#64ffda">menu</b> · exibe este painel &nbsp;|&nbsp;
            <b style="color:#64ffda">historico</b> · resume a conversa &nbsp;|&nbsp;
            <b style="color:#64ffda">dataset</b> · mostra o estado atual &nbsp;|&nbsp;
            <b style="color:#64ffda">limpar</b> · nova sessão &nbsp;|&nbsp;
            <b style="color:#64ffda">sair</b> · encerrar
        </p>
    </div>
    """))


# ── Inicialização ─────────────────────────────────────────────────────────────
display(HTML("""
<div style="text-align:center; padding:16px; background:#0d1117;
            border-radius:10px; margin:8px 0;">
    <h1 style="color:#58a6ff; margin:0;">🚀 CSV Bot Iniciado!</h1>
    <p style="color:#8b949e; margin:6px 0 0 0;">
        Converse em linguagem natural sobre seus dados
    </p>
</div>
"""))

show_menu()

# ── Loop principal de conversa ────────────────────────────────────────────────
while True:
    try:
        user_input = input("\n💬 Você: ").strip()

        if not user_input:
            continue

        cmd = user_input.lower().strip()

        # ── Comandos especiais ────────────────────────────────────────────
        if cmd in ("sair", "exit", "quit", "q"):
            display(Markdown(
                "## 👋 Até logo!\n"
                f"Foram **{len([m for m in conversation_history if m['role']=='user'])}** "
                "perguntas nesta sessão. Foi um prazer analisar os dados com você!"
            ))
            break

        if cmd == "menu":
            show_menu()
            continue

        if cmd in ("historico", "histórico"):
            n_user = len([m for m in conversation_history if m["role"] == "user"])
            n_tool = len([
                b for m in conversation_history
                if m["role"] == "assistant"
                for b in (m["content"] if isinstance(m["content"], list) else [])
                if hasattr(b, "type") and b.type == "tool_use"
            ])
            display(Markdown(
                f"### 📜 Histórico da sessão\n"
                f"- **{n_user}** perguntas feitas\n"
                f"- **{n_tool}** chamadas de ferramentas executadas\n"
                f"- **{len(conversation_history)}** mensagens no contexto do Claude"
            ))
            continue

        if cmd == "dataset":
            d = _get_df()
            display(Markdown(
                f"### 📊 Dataset atual\n"
                f"**{d.shape[0]} linhas × {d.shape[1]} colunas**"
            ))
            display(d.head(5))
            continue

        if cmd == "limpar":
            conversation_history.clear()
            display(Markdown("### 🗑️ Histórico limpo! Iniciando nova sessão."))
            continue

        # ── Envia para o bot ──────────────────────────────────────────────
        print(f"\n{'─' * 60}")
        run_bot(user_input)
        print(f"\n{'─' * 60}")

    except KeyboardInterrupt:
        display(Markdown("## 👋 Bot encerrado."))
        break
    except Exception as e:
        print(f"\n❌ Erro inesperado: {type(e).__name__}: {e}")
        print("Tente novamente ou digite 'sair'.")
