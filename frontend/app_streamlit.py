"""
CSV Conversational Bot — Interface estilo Claude
Powered by Claude Opus 4.6
"""

import os, json, warnings, math
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import streamlit as st
import ollama

warnings.filterwarnings("ignore")

# ── Página ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DataChat",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Matrix Rain ───────────────────────────────────────────────────────────────
import streamlit.components.v1 as _c
_c.html("""
<script>
(function(){
  var canvas = window.parent.document.getElementById('matrix-rain');
  if(canvas) return;
  canvas = window.parent.document.createElement('canvas');
  canvas.id = 'matrix-rain';
  canvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:0;pointer-events:none;opacity:0.13;';
  window.parent.document.body.appendChild(canvas);
  var ctx = canvas.getContext('2d');
  canvas.width = window.parent.innerWidth;
  canvas.height = window.parent.innerHeight;
  var cols = Math.floor(canvas.width / 18);
  var drops = Array(cols).fill(1);
  var chars = 'アイウエオカキクケコ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%&<>/\\|=+-*';
  function draw(){
    ctx.fillStyle = 'rgba(0,0,0,0.05)';
    ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.fillStyle = '#00ff41';
    ctx.font = '14px JetBrains Mono, monospace';
    for(var i=0;i<drops.length;i++){
      var c = chars[Math.floor(Math.random()*chars.length)];
      ctx.fillText(c, i*18, drops[i]*18);
      if(drops[i]*18 > canvas.height && Math.random() > 0.975) drops[i]=0;
      drops[i]++;
    }
  }
  setInterval(draw, 50);
  window.parent.addEventListener('resize', function(){
    canvas.width = window.parent.innerWidth;
    canvas.height = window.parent.innerHeight;
    cols = Math.floor(canvas.width/18);
    drops = Array(cols).fill(1);
  });
})();
</script>
""", height=0)

# ── Design ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700;800&display=swap');

* { -webkit-font-smoothing: antialiased; }
html, body, [class*="css"] { font-family: 'JetBrains Mono', 'Courier New', monospace !important; }
.stApp { background-color: #000000; }
#MainMenu, footer, header { visibility: hidden; }

/* Botão de expandir/colapsar sidebar — sempre visível */
[data-testid="stSidebarCollapsedControl"] button,
button[data-testid="baseButton-headerNoPadding"],
[data-testid="collapsedControl"] {
    background: rgba(0,255,65,0.12) !important;
    border: 1px solid #00ff4150 !important;
    border-radius: 3px !important;
    color: #00ff41 !important;
}
section[data-testid="stSidebarCollapsedControl"] {
    background: #050505 !important;
}

/* ════════════════════════════════════════
   SIDEBAR — Terminal / Hacker
════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background-color: #050505 !important;
    border-right: 1px solid #00ff4125 !important;
}
[data-testid="stSidebar"] > div { padding: 2rem 1.4rem !important; }

.sidebar-logo {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 1.8rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid #00ff4118;
}
.sidebar-logo-icon {
    font-size: 1.1rem; color: #00ff41; font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
}
.sidebar-title {
    font-size: 0.88rem; font-weight: 700;
    color: #00ff41; letter-spacing: 0.04em;
    font-family: 'JetBrains Mono', monospace;
}
.sidebar-sub { font-size: 0.62rem; color: #005c1e; margin-top: 2px; }

.sidebar-section {
    font-size: 0.58rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.12em;
    color: #005c1e; margin: 1.5rem 0 0.5rem 0;
}
.sidebar-section::before { content: "// "; color: #003d14; }

.dataset-badge {
    background: rgba(0,255,65,0.04);
    border: 1px solid #00ff4122;
    border-radius: 3px; padding: 9px 11px;
    font-size: 0.74rem; color: #00cc33;
    margin-bottom: 0.8rem;
    font-family: 'JetBrains Mono', monospace;
}

[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; border: none !important;
    border-radius: 2px !important; color: #00aa28 !important;
    font-size: 0.76rem !important; font-weight: 400 !important;
    font-family: 'JetBrains Mono', monospace !important;
    padding: 5px 8px !important; text-align: left !important;
    width: 100% !important; transition: all 0.1s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(0,255,65,0.07) !important; color: #00ff41 !important;
}
/* Botões de controle — voltar / nova conversa */
[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: rgba(0,255,65,0.08) !important;
    border: 1px solid #00ff4140 !important;
    color: #00ff41 !important;
    margin-bottom: 4px !important;
    padding: 8px 10px !important;
}

.status-pill {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(0,255,65,0.06); border: 1px solid #00ff4122;
    border-radius: 2px; padding: 3px 9px;
    font-size: 0.62rem; color: #00ff41; font-weight: 500;
    font-family: 'JetBrains Mono', monospace;
}
.status-dot {
    width: 5px; height: 5px; background: #00ff41;
    border-radius: 50%; animation: blink 1s step-end infinite;
}
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0;} }

/* File uploader minimalista */
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    border: none !important; background: transparent !important; padding: 0 !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background: transparent !important; border: none !important;
    padding: 0 !important; min-height: unset !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }
[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    background: rgba(0,255,65,0.06) !important;
    border: 1px solid #00ff4125 !important; border-radius: 3px !important;
    color: #00cc33 !important; font-size: 0.74rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    width: 100% !important; padding: 7px 12px !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] button:hover {
    background: rgba(0,255,65,0.12) !important; color: #00ff41 !important;
}

/* Botões de controle no rodapé da sidebar */
[data-testid="stSidebar"] [data-testid="column"] .stButton > button,
[data-testid="stSidebar"] [data-testid="stColumns"] .stButton > button {
    background: rgba(0,255,65,0.06) !important;
    border: 1px solid #00ff4130 !important;
    border-radius: 3px !important;
    color: #00cc33 !important;
    font-size: 0.7rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    padding: 6px 6px !important;
    text-align: center !important;
    transition: all 0.12s !important;
    width: 100% !important;
}
[data-testid="stSidebar"] [data-testid="column"] .stButton > button::before,
[data-testid="stSidebar"] [data-testid="stColumns"] .stButton > button::before {
    content: "" !important;
}
[data-testid="stSidebar"] [data-testid="column"] .stButton > button:hover,
[data-testid="stSidebar"] [data-testid="stColumns"] .stButton > button:hover {
    background: rgba(0,255,65,0.14) !important;
    border-color: #00ff41 !important;
    color: #00ff41 !important;
}

/* Botão voltar fixo */
button[kind="primary"] {
    background: rgba(0,255,65,0.1) !important;
    border: 1px solid #00ff41 !important;
    border-radius: 3px !important;
    color: #00ff41 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.74rem !important;
    padding: 5px 12px !important;
    transition: all 0.12s !important;
    box-shadow: 0 0 12px rgba(0,255,65,0.2) !important;
}
button[kind="primary"]:hover {
    background: rgba(0,255,65,0.2) !important;
    box-shadow: 0 0 20px rgba(0,255,65,0.35) !important;
}

/* ════════════════════════════════════════
   ÁREA PRINCIPAL — Terminal
════════════════════════════════════════ */
.chat-header { text-align: center; padding: 8vh 0 2.5rem 0; }

.chat-header-cmd {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem; color: #005c1e;
    margin-bottom: 1rem; letter-spacing: 0.02em;
}
.chat-header-cmd span { color: #00ff41; }

.chat-header h1 {
    font-size: 2.8rem !important; font-weight: 800 !important;
    color: #ffffff !important; margin: 0 !important;
    letter-spacing: -0.02em !important; line-height: 1.05 !important;
    font-family: 'JetBrains Mono', monospace !important;
    text-shadow: 0 0 40px rgba(0,255,65,0.15) !important;
}
.chat-header h1 span { color: #00ff41; }
.chat-header p {
    color: #3a7a4a; font-size: 0.82rem; margin: 0.8rem 0 0 0;
    font-family: 'JetBrains Mono', monospace; letter-spacing: 0.02em;
}

/* Cursor piscando */
.cursor::after {
    content: "_"; color: #00ff41;
    animation: blink 1s step-end infinite;
}

/* Mensagens */
[data-testid="stChatMessageContent"] { background: transparent !important; }
.stChatMessage p, .stChatMessage li {
    font-size: 0.86rem !important; line-height: 1.8 !important;
    color: #cccccc !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* Input */
[data-testid="stBottom"] > div {
    background: linear-gradient(to top, #000000 75%, transparent) !important;
    padding-bottom: 24px !important;
}
[data-testid="stChatInput"] {
    border: 1px solid #00ff4130 !important; border-radius: 3px !important;
    box-shadow: 0 0 25px rgba(0,255,65,0.06) !important;
    background: #050505 !important;
}
[data-testid="stChatInput"] textarea {
    font-size: 0.86rem !important; color: #00ff41 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #1a4d28 !important; }
[data-testid="stChatInput"] button {
    background: #00ff41 !important; border-radius: 2px !important;
}

/* Cards */
.stMainBlockContainer .stColumns [data-testid="stVerticalBlock"] > .stButton > button {
    background: rgba(0,255,65,0.03) !important;
    border: 1px solid #00ff4125 !important;
    border-radius: 3px !important;
    padding: 16px 14px !important;
    text-align: left !important;
    color: #3a7a4a !important;
    font-size: 0.76rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    min-height: 88px !important;
    transition: all 0.12s !important;
    line-height: 1.6 !important;
}
.stMainBlockContainer .stColumns [data-testid="stVerticalBlock"] > .stButton > button:hover {
    background: rgba(0,255,65,0.08) !important;
    border-color: #00ff41 !important;
    color: #00ff41 !important;
    box-shadow: 0 0 18px rgba(0,255,65,0.12) !important;
}

/* File uploader principal */
[data-testid="stFileUploader"] {
    border: 1px dashed #00ff4125 !important;
    border-radius: 3px !important; background: rgba(0,255,65,0.02) !important;
}

hr { border-color: #00ff4115 !important; }

/* Thinking */
.thinking {
    display: flex; align-items: center; gap: 8px;
    color: #1a4d28; font-size: 0.76rem; padding: 8px 0;
    font-family: 'JetBrains Mono', monospace;
}
.thinking-dots span {
    display: inline-block; width: 5px; height: 5px;
    background: #00ff41; border-radius: 50%;
    animation: bounce 1.2s infinite; margin: 0 2px;
}
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%,60%,100%{transform:translateY(0);} 30%{transform:translateY(-5px);} }

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid #00ff4118 !important;
    background: rgba(0,255,65,0.02) !important;
    border-radius: 3px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Estado da sessão ──────────────────────────────────────────────────────────
for key, val in [
    ("messages", []),
    ("history", []),
    ("df", None),
    ("charts", []),
    ("d3_html", None),
    ("_trigger", None),
]:
    if key not in st.session_state:
        st.session_state[key] = val

# ── Modelo Ollama (local, gratuito) ───────────────────────────────────────────
MODEL = "qwen2.5:7b"   # troque por llama3.1:8b ou mistral se preferir


# ══════════════════════════════════════════════════════════════════════════════
# FERRAMENTAS
# ══════════════════════════════════════════════════════════════════════════════
def get_data_info(sample_rows: int = 5) -> str:
    d = st.session_state.df
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
                "std":  float(d[col].std())  if col in num else None,
            } for col in d.columns
        },
        "stats": json.loads(d[num].describe().round(2).to_json()) if num else {},
        "sample": d.sample(min(sample_rows, len(d)), random_state=42).to_dict(orient="records"),
    }
    return json.dumps(info, ensure_ascii=False, default=str, indent=2)


def run_query(code: str) -> str:
    d = st.session_state.df
    if d is None: return "Nenhum dataset carregado."
    try:
        ns, local = {"df": d.copy(), "pd": pd, "np": np}, {}
        exec(f"_r=({code})", ns, local)
        r = local["_r"]
        if isinstance(r, pd.DataFrame): return f"DataFrame {r.shape}:\n{r.head(30).to_string()}"
        if isinstance(r, pd.Series):    return f"Series ({len(r)}):\n{r.head(30).to_string()}"
        if isinstance(r, (dict,list)):  return json.dumps(r, ensure_ascii=False, default=str)[:4000]
        return str(r)[:4000]
    except Exception as e:
        return f"Erro: {type(e).__name__}: {e}"


def create_chart(chart_type, x_col=None, y_col=None, z_col=None, color_col=None, title=None, aggregation="mean") -> str:
    d = st.session_state.df
    if d is None: return "Nenhum dataset carregado."
    title = title or f"{chart_type} — {x_col or ''}"
    ct = chart_type.lower().strip()
    num = d.select_dtypes(include=np.number).columns.tolist()
    cat = d.select_dtypes(include=["object","bool"]).columns.tolist()
    TEMPLATE = "plotly_white"
    COLORS   = px.colors.qualitative.Set2
    is_3d = False

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
                             template=TEMPLATE, opacity=0.65,
                             hover_data=d.columns[:5].tolist(),
                             color_discrete_sequence=COLORS)

        elif ct in ("scatter3d","scatter_3d","dispersao3d","dispersão3d","3d_scatter"):
            is_3d = True
            x = x_col or (num[0] if num else d.columns[0])
            y = y_col or (num[1] if len(num)>1 else num[0])
            z = z_col or (num[2] if len(num)>2 else num[0])
            fig = px.scatter_3d(d, x=x, y=y, z=z, color=color_col or (cat[0] if cat else None),
                                title=title, template=TEMPLATE, opacity=0.75,
                                hover_data=d.columns[:5].tolist(),
                                color_discrete_sequence=COLORS)
            fig.update_traces(marker=dict(size=4, line=dict(width=0.3, color="#333")))

        elif ct in ("surface","surface3d","superficie","superfície","3d_surface"):
            is_3d = True
            x = x_col or (num[0] if num else d.columns[0])
            y = y_col or (num[1] if len(num)>1 else num[0])
            z = z_col or (num[2] if len(num)>2 else num[0])
            # Cria grid pivotado para superfície
            try:
                pivot = d.pivot_table(values=z, index=y, columns=x, aggfunc="mean")
                fig = go.Figure(data=[go.Surface(
                    z=pivot.values, x=pivot.columns, y=pivot.index,
                    colorscale="Viridis", opacity=0.92,
                    contours=dict(
                        z=dict(show=True, usecolormap=True, highlightcolor="#fff", project_z=True)
                    )
                )])
                fig.update_layout(title=title, scene=dict(
                    xaxis_title=x, yaxis_title=y, zaxis_title=z
                ))
            except Exception:
                # Fallback: surface com dados numéricos diretos
                from scipy.interpolate import griddata
                xi = np.linspace(d[x].min(), d[x].max(), 50)
                yi = np.linspace(d[y].min(), d[y].max(), 50)
                X, Y = np.meshgrid(xi, yi)
                Z = griddata((d[x].values, d[y].values), d[z].values, (X, Y), method="cubic")
                fig = go.Figure(data=[go.Surface(
                    z=Z, x=xi, y=yi,
                    colorscale="Viridis", opacity=0.92,
                    contours=dict(z=dict(show=True, usecolormap=True, highlightcolor="#fff"))
                )])
                fig.update_layout(title=title, scene=dict(
                    xaxis_title=x, yaxis_title=y, zaxis_title=z
                ))

        elif ct in ("bar3d","bar_3d","barras3d","3d_bar"):
            is_3d = True
            x = x_col or (cat[0] if cat else d.columns[0])
            y = y_col or (cat[1] if len(cat)>1 else (cat[0] if cat else d.columns[0]))
            z = z_col or (num[0] if num else d.columns[0])
            agg = aggregation if aggregation in ["mean","sum","count","max","min","median"] else "mean"
            pivot = d.pivot_table(values=z, index=x, columns=y, aggfunc=agg).fillna(0)
            fig = go.Figure()
            colors_3d = px.colors.qualitative.Set2
            for i, col_name in enumerate(pivot.columns):
                fig.add_trace(go.Bar3d(
                    x=[col_name]*len(pivot.index),
                    y=list(pivot.index),
                    z=pivot[col_name].values,
                    name=str(col_name),
                ) if hasattr(go, 'Bar3d') else go.Scatter3d(
                    x=[col_name]*len(pivot.index),
                    y=list(pivot.index),
                    z=pivot[col_name].values,
                    mode="markers",
                    marker=dict(size=pivot[col_name].values / pivot[col_name].max() * 20 + 3,
                                color=colors_3d[i % len(colors_3d)], opacity=0.85,
                                line=dict(width=0.5, color="#333")),
                    name=str(col_name),
                ))
            fig.update_layout(title=title, scene=dict(
                xaxis_title=y, yaxis_title=x, zaxis_title=f"{z} ({agg})"
            ))

        elif ct in ("mesh3d","mesh_3d","malha3d","3d_mesh"):
            is_3d = True
            x = x_col or (num[0] if num else d.columns[0])
            y = y_col or (num[1] if len(num)>1 else num[0])
            z = z_col or (num[2] if len(num)>2 else num[0])
            fig = go.Figure(data=[go.Mesh3d(
                x=d[x], y=d[y], z=d[z],
                opacity=0.6, colorscale="Viridis",
                intensity=d[z], intensitymode="vertex",
                flatshading=True,
            )])
            fig.update_layout(title=title, scene=dict(
                xaxis_title=x, yaxis_title=y, zaxis_title=z
            ))

        elif ct in ("bar","barras","barra"):
            agg = aggregation if aggregation in ["mean","sum","count","max","min","median"] else "mean"
            if x_col and y_col:
                data = d.groupby(x_col)[y_col].agg(agg).reset_index()
                fig = px.bar(data.sort_values(y_col, ascending=False),
                             x=x_col, y=y_col, title=title,
                             color=color_col or x_col, template=TEMPLATE,
                             text_auto=".2s", color_discrete_sequence=COLORS)
            elif x_col:
                counts = d[x_col].value_counts().reset_index()
                counts.columns = [x_col, "contagem"]
                fig = px.bar(counts, x=x_col, y="contagem", title=title,
                             color=x_col, template=TEMPLATE, text_auto=True,
                             color_discrete_sequence=COLORS)

        elif ct in ("box","boxplot"):
            col = y_col or (num[0] if num else d.columns[0])
            fig = px.box(d, x=color_col or x_col, y=col, title=title,
                         template=TEMPLATE, points="outliers",
                         color_discrete_sequence=COLORS)

        elif ct in ("heatmap","heatmap_correlation","correlação","correlacao"):
            corr = d[num].corr().round(3)
            fig = px.imshow(corr, title=title, template=TEMPLATE,
                            color_continuous_scale="RdBu_r", text_auto=True)

        elif ct in ("pie","pizza"):
            col = x_col or (cat[0] if cat else d.columns[0])
            counts = d[col].value_counts()
            fig = px.pie(values=counts.values, names=counts.index, title=title,
                         template=TEMPLATE, hole=0.38,
                         color_discrete_sequence=COLORS)

        elif ct in ("line","linha"):
            x = x_col or d.columns[0]
            y = y_col or (num[0] if num else d.columns[1])
            fig = px.line(d.sort_values(x), x=x, y=y, color=color_col, title=title,
                          template=TEMPLATE, markers=True,
                          color_discrete_sequence=COLORS)

        elif ct == "violin":
            col = y_col or (num[0] if num else d.columns[0])
            fig = px.violin(d, x=color_col or x_col, y=col, title=title,
                            template=TEMPLATE, box=True,
                            color_discrete_sequence=COLORS)
        else:
            return f"Tipo '{chart_type}' não reconhecido. Use: histogram, scatter, bar, box, heatmap_correlation, pie, line, violin, scatter3d, surface3d, bar3d, mesh3d"

        if fig:
            if is_3d:
                fig.update_layout(
                    height=550,
                    font=dict(family="Inter, Arial", size=12, color="#3d3730"),
                    title_font=dict(size=14, color="#1a1a1a", family="Inter"),
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=60, b=10),
                    legend=dict(bgcolor="rgba(0,0,0,0)"),
                    scene=dict(
                        bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(backgroundcolor="rgba(245,240,235,0.4)", gridcolor="#e0d9cf", showbackground=True),
                        yaxis=dict(backgroundcolor="rgba(240,236,228,0.4)", gridcolor="#e0d9cf", showbackground=True),
                        zaxis=dict(backgroundcolor="rgba(235,230,222,0.4)", gridcolor="#e0d9cf", showbackground=True),
                    ),
                )
            else:
                fig.update_layout(
                    height=440,
                    font=dict(family="Inter, Arial", size=12, color="#3d3730"),
                    title_font=dict(size=14, color="#1a1a1a", family="Inter"),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=40, r=20, t=60, b=40),
                    legend=dict(bgcolor="rgba(0,0,0,0)"),
                )
            st.session_state.charts.append(fig)
            return f"✅ Gráfico '{title}' gerado."
    except Exception as e:
        return f"Erro ao criar gráfico: {e}"


def generate_data(n_rows: int) -> str:
    d = st.session_state.df
    if d is None: return "Nenhum dataset carregado."
    try:
        num = d.select_dtypes(include=np.number).columns.tolist()
        cat = d.select_dtypes(include=["object","bool"]).columns.tolist()
        new = {}
        for col in d.columns:
            s = d[col].dropna()
            if col in num:
                m, sd = float(s.mean()), float(s.std())
                gen = np.clip(np.random.normal(m, sd*0.85, n_rows), float(s.min()), float(s.max()))
                new[col] = gen.round(0 if d[col].dtype in [np.int64,np.int32] else 2).tolist()
            elif col in cat:
                vc = s.value_counts(normalize=True)
                new[col] = np.random.choice(vc.index.tolist(), n_rows, p=vc.values.tolist()).tolist()
        st.session_state.df = pd.concat([d, pd.DataFrame(new)], ignore_index=True)
        return f"✅ {n_rows} registros gerados. Total: {len(d)} → {len(st.session_state.df)} linhas."
    except Exception as e:
        return f"Erro: {e}"


def save_csv(filename: str = "dataset_atualizado.csv") -> str:
    d = st.session_state.df
    if d is None: return "Nenhum dataset carregado."
    if not filename.endswith(".csv"): filename += ".csv"
    path = os.path.join(os.path.expanduser("~/Downloads/TrabalhoBD"), filename)
    d.to_csv(path, index=False, encoding="utf-8-sig")
    return f"✅ Salvo em {path} ({len(d)} linhas × {len(d.columns)} colunas)"


def detect_anomalies(column: str, method: str = "iqr") -> str:
    d = st.session_state.df
    if d is None: return "Nenhum dataset carregado."
    if column not in d.columns: return f"Coluna '{column}' não encontrada. Colunas disponíveis: {list(d.columns)}"
    if d[column].dtype not in [np.float64, np.float32, np.int64, np.int32]:
        return f"Coluna '{column}' não é numérica (tipo: {d[column].dtype})."

    s = d[column].dropna()

    if method == "zscore":
        z = np.abs((s - s.mean()) / s.std())
        mask = z > 3
        threshold_info = f"Z-score > 3σ (média={s.mean():.2f}, σ={s.std():.2f})"
    else:  # iqr
        Q1, Q3 = s.quantile(0.25), s.quantile(0.75)
        IQR = Q3 - Q1
        lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        mask = (s < lower) | (s > upper)
        threshold_info = f"IQR: fora de [{lower:.2f}, {upper:.2f}]"

    full_mask = mask.reindex(d.index, fill_value=False)
    anomalies = d[full_mask]
    normal    = d[~full_mask]
    n_anom    = len(anomalies)

    # ── Gráfico com anotações ─────────────────────────────────────────────────
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=normal.index, y=normal[column], mode="markers", name="Normal",
        marker=dict(color="#6b9bd2", size=5, opacity=0.55)
    ))
    if n_anom > 0:
        fig.add_trace(go.Scatter(
            x=anomalies.index, y=anomalies[column], mode="markers", name="⚠️ Anomalia",
            marker=dict(color="#e05c5c", size=9, symbol="x",
                        line=dict(width=2, color="#c93030"))
        ))
        # Anota os 5 valores mais extremos
        top = anomalies.nlargest(min(5, n_anom), column)
        for idx, row in top.iterrows():
            fig.add_annotation(
                x=idx, y=row[column],
                text=f"<b>{row[column]:.1f}</b>",
                showarrow=True, arrowhead=2, arrowcolor="#c93030",
                font=dict(size=10, color="#c93030"),
                bgcolor="white", bordercolor="#e05c5c", borderwidth=1,
                ax=0, ay=-36
            )

    fig.update_layout(
        title=f"Anomalias — '{column}' ({method.upper()})  ·  {n_anom} detectadas  ·  {threshold_info}",
        height=430,
        font=dict(family="Inter, Arial", size=12, color="#3d3730"),
        title_font=dict(size=13, color="#1a1a1a", family="Inter"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=65, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=True, gridcolor="#f0ece4"),
        yaxis=dict(showgrid=True, gridcolor="#f0ece4"),
    )
    st.session_state.charts.append(fig)

    result = {
        "column": column, "method": method, "threshold": threshold_info,
        "n_anomalies": n_anom,
        "pct_anomalies": round(n_anom / len(d) * 100, 2),
        "anomaly_stats": anomalies[column].describe().round(2).to_dict() if n_anom > 0 else {},
        "top_anomalies": anomalies[[column]].head(10).to_dict(orient="records"),
    }
    return json.dumps(result, ensure_ascii=False, default=str, indent=2)


# ── Visualizações com Grafos (Nós interativos) ──────────────────────────────

def create_correlation_network(threshold: float = 0.02) -> str:
    """Cria rede D3.js interativa de correlações com nós arrastáveis."""
    d = st.session_state.df
    if d is None: return "Nenhum dataset carregado."
    num = d.select_dtypes(include=np.number).columns.tolist()
    if len(num) < 2: return "Precisa de pelo menos 2 colunas numéricas."

    corr = d[num].corr()
    colors = ["#c96442","#4a7fb5","#2c8c6f","#e8a87c","#9b59b6","#e05c5c",
              "#f39c12","#1abc9c","#3498db","#e74c3c"]

    nodes_data = []
    for i, col in enumerate(num):
        nodes_data.append({"id": col, "color": colors[i % len(colors)], "mean": round(float(d[col].mean()), 2), "std": round(float(d[col].std()), 2)})

    links_data = []
    edges_info = []
    for i in range(len(num)):
        for j in range(i + 1, len(num)):
            r = float(corr.iloc[i, j])
            if abs(r) >= threshold:
                links_data.append({"source": num[i], "target": num[j], "value": round(r, 4)})
                edges_info.append((num[i], num[j], r))

    graph_json = json.dumps({"nodes": nodes_data, "links": links_data}, ensure_ascii=False)
    uid = f"corr_{abs(hash(str(num)))}"

    html = f"""
    <div id="{uid}" style="width:100%;height:580px;background:transparent;border-radius:12px;overflow:hidden;">
        <div style="text-align:center;padding:10px 0 0 0;font-family:Inter,sans-serif;font-size:15px;font-weight:600;color:#2c2c2c;">
            Rede de Correlações entre Variáveis
        </div>
        <div style="text-align:center;font-family:Inter,sans-serif;font-size:11px;color:#8a7f72;margin-bottom:5px;">
            Arraste os nós · Linhas vermelhas = positiva · Azuis = negativa · Espessura = força
        </div>
    </div>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script>
    (function() {{
        const data = {graph_json};
        const container = document.getElementById("{uid}");
        const width = container.offsetWidth;
        const height = 530;

        const svg = d3.select("#{uid}").append("svg").attr("width", width).attr("height", height);

        const defs = svg.append("defs");
        defs.append("filter").attr("id","glow_{uid}")
            .append("feDropShadow").attr("dx",0).attr("dy",2).attr("stdDeviation",4).attr("flood-opacity",0.2);

        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(120))
            .force("charge", d3.forceManyBody().strength(-350))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(45));

        // Links
        const link = svg.append("g").selectAll("line")
            .data(data.links).enter().append("line")
            .attr("stroke", d => d.value > 0 ? "#c96442" : "#4a7fb5")
            .attr("stroke-width", d => Math.max(1.5, Math.abs(d.value) * 8))
            .attr("stroke-opacity", d => 0.3 + Math.abs(d.value) * 0.6);

        // Link labels
        const linkLabel = svg.append("g").selectAll("text")
            .data(data.links).enter().append("text")
            .text(d => d.value.toFixed(3))
            .attr("font-family", "Inter, sans-serif")
            .attr("font-size", "9px")
            .attr("fill", "#8a7f72")
            .attr("text-anchor", "middle")
            .attr("dy", -4);

        // Node groups
        const node = svg.append("g").selectAll("g")
            .data(data.nodes).enter().append("g")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        // Circle
        node.append("circle")
            .attr("r", 28)
            .attr("fill", d => d.color)
            .attr("stroke", "white").attr("stroke-width", 3)
            .attr("filter", "url(#glow_{uid})")
            .attr("cursor", "grab")
            .style("opacity", 0)
            .transition().duration(600).delay((d, i) => i * 80)
            .style("opacity", 0.9);

        // Label above
        node.append("text")
            .text(d => d.id)
            .attr("text-anchor", "middle")
            .attr("dy", -35)
            .attr("font-family", "Inter, sans-serif")
            .attr("font-size", "11px")
            .attr("font-weight", "600")
            .attr("fill", "#2c2c2c")
            .style("pointer-events", "none");

        // Stats inside
        node.append("text")
            .text(d => "μ " + d.mean)
            .attr("text-anchor", "middle")
            .attr("dy", 0)
            .attr("font-family", "Inter, sans-serif")
            .attr("font-size", "8px")
            .attr("font-weight", "500")
            .attr("fill", "white")
            .style("pointer-events", "none");

        node.append("text")
            .text(d => "σ " + d.std)
            .attr("text-anchor", "middle")
            .attr("dy", 12)
            .attr("font-family", "Inter, sans-serif")
            .attr("font-size", "8px")
            .attr("fill", "rgba(255,255,255,0.7)")
            .style("pointer-events", "none");

        simulation.on("tick", () => {{
            link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
            linkLabel.attr("x", d => (d.source.x + d.target.x) / 2)
                     .attr("y", d => (d.source.y + d.target.y) / 2);
            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});

        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x; d.fy = d.y;
            d3.select(this).select("circle").attr("cursor", "grabbing");
        }}
        function dragged(event, d) {{ d.fx = event.x; d.fy = event.y; }}
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null; d.fy = null;
            d3.select(this).select("circle").attr("cursor", "grab");
        }}
    }})();
    </script>
    """
    st.session_state.d3_html = html

    strong = [(n1, n2, r) for n1, n2, r in edges_info if abs(r) > 0.3]
    result = {
        "total_variaveis": len(num),
        "total_conexoes": len(edges_info),
        "correlacoes_fortes": [{"var1": n1, "var2": n2, "r": round(r, 3)} for n1, n2, r in strong],
        "tipo": "rede_interativa_d3",
    }
    return json.dumps(result, ensure_ascii=False, default=str, indent=2)


def create_analysis_flow(analysis_type: str = "completa") -> str:
    """Cria grafo D3.js do fluxo de análise com nós arrastáveis."""
    d = st.session_state.df
    if d is None: return "Nenhum dataset carregado."

    num = d.select_dtypes(include=np.number).columns.tolist()
    cat = d.select_dtypes(include=["object", "bool"]).columns.tolist()
    n_rows, n_cols = d.shape
    n_nulls = int(d.isnull().sum().sum())
    n_dupes = int(d.duplicated().sum())

    nodes_data = [
        {"id": "Dataset", "info": f"{n_rows:,} linhas x {n_cols} colunas", "color": "#c96442", "size": 42, "level": 0},
        {"id": "Qualidade", "info": f"Nulos: {n_nulls} | Dupl: {n_dupes}", "color": "#e8a87c", "size": 30, "level": 1},
        {"id": "Numericas", "info": f"{len(num)} colunas", "color": "#4a7fb5", "size": 30, "level": 1},
        {"id": "Categoricas", "info": f"{len(cat)} colunas", "color": "#6b9bd2", "size": 30, "level": 1},
    ]
    links_data = [
        {"source": "Dataset", "target": "Qualidade"},
        {"source": "Dataset", "target": "Numericas"},
        {"source": "Dataset", "target": "Categoricas"},
    ]

    insights = []
    if n_nulls == 0: insights.append("Sem dados faltantes")

    if len(num) >= 2:
        top_corr = d[num].corr().abs()
        np.fill_diagonal(top_corr.values, 0)
        max_corr = float(top_corr.max().max())
        max_pair = top_corr.stack().idxmax()
        nodes_data.append({"id": "Correlacoes", "info": f"Max: {max_pair[0]} x {max_pair[1]} ({max_corr:.2f})", "color": "#c96442", "size": 28, "level": 2})
        links_data.append({"source": "Numericas", "target": "Correlacoes"})
        if max_corr > 0.7: insights.append(f"Correlacao forte ({max_corr:.2f})")

    if num:
        total_outliers = 0
        n_cols_out = 0
        for col in num[:5]:
            Q1, Q3 = d[col].quantile(0.25), d[col].quantile(0.75)
            IQR = Q3 - Q1
            n_out = int(((d[col] < Q1 - 1.5 * IQR) | (d[col] > Q3 + 1.5 * IQR)).sum())
            if n_out > 0: n_cols_out += 1; total_outliers += n_out
        nodes_data.append({"id": "Anomalias", "info": f"{total_outliers} outliers em {n_cols_out} cols", "color": "#e05c5c", "size": 28, "level": 2})
        links_data.append({"source": "Numericas", "target": "Anomalias"})
        if total_outliers > 0: insights.append(f"{total_outliers} anomalias")

    if cat:
        n_unique = d[cat[0]].nunique()
        nodes_data.append({"id": "Distribuicao", "info": f"{cat[0]}: {n_unique} categorias", "color": "#9b59b6", "size": 28, "level": 2})
        links_data.append({"source": "Categoricas", "target": "Distribuicao"})

    insight_text = " | ".join(insights) if insights else "Dataset limpo"
    nodes_data.append({"id": "Insights", "info": insight_text, "color": "#2c8c6f", "size": 38, "level": 3})

    for n in nodes_data:
        if n["level"] == 2:
            links_data.append({"source": n["id"], "target": "Insights"})
    links_data.append({"source": "Qualidade", "target": "Insights"})

    graph_json = json.dumps({"nodes": nodes_data, "links": links_data}, ensure_ascii=False)
    uid = f"flow_{abs(hash(str(n_rows)))}"

    html = f"""
    <div id="{uid}" style="width:100%;height:580px;background:transparent;border-radius:12px;overflow:hidden;">
        <div style="text-align:center;padding:10px 0 0 0;font-family:Inter,sans-serif;font-size:15px;font-weight:600;color:#2c2c2c;">
            Fluxo de Análise dos Dados
        </div>
        <div style="text-align:center;font-family:Inter,sans-serif;font-size:11px;color:#8a7f72;margin-bottom:5px;">
            Arraste os nós para explorar o fluxo
        </div>
    </div>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script>
    (function() {{
        const data = {graph_json};
        const container = document.getElementById("{uid}");
        const width = container.offsetWidth;
        const height = 530;
        const svg = d3.select("#{uid}").append("svg").attr("width", width).attr("height", height);

        const defs = svg.append("defs");
        defs.append("filter").attr("id","sh_{uid}")
            .append("feDropShadow").attr("dx",0).attr("dy",2).attr("stdDeviation",3).attr("flood-opacity",0.15);

        // Arrow marker
        defs.append("marker").attr("id","arrow_{uid}").attr("viewBox","0 0 10 10")
            .attr("refX",25).attr("refY",5).attr("markerWidth",6).attr("markerHeight",6)
            .attr("orient","auto").append("path").attr("d","M0,0 L10,5 L0,10 Z").attr("fill","#c4bab0");

        // Force with X positioning by level
        const xScale = d3.scaleLinear().domain([0, 3]).range([80, width - 80]);
        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("x", d3.forceX(d => xScale(d.level)).strength(0.7))
            .force("y", d3.forceY(height / 2).strength(0.1))
            .force("collision", d3.forceCollide().radius(d => d.size + 10));

        const link = svg.append("g").selectAll("line")
            .data(data.links).enter().append("line")
            .attr("stroke", "#c4bab0").attr("stroke-width", 2)
            .attr("marker-end", "url(#arrow_{uid})");

        const node = svg.append("g").selectAll("g")
            .data(data.nodes).enter().append("g")
            .call(d3.drag().on("start", ds).on("drag", dr).on("end", de));

        node.append("circle")
            .attr("r", d => d.size)
            .attr("fill", d => d.color)
            .attr("stroke", "white").attr("stroke-width", 2.5)
            .attr("filter", "url(#sh_{uid})")
            .attr("cursor", "grab")
            .style("opacity", 0)
            .transition().duration(700).delay((d, i) => i * 120)
            .style("opacity", 0.9);

        node.append("text")
            .text(d => d.id)
            .attr("text-anchor", "middle").attr("dy", -d => d.size - 8)
            .attr("font-family", "Inter, sans-serif")
            .attr("font-size", d => d.level === 0 ? "13px" : "11px")
            .attr("font-weight", "600").attr("fill", "#2c2c2c")
            .style("pointer-events", "none");

        node.append("text")
            .text(d => d.id)
            .attr("text-anchor", "middle")
            .attr("dy", d => -(d.size + 8))
            .attr("font-family", "Inter, sans-serif")
            .attr("font-size", d => d.level === 0 ? "12px" : "10px")
            .attr("font-weight", "600").attr("fill", "#2c2c2c")
            .style("pointer-events", "none");

        // Info inside
        node.append("text")
            .text(d => d.info.length > 20 ? d.info.substring(0, 18) + "..." : d.info)
            .attr("text-anchor", "middle").attr("dy", 4)
            .attr("font-family", "Inter, sans-serif")
            .attr("font-size", "7.5px").attr("fill", "white")
            .style("pointer-events", "none");

        simulation.on("tick", () => {{
            link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});

        function ds(e, d) {{ if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }}
        function dr(e, d) {{ d.fx = e.x; d.fy = e.y; }}
        function de(e, d) {{ if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }}
    }})();
    </script>
    """
    st.session_state.d3_html = html

    return json.dumps({
        "etapas": len(nodes_data), "conexoes": len(links_data),
        "insights": insights,
        "tipo": "fluxo_interativo_d3",
    }, ensure_ascii=False, default=str, indent=2)


def create_category_tree(column: str = None, value_col: str = None) -> str:
    """Cria árvore interativa D3.js com nós arrastáveis e animações de física."""
    d = st.session_state.df
    if d is None: return "Nenhum dataset carregado."
    cat_cols = d.select_dtypes(include=["object", "bool"]).columns.tolist()
    num_cols = d.select_dtypes(include=np.number).columns.tolist()

    if not cat_cols: return "Nenhuma coluna categórica encontrada."
    col = column or cat_cols[0]
    if col not in d.columns: return f"Coluna '{col}' não encontrada."

    vcol = value_col or (num_cols[0] if num_cols else None)
    counts = d[col].value_counts().head(12)
    total = len(d)

    colors = ["#c96442","#e8a87c","#4a7fb5","#6b9bd2","#2c8c6f","#e05c5c",
              "#9b59b6","#f39c12","#1abc9c","#e74c3c","#3498db","#2ecc71"]

    # Montar dados JSON para D3
    nodes_data = [{"id": str(col), "label": str(col), "count": total, "pct": 100, "isRoot": True, "color": "#c96442"}]
    links_data = []
    for i, (cat_val, count) in enumerate(counts.items()):
        pct = round(count / total * 100, 1)
        node_info = {"id": str(cat_val), "label": str(cat_val), "count": int(count), "pct": pct, "isRoot": False, "color": colors[i % len(colors)]}
        if vcol:
            sub = d[d[col] == cat_val]
            node_info["avg"] = round(float(sub[vcol].mean()), 2)
            node_info["value_col"] = vcol
        nodes_data.append(node_info)
        links_data.append({"source": str(col), "target": str(cat_val)})

    graph_json = json.dumps({"nodes": nodes_data, "links": links_data}, ensure_ascii=False)
    uid = f"tree_{abs(hash(col))}"

    html = f"""
    <div id="{uid}" style="width:100%;height:580px;background:transparent;border-radius:12px;overflow:hidden;position:relative;">
        <div style="text-align:center;padding:10px 0 0 0;font-family:Inter,sans-serif;font-size:15px;font-weight:600;color:#2c2c2c;">
            Árvore de Categorias — {col}
        </div>
        <div style="text-align:center;font-family:Inter,sans-serif;font-size:11px;color:#8a7f72;margin-bottom:5px;">
            Arraste os nós para mover
        </div>
    </div>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script>
    (function() {{
        const data = {graph_json};
        const container = document.getElementById("{uid}");
        const width = container.offsetWidth;
        const height = 530;

        const svg = d3.select("#{uid}")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        // Seta gradiente
        const defs = svg.append("defs");
        defs.append("filter").attr("id","shadow_{uid}")
            .append("feDropShadow").attr("dx",0).attr("dy",2).attr("stdDeviation",3).attr("flood-opacity",0.15);

        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(130))
            .force("charge", d3.forceManyBody().strength(-400))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(d => d.isRoot ? 50 : 35));

        // Links
        const link = svg.append("g").selectAll("line")
            .data(data.links).enter().append("line")
            .attr("stroke", "#d6cfc5").attr("stroke-width", 2.5)
            .attr("stroke-opacity", 0.6);

        // Node groups
        const node = svg.append("g").selectAll("g")
            .data(data.nodes).enter().append("g")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        // Circle
        node.append("circle")
            .attr("r", d => d.isRoot ? 38 : 18 + d.pct * 0.5)
            .attr("fill", d => d.color)
            .attr("stroke", "white").attr("stroke-width", 2.5)
            .attr("filter", "url(#shadow_{uid})")
            .attr("cursor", "grab")
            .style("opacity", 0)
            .transition().duration(800).delay((d, i) => i * 100)
            .style("opacity", 0.9);

        // Label
        node.append("text")
            .text(d => d.label)
            .attr("text-anchor", "middle")
            .attr("dy", d => d.isRoot ? -45 : -(22 + d.pct * 0.5))
            .attr("font-family", "Inter, sans-serif")
            .attr("font-size", d => d.isRoot ? "13px" : "11px")
            .attr("font-weight", d => d.isRoot ? "700" : "500")
            .attr("fill", "#2c2c2c")
            .style("pointer-events", "none");

        // Count inside circle
        node.append("text")
            .text(d => d.isRoot ? d.count.toLocaleString() : d.pct + "%")
            .attr("text-anchor", "middle")
            .attr("dy", d => d.isRoot ? 5 : 4)
            .attr("font-family", "Inter, sans-serif")
            .attr("font-size", d => d.isRoot ? "12px" : "9px")
            .attr("font-weight", "600")
            .attr("fill", "white")
            .style("pointer-events", "none");

        // Tooltip (count below)
        node.filter(d => !d.isRoot).append("text")
            .text(d => {{
                let t = d.count.toLocaleString() + " registros";
                if (d.avg !== undefined) t += " | " + d.value_col + ": " + d.avg;
                return t;
            }})
            .attr("text-anchor", "middle")
            .attr("dy", d => 22 + d.pct * 0.5 + 14)
            .attr("font-family", "Inter, sans-serif")
            .attr("font-size", "9px")
            .attr("fill", "#8a7f72")
            .style("pointer-events", "none");

        simulation.on("tick", () => {{
            link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});

        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x; d.fy = d.y;
            d3.select(this).select("circle").attr("cursor", "grabbing");
        }}
        function dragged(event, d) {{
            d.fx = event.x; d.fy = event.y;
        }}
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null; d.fy = null;
            d3.select(this).select("circle").attr("cursor", "grab");
        }}
    }})();
    </script>
    """
    # Usar st.components.v1.html para renderizar D3
    st.session_state.d3_html = html

    result = {
        "coluna": col, "total_categorias": len(counts),
        "top_categorias": {str(k): int(v) for k, v in counts.items()},
        "tipo": "arvore_interativa_d3",
    }
    if vcol:
        result["valor_agregado"] = vcol
        result["media_por_categoria"] = {str(k): round(float(v), 2) for k, v in d.groupby(col)[vcol].mean().items() if str(k) in [str(c) for c in counts.index]}
    return json.dumps(result, ensure_ascii=False, default=str, indent=2)


TOOLS = [
    {"name":"get_data_info","description":"Obtém shape, colunas, tipos, estatísticas e amostra do dataset. Use antes de qualquer análise.","input_schema":{"type":"object","properties":{"sample_rows":{"type":"integer","default":5}}}},
    {"name":"run_query","description":"Executa expressão pandas no DataFrame 'df'. Exemplos: 'df.groupby(\"categoria\")[\"renda_mensal\"].mean()' | 'df[df[\"satisfacao\"]<5].shape[0]'","input_schema":{"type":"object","properties":{"code":{"type":"string"}},"required":["code"]}},
    {"name":"create_chart","description":"Cria gráfico Plotly interativo. Tipos 2D: histogram, scatter, bar, box, heatmap_correlation, pie, line, violin. Tipos 3D (interativos, rotacionáveis): scatter3d (dispersão 3D com 3 variáveis numéricas), surface3d (superfície 3D interpolada), bar3d (barras 3D categórico×categórico×numérico), mesh3d (malha 3D). Use scatter3d/surface3d quando pedirem visualização 3D, gráfico tridimensional ou relação entre 3 variáveis.","input_schema":{"type":"object","properties":{"chart_type":{"type":"string"},"x_col":{"type":"string"},"y_col":{"type":"string"},"z_col":{"type":"string","description":"Terceira coluna (eixo Z) para gráficos 3D"},"color_col":{"type":"string"},"title":{"type":"string"},"aggregation":{"type":"string","default":"mean"}},"required":["chart_type"]}},
    {"name":"detect_anomalies","description":"Detecta anomalias em uma coluna numérica usando IQR ou Z-score e gera gráfico com pontos destacados e anotações. Use quando pedirem anomalias, outliers, valores extremos ou comportamentos fora do padrão.","input_schema":{"type":"object","properties":{"column":{"type":"string","description":"Nome da coluna numérica"},"method":{"type":"string","enum":["iqr","zscore"],"default":"iqr","description":"iqr=robusto para qualquer distribuição; zscore=para distribuições normais"}},"required":["column"]}},
    {"name":"generate_data","description":"Gera registros sintéticos baseados nos padrões do dataset.","input_schema":{"type":"object","properties":{"n_rows":{"type":"integer"}},"required":["n_rows"]}},
    {"name":"save_csv","description":"Salva o dataset em CSV.","input_schema":{"type":"object","properties":{"filename":{"type":"string","default":"dataset_atualizado.csv"}}}},
    {"name":"create_correlation_network","description":"Cria grafo interativo (rede de nós) mostrando correlações entre variáveis numéricas. Nós = variáveis, arestas = correlações. Ideal para visualizar relações complexas. Use quando pedirem: rede de correlações, mapa de variáveis, grafo, network, relação entre variáveis, nós conectados.","input_schema":{"type":"object","properties":{"threshold":{"type":"number","default":0.3,"description":"Correlação mínima para mostrar conexão (0-1)"}}}},
    {"name":"create_analysis_flow","description":"Cria grafo visual do fluxo de análise dos dados — mostra as etapas (Dataset → Qualidade → Numéricas → Correlações → Anomalias → Insights) como nós conectados. Ideal para dar uma visão geral inteligente dos dados. Use quando pedirem: fluxo de análise, visão geral, mapa dos dados, raciocínio da análise, árvore de análise.","input_schema":{"type":"object","properties":{"analysis_type":{"type":"string","default":"completa"}}}},
    {"name":"create_category_tree","description":"Cria árvore hierárquica interativa (nós radiais) mostrando categorias e seus valores. Nó central = coluna, ramos = categorias com contagem e percentual. Use quando pedirem: árvore de categorias, distribuição visual, mapa de categorias, árvore com nós.","input_schema":{"type":"object","properties":{"column":{"type":"string","description":"Coluna categórica para a árvore"},"value_col":{"type":"string","description":"Coluna numérica para agregar valores por categoria"}}}},
]
TOOL_FNS = {
    "get_data_info":    lambda i: get_data_info(**i),
    "run_query":        lambda i: run_query(**i),
    "create_chart":     lambda i: create_chart(**i),
    "detect_anomalies": lambda i: detect_anomalies(**i),
    "generate_data":    lambda i: generate_data(**i),
    "save_csv":         lambda i: save_csv(**i),
    "create_correlation_network": lambda i: create_correlation_network(**i),
    "create_analysis_flow":       lambda i: create_analysis_flow(**i),
    "create_category_tree":       lambda i: create_category_tree(**i),
}

# Converte TOOLS do formato Anthropic para o formato Ollama/OpenAI
TOOLS_OLLAMA = [
    {
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t["description"],
            "parameters": t.get("input_schema", {"type": "object", "properties": {}}),
        },
    }
    for t in TOOLS
]


def get_system() -> str:
    d = st.session_state.df
    if d is not None:
        num = d.select_dtypes(include=np.number).columns.tolist()
        cat = d.select_dtypes(include=["object","bool"]).columns.tolist()
        context = f"""Dataset ativo: {len(d)} linhas × {len(d.columns)} colunas
Todas as colunas: {", ".join(d.columns.tolist())}
Colunas numéricas: {", ".join(num) if num else "nenhuma"}
Colunas categóricas: {", ".join(cat) if cat else "nenhuma"}"""
    else:
        context = "Nenhum dataset carregado ainda."

    return f"""Você é um Analista de Dados Sênior chamado DataChat. Responda sempre em Português do Brasil.
Você é conversacional, simpático e natural — como um colega de trabalho experiente.

{context}

COMPORTAMENTO CONVERSACIONAL (MUITO IMPORTANTE):
- Você CONVERSA antes de agir. Nunca execute análises ou gere gráficos sem antes entender o que o usuário quer.
- Se o usuário perguntar "você consegue fazer X?" ou "dá pra fazer Y?", responda que SIM e pergunte detalhes: quais colunas, que tipo de visualização, etc. NÃO execute imediatamente.
- Se o usuário pedir algo vago como "me mostra algo interessante" ou "analisa os dados", aí sim você pode tomar iniciativa e executar.
- Se o usuário pedir algo específico e claro como "faz um gráfico de barras de vendas por região", execute direto sem perguntar.
- Resumindo: perguntas genéricas → converse. Pedidos claros → execute.
- Cumprimentos como "oi", "olá", "bom dia" → responda naturalmente, pergunte como pode ajudar. NÃO execute ferramentas.

FERRAMENTAS (use quando for executar de fato):
- get_data_info: conhecer o dataset (chame antes da primeira análise real)
- run_query: consultas pandas
- create_chart: visualizações 2D (histogram, scatter, bar, box, heatmap_correlation, pie, line, violin) e 3D interativas (scatter3d, surface3d, bar3d, mesh3d)
- detect_anomalies: outliers com gráfico anotado (method: iqr ou zscore)
- create_correlation_network: grafo interativo de correlações (nós = variáveis, arestas = correlações)
- create_analysis_flow: mapa visual do fluxo de análise com nós conectados (Dataset → Qualidade → Insights)
- create_category_tree: árvore radial interativa de categorias (nó central + ramos)
- generate_data: gerar registros sintéticos
- save_csv: salvar dataset

REGRAS:
- Trabalhe EXCLUSIVAMENTE com colunas reais do dataset — nunca invente
- Adapte linguagem ao domínio dos dados
- Explique resultados de forma clara
- Conecte insights de mensagens anteriores
- Seja conciso e use markdown para organizar
- Ao final de uma análise, sugira 1-2 próximos passos relevantes"""


TOOL_LABELS = {
    "get_data_info":    "📋 Lendo estrutura do dataset…",
    "run_query":        "🔍 Executando consulta…",
    "create_chart":     "📊 Gerando visualização…",
    "detect_anomalies": "🔬 Detectando anomalias…",
    "generate_data":    "🎲 Gerando dados sintéticos…",
    "save_csv":         "💾 Salvando CSV…",
    "create_correlation_network": "🕸️ Criando rede de correlações…",
    "create_analysis_flow":       "🧠 Mapeando fluxo de análise…",
    "create_category_tree":       "🌳 Construindo árvore de categorias…",
}


def run_agent_streaming(user_msg: str, text_ph, status_ph) -> str:
    # Monta histórico com system prompt na frente
    messages = [{"role": "system", "content": get_system()}]
    messages += [m for m in st.session_state.history if m["role"] != "system"]
    messages.append({"role": "user", "content": user_msg})
    final_text = ""

    for iteration in range(8):
        status_ph.markdown(
            '<div class="thinking"><div class="thinking-dots">'
            '<span></span><span></span><span></span></div>'
            '&nbsp;⚙️ Pensando…</div>',
            unsafe_allow_html=True,
        )

        try:
            resp = ollama.chat(
                model=MODEL,
                messages=messages,
                tools=TOOLS_OLLAMA,
                stream=False,
            )
        except Exception as e:
            status_ph.empty()
            text_ph.markdown(f"❌ Erro ao conectar ao Ollama: `{e}`\n\n"
                             "Verifique se o Ollama está rodando (`ollama serve`) "
                             f"e o modelo baixado (`ollama pull {MODEL}`).")
            return str(e)

        status_ph.empty()
        msg = resp.message

        # Adiciona resposta do assistente no histórico
        assistant_entry: dict = {"role": "assistant", "content": msg.content or ""}
        if msg.tool_calls:
            assistant_entry["tool_calls"] = msg.tool_calls
        messages.append(assistant_entry)

        # Sem chamadas de ferramentas → resposta final
        if not msg.tool_calls:
            final_text = msg.content or ""
            text_ph.markdown(final_text)
            break

        # Executa cada ferramenta chamada
        for tc in msg.tool_calls:
            name = tc.function.name
            args = tc.function.arguments if isinstance(tc.function.arguments, dict) else {}
            label = TOOL_LABELS.get(name, f"⚙️ {name}…")
            status_ph.markdown(
                f'<div class="thinking"><div class="thinking-dots">'
                f'<span></span><span></span><span></span></div>'
                f'&nbsp;{label}</div>',
                unsafe_allow_html=True,
            )
            text_ph.empty()
            fn  = TOOL_FNS.get(name)
            res = fn(args) if fn else f"Ferramenta '{name}' não encontrada."
            messages.append({"role": "tool", "content": str(res)[:8000]})

    # Salva histórico sem o system prompt (para não duplicar na próxima chamada)
    st.session_state.history = [m for m in messages if m["role"] != "system"]
    return final_text


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Logo
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">&gt;_</div>
        <div>
            <div class="sidebar-title">DataChat</div>
            <div class="sidebar-sub">v1.0.0 // powered by Claude</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Status
    st.markdown('<div class="status-pill"><div class="status-dot"></div> system online</div>', unsafe_allow_html=True)

    # Controles rápidos — sempre visíveis no topo
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    col_v, col_n = st.columns(2)
    with col_v:
        if st.button("> menu", use_container_width=True, key="btn_menu"):
            st.session_state.messages = []
            st.session_state.history = []
            st.session_state.df = None
            st.rerun()
    with col_n:
        if st.button("> nova", use_container_width=True, key="btn_nova"):
            st.session_state.messages = []
            st.session_state.history = []
            st.session_state.df = None
            st.rerun()
    st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

    # Dataset
    st.markdown('<div class="sidebar-section">Dataset</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("Carregar CSV", type=["csv"], label_visibility="collapsed")
    if uploaded:
        try:
            df_new = pd.read_csv(uploaded)
            if st.session_state.df is None or not df_new.equals(st.session_state.df):
                st.session_state.df = df_new
                st.session_state.history = []
                st.session_state.messages = []
                st.rerun()
        except Exception as e:
            st.error(f"Erro ao ler CSV: {e}")

    if st.button("Usar exemplo de dados", use_container_width=True):
        np.random.seed(42); n = 300
        cats = np.random.choice(["Bronze","Prata","Ouro","Platina"],n,p=[0.4,0.3,0.2,0.1])
        renda = np.where(cats=="Platina",np.random.normal(16000,3500,n).clip(10000,35000),
                np.where(cats=="Ouro",np.random.normal(9000,2000,n).clip(5500,16000),
                np.where(cats=="Prata",np.random.normal(4800,1000,n).clip(3000,8000),
                np.random.normal(2500,700,n).clip(1200,5000)))).round(2)
        st.session_state.df = pd.DataFrame({
            "cliente_id":range(1001,1001+n),"nome":[f"Cliente {i:03d}" for i in range(1,n+1)],
            "idade":np.random.randint(18,72,n),"genero":np.random.choice(["M","F","Outro"],n,p=[0.48,0.48,0.04]),
            "cidade":np.random.choice(["São Paulo","Rio de Janeiro","Belo Horizonte","Curitiba","Porto Alegre","Fortaleza"],n),
            "categoria":cats,"renda_mensal":renda,
            "total_compras":np.random.randint(1,80,n),"ticket_medio":np.random.normal(280,120,n).clip(40,1200).round(2),
            "satisfacao":np.clip(np.where(cats=="Platina",8,np.where(cats=="Ouro",7,np.where(cats=="Prata",6,5)))+np.random.randint(-2,3,n),1,10),
            "churn_risco":np.random.choice(["Baixo","Médio","Alto"],n,p=[0.55,0.28,0.17]),
            "data_cadastro":pd.date_range("2020-01-01",periods=n,freq="3D").strftime("%Y-%m-%d"),
            "ativo":np.random.choice([True,False],n,p=[0.85,0.15]),
        })
        st.session_state.history = []; st.session_state.messages = []
        st.rerun()

    # Info dataset ativo
    if st.session_state.df is not None:
        d = st.session_state.df
        st.markdown(f"""
        <div class="dataset-badge">
            <strong>{len(d):,}</strong> linhas &nbsp;·&nbsp; <strong>{len(d.columns)}</strong> colunas
        </div>
        """, unsafe_allow_html=True)
        with st.expander("Ver colunas", expanded=False):
            for col in d.columns:
                st.markdown(f"<span style='font-size:0.8rem;color:#8a7f72'>`{col}`</span> <span style='font-size:0.75rem;color:#c4bab0'>{d[col].dtype}</span>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Explorar</div>', unsafe_allow_html=True)

    if st.session_state.df is not None:
        d = st.session_state.df
        num = d.select_dtypes(include=np.number).columns.tolist()
        cat = d.select_dtypes(include=["object","bool"]).columns.tolist()
        sug_col1 = num[0] if num else d.columns[0]
        sug_col2 = cat[0] if cat else d.columns[1] if len(d.columns) > 1 else d.columns[0]
        sugestoes = [
            "Resumo do dataset",
            f"Distribuição de {sug_col1}",
            f"Valores únicos de {sug_col2}",
            "Correlação entre variáveis",
            "Gráfico 3D das variáveis numéricas",
            "Mapa de correlações em rede",
            "Fluxo de análise dos dados",
            f"Árvore de categorias de {sug_col2}",
        ]
    else:
        sugestoes = [
            "Resumo do dataset",
            "Distribuição das variáveis",
            "Valores mais frequentes",
            "Correlação entre variáveis",
            "Registros com valores extremos",
            "Gere registros sintéticos",
        ]
    for texto in sugestoes:
        if st.button(texto, use_container_width=True, key=f"s_{texto}"):
            st.session_state._trigger = texto
            st.rerun()

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.divider()

    n_msgs = len([m for m in st.session_state.messages if m["role"]=="user"])
    st.markdown(f"""
    <div style="background:rgba(0,255,65,0.03);border:1px solid #00ff4118;border-radius:2px;padding:7px 11px;margin-bottom:8px;">
        <span style="font-size:0.65rem;color:#1a4d28;font-family:'JetBrains Mono',monospace;">// {n_msgs} cmds executados</span>
    </div>
    <style>
    div[data-testid="stSidebar"] div[data-testid="stButton"]:has(button[kind="secondary"]) button {{
        background: rgba(0,255,65,0.08) !important;
        border: 1px solid #00ff4145 !important;
        border-radius: 3px !important;
        color: #00cc33 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.74rem !important;
        padding: 7px 10px !important;
        margin-bottom: 4px !important;
        width: 100% !important;
    }}
    #btn_menu, #btn_nova {{
        color: #00ff41 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # (controles movidos para o topo da sidebar)


# ══════════════════════════════════════════════════════════════════════════════
# ÁREA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
main = st.container()

with main:
    # Header inicial (só aparece sem mensagens)
    if not st.session_state.messages:
        if st.session_state.df is not None:
            d = st.session_state.df
            num_cols = d.select_dtypes(include=np.number).columns.tolist()
            cat_cols = d.select_dtypes(include=["object", "bool"]).columns.tolist()
            sug1 = cat_cols[0] if cat_cols else d.columns[0]

            st.markdown("""
            <div class="chat-header">
                <div class="chat-header-cmd">&gt; ./execute <span>datachat.sh</span> --mode=análise</div>
                <h1>O que você quer<br><span>descobrir</span>?<span class="cursor"></span></h1>
                <p>// dataset carregado. escolha uma análise ou faça sua pergunta.</p>
            </div>
            """, unsafe_allow_html=True)

            # Opções rápidas como cards clicáveis
            opcoes = [
                ("01", "[scan] Resumo geral", "// estatísticas completas do dataset", "Resumo do dataset"),
                ("02", "[graph] Rede de correlações", "// grafo interativo entre variáveis", "Mapa de correlações em rede"),
                ("03", "[map] Fluxo de análise", "// mapa visual do raciocínio dos dados", "Fluxo de análise dos dados"),
                ("04", f"[tree] Árvore de {sug1}", "// hierarquia radial de categorias", f"Árvore de categorias de {sug1}"),
                ("05", "[viz] Gráfico 3D", "// visualização tridimensional interativa", "Gráfico 3D das variáveis numéricas"),
                ("06", "[alert] Detectar anomalias", "// outliers e valores fora do padrão", f"Detectar anomalias em {num_cols[0]}" if num_cols else "Detectar anomalias"),
            ]

            cols = st.columns(3)
            for i, (num, titulo, desc, trigger_text) in enumerate(opcoes):
                with cols[i % 3]:
                    if st.button(
                        f"**{num}. {titulo}**\n\n{desc}",
                        use_container_width=True,
                        key=f"opt_{num}",
                    ):
                        st.session_state._trigger = trigger_text
                        st.rerun()

            st.markdown("<div style='text-align:center;color:#1a4d28;font-size:0.72rem;margin-top:1.2rem;font-family:JetBrains Mono,monospace'>// ou digite sua consulta abaixo_</div>", unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class="chat-header">
                <div class="chat-header-cmd">&gt; ./execute <span>datachat.sh</span></div>
                <h1>Análise de dados.<br><span>Do jeito certo.</span><span class="cursor"></span></h1>
                <p>// carregue um CSV abaixo ou use o dataset de exemplo para iniciar.</p>
            </div>
            """, unsafe_allow_html=True)

            # Upload direto na área principal
            st.markdown('<div style="margin-top:0.5rem;margin-bottom:0.3rem;color:#00ff41;font-size:0.78rem;font-family:JetBrains Mono,monospace">// carregar arquivo CSV</div>', unsafe_allow_html=True)
            uploaded_main = st.file_uploader(
                "Carregar CSV",
                type=["csv"],
                label_visibility="collapsed",
                key="upload_main"
            )
            if uploaded_main:
                try:
                    df_new = pd.read_csv(uploaded_main)
                    st.session_state.df = df_new
                    st.session_state.history = []
                    st.session_state.messages = []
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao ler CSV: {e}")

            st.markdown('<div style="margin-top:1rem;margin-bottom:0.5rem;color:#1a4d28;font-size:0.72rem;font-family:JetBrains Mono,monospace">// ou use dados de exemplo</div>', unsafe_allow_html=True)
            if st.button("▶  Usar dataset de exemplo", use_container_width=False, key="exemplo_main"):
                np.random.seed(42); n = 300
                cats = np.random.choice(["Bronze","Prata","Ouro","Platina"],n,p=[0.4,0.3,0.2,0.1])
                renda = np.where(cats=="Platina",np.random.normal(16000,3500,n).clip(10000,35000),
                        np.where(cats=="Ouro",np.random.normal(9000,2000,n).clip(5500,16000),
                        np.where(cats=="Prata",np.random.normal(4800,1000,n).clip(3000,8000),
                        np.random.normal(2500,700,n).clip(1200,5000)))).round(2)
                st.session_state.df = pd.DataFrame({
                    "cliente_id":range(1001,1001+n),"nome":[f"Cliente {i:03d}" for i in range(1,n+1)],
                    "idade":np.random.randint(18,72,n),"genero":np.random.choice(["M","F","Outro"],n,p=[0.48,0.48,0.04]),
                    "cidade":np.random.choice(["São Paulo","Rio de Janeiro","Belo Horizonte","Curitiba","Porto Alegre","Fortaleza"],n),
                    "categoria":cats,"renda_mensal":renda,
                    "total_compras":np.random.randint(1,80,n),"ticket_medio":np.random.normal(280,120,n).clip(40,1200).round(2),
                    "satisfacao":np.clip(np.where(cats=="Platina",8,np.where(cats=="Ouro",7,np.where(cats=="Prata",6,5)))+np.random.randint(-2,3,n),1,10),
                    "churn_risco":np.random.choice(["Baixo","Médio","Alto"],n,p=[0.55,0.28,0.17]),
                    "data_cadastro":pd.date_range("2020-01-01",periods=n,freq="3D").strftime("%Y-%m-%d"),
                    "ativo":np.random.choice([True,False],n,p=[0.85,0.15]),
                })
                st.session_state.history = []; st.session_state.messages = []
                st.rerun()


    # Botão voltar — sempre visível, fixo no topo
    st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stButton"] > button[kind="primary"]) {
        position: fixed; top: 14px; left: 14px; z-index: 9999;
    }
    </style>
    """, unsafe_allow_html=True)
    if st.button("◀ voltar", key="btn_voltar_main", type="primary"):
        st.session_state.messages = []
        st.session_state.history = []
        st.session_state.df = None
        st.rerun()

    # Histórico de mensagens
    for mi, msg in enumerate(st.session_state.messages):
        avatar = "🧑" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            for fi, fig in enumerate(msg.get("charts", [])):
                st.plotly_chart(fig, use_container_width=True, key=f"hist_{mi}_{fi}")
            if msg.get("d3_html"):
                import streamlit.components.v1 as components
                components.html(msg["d3_html"], height=620, scrolling=False)

    # Trigger de sugestão
    trigger = st.session_state.get("_trigger")
    if trigger:
        del st.session_state["_trigger"]
        prompt = trigger
    else:
        prompt = st.chat_input(
            "Pergunte sobre seus dados...",
            disabled=st.session_state.df is None,
        )

    if prompt:
        # Mensagem do usuário
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Resposta do assistente
        with st.chat_message("assistant", avatar="🤖"):
            st.session_state.charts = []
            st.session_state.d3_html = None
            status_ph = st.empty()
            text_ph   = st.empty()

            # Indicador inicial de pensamento
            status_ph.markdown(
                '<div class="thinking"><div class="thinking-dots"><span></span>'
                '<span></span><span></span></div>&nbsp;Analisando…</div>',
                unsafe_allow_html=True,
            )

            response = run_agent_streaming(prompt, text_ph, status_ph)
            status_ph.empty()

            charts_now = list(st.session_state.charts)
            for fi, fig in enumerate(charts_now):
                st.plotly_chart(fig, use_container_width=True, key=f"new_{fi}_{id(fig)}")

            d3_now = st.session_state.get("d3_html")
            if d3_now:
                import streamlit.components.v1 as components
                components.html(d3_now, height=620, scrolling=False)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "charts": charts_now,
            "d3_html": d3_now,
        })
        st.session_state.charts = []
        st.session_state.d3_html = None
        st.rerun()
