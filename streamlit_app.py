import streamlit as st, pandas as pd, plotly.graph_objects as go, requests, ta
st.set_page_config(page_title="AI-Trader", layout="wide")
st.title("Free AI Trading Dashboard")
PAIRS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","ADAUSDT"]
@st.cache_data(ttl=120)
def get(symbol):
    url = f"https://testnet.binance.vision/api/v3/klines?symbol={symbol}&interval=1h&limit=100"
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns="t o h l c v x qv n tb tq x".split())
    df["date"] = pd.to_datetime(df.t, unit="ms")
    for col in "o h l c".split(): df[col] = pd.to_numeric(df[col])
    df["rsi"] = ta.momentum.rsi(df.c, 14)
    df["signal"] = (df.rsi < 30).astype(int).diff()
    return df
cols = st.columns(len(PAIRS))
for idx, pair in enumerate(PAIRS):
    df = get(pair)
    with cols[idx]:
        fig = go.Figure(go.Candlestick(x=df.date, open=df.o, high=df.h, low=df.l, close=df.c))
        buys  = df[df.signal == 1]
        sells = df[df.signal == -1]
        fig.add_scatter(x=buys.date,  y=buys.c*.99, marker=dict(color="green", size=10), name="Buy", mode="markers")
        fig.add_scatter(x=sells.date, y=sells.c*1.01, marker=dict(color="red", size=10), name="Sell", mode="markers")
        fig.update_layout(title=pair, xaxis_rangeslider_visible=False, height=350, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
