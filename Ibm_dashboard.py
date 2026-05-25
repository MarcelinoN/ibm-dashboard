import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="IBM Stock Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilo customizado ──────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    .main { background-color: #0b0f1a; }
    .block-container { padding-top: 2rem; }

    .metric-card {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        text-align: center;
    }
    .metric-label {
        font-family: 'Space Mono', monospace;
        font-size: 0.7rem;
        color: #6b7280;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-family: 'Space Mono', monospace;
        font-size: 1.6rem;
        font-weight: 700;
        color: #f9fafb;
    }
    .metric-delta-up   { color: #34d399; font-size: 0.85rem; }
    .metric-delta-down { color: #f87171; font-size: 0.85rem; }

    .section-title {
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        color: #6b7280;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
        border-left: 3px solid #3b82f6;
        padding-left: 0.6rem;
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stSlider"] label {
        font-family: 'Space Mono', monospace;
        font-size: 0.72rem;
        color: #9ca3af;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# ── Funções de dados ────────────────────────────────────────────────────────
API_URL = (
    "https://www.alphavantage.co/query"
    "?function=TIME_SERIES_INTRADAY"
    "&symbol={symbol}"
    "&interval={interval}"
    "&apikey={apikey}"
)

@st.cache_data(ttl=300)
def fetch_data(symbol: str, interval: str, apikey: str) -> pd.DataFrame:
    url = API_URL.format(symbol=symbol, interval=interval, apikey=apikey)
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    raw = resp.json()

    key = f"Time Series ({interval})"
    if key not in raw:
        raise ValueError(f"Chave '{key}' não encontrada. Resposta: {raw}")

    df = pd.DataFrame(raw[key]).T
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    df.columns = ["open", "high", "low", "close", "volume"]
    df = df.astype(float)
    return df

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configurações")
    symbol   = st.text_input("Símbolo", value="IBM").upper()
    interval = st.selectbox("Intervalo", ["1min", "5min", "15min", "30min", "60min"], index=1)
    apikey   = st.text_input("API Key", value="demo", type="password",
                             help="Use 'demo' para IBM. Para outros ativos, obtenha uma chave gratuita em alphavantage.co")
    n_candles = st.slider("Últimas N velas", min_value=20, max_value=200, value=80, step=10)
    chart_type = st.radio("Tipo de gráfico principal", ["Candlestick", "Linha"])
    show_volume = st.checkbox("Mostrar volume", value=True)
    show_ma     = st.checkbox("Mostrar médias móveis", value=True)
    if show_ma:
        ma_fast = st.slider("MA Rápida (períodos)", 5, 30, 9)
        ma_slow = st.slider("MA Lenta (períodos)", 10, 100, 21)

    st.markdown("---")
    btn = st.button("🔄 Atualizar dados", use_container_width=True)

# ── Carregamento ─────────────────────────────────────────────────────────────
st.markdown(f"# 📊 {symbol} — Dashboard Intraday")

try:
    df = fetch_data(symbol, interval, apikey)
except Exception as e:
    st.error(f"Erro ao buscar dados: {e}")
    st.stop()

df_plot = df.tail(n_candles).copy()
if show_ma:
    df_plot["ma_fast"] = df_plot["close"].rolling(ma_fast).mean()
    df_plot["ma_slow"] = df_plot["close"].rolling(ma_slow).mean()

# ── Métricas ─────────────────────────────────────────────────────────────────
last       = df_plot["close"].iloc[-1]
prev       = df_plot["close"].iloc[-2]
chg        = last - prev
chg_pct    = chg / prev * 100
high_day   = df_plot["high"].max()
low_day    = df_plot["low"].min()
vol_total  = int(df_plot["volume"].sum())
last_time  = df_plot.index[-1].strftime("%H:%M")

delta_class = "metric-delta-up" if chg >= 0 else "metric-delta-down"
arrow       = "▲" if chg >= 0 else "▼"

col1, col2, col3, col4, col5 = st.columns(5)
cards = [
    ("Último preço", f"${last:.2f}", f'<span class="{delta_class}">{arrow} {chg:+.2f} ({chg_pct:+.2f}%)</span>'),
    ("Máxima do período", f"${high_day:.2f}", ""),
    ("Mínima do período", f"${low_day:.2f}", ""),
    ("Volume total", f"{vol_total:,}", ""),
    ("Última atualização", last_time, '<span style="color:#6b7280;font-size:0.75rem">US/Eastern</span>'),
]
for col, (label, value, delta) in zip([col1, col2, col3, col4, col5], cards):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta}
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Gráfico principal ─────────────────────────────────────────────────────────
st.markdown('<p class="section-title">Série de preços</p>', unsafe_allow_html=True)

color_up   = "#34d399"
color_down = "#f87171"
bg         = "#0b0f1a"
grid_color = "#1f2937"

fig = go.Figure()

if chart_type == "Candlestick":
    fig.add_trace(go.Candlestick(
        x=df_plot.index,
        open=df_plot["open"], high=df_plot["high"],
        low=df_plot["low"],   close=df_plot["close"],
        increasing_line_color=color_up,   increasing_fillcolor=color_up,
        decreasing_line_color=color_down, decreasing_fillcolor=color_down,
        name="OHLC",
    ))
else:
    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot["close"],
        mode="lines",
        line=dict(color="#60a5fa", width=2),
        fill="tozeroy",
        fillcolor="rgba(96,165,250,0.07)",
        name="Fechamento",
    ))

if show_ma:
    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot["ma_fast"],
        mode="lines", line=dict(color="#fbbf24", width=1.5, dash="dot"),
        name=f"MA {ma_fast}",
    ))
    fig.add_trace(go.Scatter(
        x=df_plot.index, y=df_plot["ma_slow"],
        mode="lines", line=dict(color="#a78bfa", width=1.5, dash="dot"),
        name=f"MA {ma_slow}",
    ))

fig.update_layout(
    xaxis_rangeslider_visible=False,
    paper_bgcolor=bg, plot_bgcolor=bg,
    font=dict(family="DM Sans", color="#9ca3af"),
    margin=dict(l=10, r=10, t=10, b=10),
    height=420,
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
    xaxis=dict(gridcolor=grid_color, showgrid=True, zeroline=False),
    yaxis=dict(gridcolor=grid_color, showgrid=True, zeroline=False, side="right"),
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)

# ── Volume ────────────────────────────────────────────────────────────────────
if show_volume:
    st.markdown('<p class="section-title">Volume negociado</p>', unsafe_allow_html=True)
    colors = [color_up if c >= o else color_down
              for c, o in zip(df_plot["close"], df_plot["open"])]
    fig_vol = go.Figure(go.Bar(
        x=df_plot.index, y=df_plot["volume"],
        marker_color=colors, name="Volume",
    ))
    fig_vol.update_layout(
        paper_bgcolor=bg, plot_bgcolor=bg,
        font=dict(family="DM Sans", color="#9ca3af"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=200,
        xaxis=dict(gridcolor=grid_color, showgrid=False, zeroline=False),
        yaxis=dict(gridcolor=grid_color, showgrid=True, zeroline=False, side="right"),
        showlegend=False,
        hovermode="x unified",
    )
    st.plotly_chart(fig_vol, use_container_width=True)

# ── Tabela de dados ───────────────────────────────────────────────────────────
with st.expander("📋 Ver dados brutos"):
    display_df = df_plot[["open","high","low","close","volume"]].copy()
    display_df.index = display_df.index.strftime("%Y-%m-%d %H:%M")
    display_df.columns = ["Abertura", "Máxima", "Mínima", "Fechamento", "Volume"]
    st.dataframe(display_df.sort_index(ascending=False).style.format({
        "Abertura": "${:.2f}", "Máxima": "${:.2f}",
        "Mínima": "${:.2f}",  "Fechamento": "${:.2f}",
        "Volume": "{:,.0f}",
    }), use_container_width=True)

# ── Rodapé ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Dados fornecidos por [Alpha Vantage](https://www.alphavantage.co) · Use a chave `demo` apenas para o símbolo IBM.")