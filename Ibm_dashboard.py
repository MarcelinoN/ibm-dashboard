import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="StockVision — IBM Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Estilo global ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .main { background-color: #0b0f1a; }
    .block-container { padding-top: 0rem !important; }

    /* ── Landing ── */
    .landing-wrap {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 4rem 2rem;
        background: radial-gradient(ellipse at 60% 0%, #1e3a5f55 0%, transparent 60%),
                    radial-gradient(ellipse at 20% 80%, #0f2a1e55 0%, transparent 55%),
                    #0b0f1a;
    }
    .badge {
        display: inline-block;
        background: rgba(59,130,246,0.15);
        border: 1px solid rgba(59,130,246,0.4);
        color: #60a5fa;
        font-family: 'Space Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        padding: 0.35rem 1rem;
        border-radius: 999px;
        margin-bottom: 2rem;
    }
    .landing-title {
        font-family: 'Space Mono', monospace;
        font-size: clamp(2.5rem, 6vw, 4.5rem);
        font-weight: 700;
        color: #f9fafb;
        line-height: 1.1;
        margin-bottom: 1.2rem;
    }
    .landing-title span { color: #34d399; }
    .landing-sub {
        font-size: 1.15rem;
        color: #9ca3af;
        max-width: 520px;
        line-height: 1.7;
        margin: 0 auto 2.5rem;
    }
    .features-row {
        display: flex;
        gap: 1.5rem;
        justify-content: center;
        flex-wrap: wrap;
        margin-bottom: 3rem;
    }
    .feature-pill {
        background: rgba(255,255,255,0.04);
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        color: #d1d5db;
        font-size: 0.85rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .ticker-strip {
        display: flex;
        gap: 2rem;
        justify-content: center;
        flex-wrap: wrap;
        margin-top: 3rem;
        opacity: 0.5;
    }
    .ticker-item {
        font-family: 'Space Mono', monospace;
        font-size: 0.7rem;
        color: #6b7280;
        letter-spacing: 0.1em;
    }

    /* ── Dashboard ── */
    .metric-card {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        text-align: center;
    }
    .metric-label {
        font-family: 'Space Mono', monospace;
        font-size: 0.65rem;
        color: #6b7280;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-family: 'Space Mono', monospace;
        font-size: 1.5rem;
        font-weight: 700;
        color: #f9fafb;
    }
    .metric-delta-up   { color: #34d399; font-size: 0.82rem; }
    .metric-delta-down { color: #f87171; font-size: 0.82rem; }
    .section-title {
        font-family: 'Space Mono', monospace;
        font-size: 0.7rem;
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
        font-size: 0.7rem;
        color: #9ca3af;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# ── Estado de navegação ─────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "landing"

# ══════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":

    st.markdown("""
    <div class="landing-wrap">
        <div class="badge">📡 Dados em tempo real · Alpha Vantage API</div>
        <div class="landing-title">Mercado na palma<br>da sua <span>mão.</span></div>
        <div class="landing-sub">
            Dashboard interativo de ações com gráficos de candlestick,
            médias móveis e análise de volume — tudo em um só lugar.
        </div>
        <div class="features-row">
            <div class="feature-pill">📊 Candlestick & Linha</div>
            <div class="feature-pill">📉 Médias Móveis</div>
            <div class="feature-pill">🔊 Análise de Volume</div>
            <div class="feature-pill">⚡ Atualização a cada 5min</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        if st.button("🚀  Acessar o Dashboard", use_container_width=True, type="primary"):
            st.session_state.page = "dashboard"
            st.rerun()

    st.markdown("""
    <div class="ticker-strip">
        <span class="ticker-item">IBM · $219.00</span>
        <span class="ticker-item">AAPL · nasdaq</span>
        <span class="ticker-item">MSFT · nasdaq</span>
        <span class="ticker-item">GOOGL · nasdaq</span>
        <span class="ticker-item">TSLA · nasdaq</span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
else:

    # ── API ──────────────────────────────────────────────────────────────────
    API_URL = (
        "https://www.alphavantage.co/query"
        "?function=TIME_SERIES_INTRADAY"
        "&symbol={symbol}&interval={interval}&apikey={apikey}"
    )

    @st.cache_data(ttl=300)
    def fetch_data(symbol, interval, apikey):
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
        return df.astype(float)

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        if st.button("← Voltar à Home"):
            st.session_state.page = "landing"
            st.rerun()
        st.markdown("## ⚙️ Configurações")
        symbol    = st.text_input("Símbolo", value="IBM").upper()
        interval  = st.selectbox("Intervalo", ["1min","5min","15min","30min","60min"], index=1)
        apikey    = st.text_input("API Key", value="demo", type="password",
                                  help="Use 'demo' apenas para IBM.")
        n_candles = st.slider("Últimas N velas", 20, 200, 80, 10)
        chart_type  = st.radio("Tipo de gráfico", ["Candlestick", "Linha"])
        show_volume = st.checkbox("Mostrar volume", value=True)
        show_ma     = st.checkbox("Mostrar médias móveis", value=True)
        if show_ma:
            ma_fast = st.slider("MA Rápida", 5, 30, 9)
            ma_slow = st.slider("MA Lenta", 10, 100, 21)
        st.markdown("---")
        st.button("🔄 Atualizar", use_container_width=True)

    # ── Cabeçalho ────────────────────────────────────────────────────────────
    st.markdown(f"# 📊 {symbol} — Dashboard Intraday")

    # ── Dados ────────────────────────────────────────────────────────────────
    try:
        df = fetch_data(symbol, interval, apikey)
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        st.stop()

    df_plot = df.tail(n_candles).copy()
    if show_ma:
        df_plot["ma_fast"] = df_plot["close"].rolling(ma_fast).mean()
        df_plot["ma_slow"] = df_plot["close"].rolling(ma_slow).mean()

    # ── Métricas ─────────────────────────────────────────────────────────────
    last      = df_plot["close"].iloc[-1]
    prev      = df_plot["close"].iloc[-2]
    chg       = last - prev
    chg_pct   = chg / prev * 100
    high_day  = df_plot["high"].max()
    low_day   = df_plot["low"].min()
    vol_total = int(df_plot["volume"].sum())
    last_time = df_plot.index[-1].strftime("%H:%M")

    dc    = "metric-delta-up" if chg >= 0 else "metric-delta-down"
    arrow = "▲" if chg >= 0 else "▼"

    cards = [
        ("Último preço",      f"${last:.2f}",      f'<span class="{dc}">{arrow} {chg:+.2f} ({chg_pct:+.2f}%)</span>'),
        ("Máxima do período", f"${high_day:.2f}",  ""),
        ("Mínima do período", f"${low_day:.2f}",   ""),
        ("Volume total",      f"{vol_total:,}",     ""),
        ("Última atualização",last_time,            '<span style="color:#6b7280;font-size:.75rem">US/Eastern</span>'),
    ]
    for col, (label, value, delta) in zip(st.columns(5), cards):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                {delta}
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gráfico principal ─────────────────────────────────────────────────────
    bg, grid_color = "#0b0f1a", "#1f2937"
    color_up, color_down = "#34d399", "#f87171"

    st.markdown('<p class="section-title">Série de preços</p>', unsafe_allow_html=True)
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
            mode="lines", line=dict(color="#60a5fa", width=2),
            fill="tozeroy", fillcolor="rgba(96,165,250,0.07)",
            name="Fechamento",
        ))

    if show_ma:
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot["ma_fast"],
            mode="lines", line=dict(color="#fbbf24", width=1.5, dash="dot"),
            name=f"MA {ma_fast}"))
        fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot["ma_slow"],
            mode="lines", line=dict(color="#a78bfa", width=1.5, dash="dot"),
            name=f"MA {ma_slow}"))

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        paper_bgcolor=bg, plot_bgcolor=bg,
        font=dict(family="DM Sans", color="#9ca3af"),
        margin=dict(l=10, r=10, t=10, b=10), height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        xaxis=dict(gridcolor=grid_color, showgrid=True, zeroline=False),
        yaxis=dict(gridcolor=grid_color, showgrid=True, zeroline=False, side="right"),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Volume ────────────────────────────────────────────────────────────────
    if show_volume:
        st.markdown('<p class="section-title">Volume negociado</p>', unsafe_allow_html=True)
        colors = [color_up if c >= o else color_down
                  for c, o in zip(df_plot["close"], df_plot["open"])]
        fig_vol = go.Figure(go.Bar(x=df_plot.index, y=df_plot["volume"],
                                   marker_color=colors, name="Volume"))
        fig_vol.update_layout(
            paper_bgcolor=bg, plot_bgcolor=bg,
            font=dict(family="DM Sans", color="#9ca3af"),
            margin=dict(l=10, r=10, t=10, b=10), height=200,
            xaxis=dict(gridcolor=grid_color, showgrid=False, zeroline=False),
            yaxis=dict(gridcolor=grid_color, showgrid=True, zeroline=False, side="right"),
            showlegend=False, hovermode="x unified",
        )
        st.plotly_chart(fig_vol, use_container_width=True)

    # ── Tabela ────────────────────────────────────────────────────────────────
    with st.expander("📋 Ver dados brutos"):
        display_df = df_plot[["open","high","low","close","volume"]].copy()
        display_df.index = display_df.index.strftime("%Y-%m-%d %H:%M")
        display_df.columns = ["Abertura","Máxima","Mínima","Fechamento","Volume"]
        st.dataframe(display_df.sort_index(ascending=False).style.format({
            "Abertura": "${:.2f}", "Máxima": "${:.2f}",
            "Mínima": "${:.2f}",  "Fechamento": "${:.2f}", "Volume": "{:,.0f}",
        }), use_container_width=True)

    st.markdown("---")
    st.caption("Dados fornecidos por [Alpha Vantage](https://www.alphavantage.co) · Chave `demo` apenas para IBM.")
