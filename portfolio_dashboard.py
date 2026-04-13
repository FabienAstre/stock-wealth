import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

# ═════════════════════════════════════════════════════
# CONFIG
# ═════════════════════════════════════════════════════

st.set_page_config(page_title="Portfolio AI", layout="wide")
# =========================
# PORTFOLIO INPUT
# =========================
PORTFOLIO = {
    "AAPL.TO": {"shares": 29.99, "ac": 32.86},
    "ABCL": {"shares": 159.9965, "ac": 4.2607},
    "AEHR": {"shares": 15, "ac": 20.56},
    "AMZN.TO": {"shares": 79.99, "ac": 17.19},
    "APLD": {"shares": 25, "ac": 24.72},
    "APPS.NE": {"shares": 39.842, "ac": 17.68},
    "ASML.TO": {"shares": 45, "ac": 26.20},
    "BAM.TO": {"shares": 10.08, "ac": 72.44},
    "BBAI": {"shares": 60, "ac": 7.655},
    "BEP-UN.TO": {"shares": 30.3548, "ac": 39.07},
    "BRK.TO": {"shares": 20, "ac": 33.38},
    "CEGS.TO": {"shares": 43.05, "ac": 22.01},
    "CGL.TO": {"shares": 15, "ac": 22.19},
    "CLBT": {"shares": 40, "ac": 18.65},
    "CMPS": {"shares": 80, "ac": 5.00},
    "COPP.TO": {"shares": 17, "ac": 51.35},
    "CRCL": {"shares": 14, "ac": 95.28},
    "CRWV": {"shares": 12.9979, "ac": 109.50},
    "CU.TO": {"shares": 30.26, "ac": 37.39},
    "DRUG.CN": {"shares": 8, "ac": 73.92},
    "ENB.TO": {"shares": 20, "ac": 62.53},
    "EOSE": {"shares": 60, "ac": 12.09},
    "HELP": {"shares": 80, "ac": 8.47},
    "IMVT": {"shares": 10, "ac": 26.47},
    "ISRG.NE": {"shares": 25, "ac": 26.86},
    "JOBY": {"shares": 45, "ac": 12.14},
    "LMT.TO": {"shares": 30.14, "ac": 31.03},
    "LUNR": {"shares": 45, "ac": 11.08},
    "MDA.TO": {"shares": 50, "ac": 30.38},
    "META.TO": {"shares": 30, "ac": 34.75},
    "MSFT.TO": {"shares": 60.11, "ac": 27.40},
    "NNE": {"shares": 10, "ac": 42.58},
    "NU": {"shares": 40, "ac": 14.98},
    "NVDA.TO": {"shares": 80, "ac": 22.96},
    "NVTS": {"shares": 60, "ac": 7.21},
    "NXT": {"shares": 8, "ac": 72.18},
    "OKLO": {"shares": 9, "ac": 121.28},
    "ONE.V": {"shares": 400, "ac": 0.8275},
    "PHOS.CN": {"shares": 500, "ac": 0.5943},
    "PNG.V": {"shares": 200, "ac": 5.41},
    "QBTS": {"shares": 25, "ac": 25.34},
    "RARE": {"shares": 20, "ac": 29.56},
    "RDDT": {"shares": 7, "ac": 114.74},
    "RDW": {"shares": 40, "ac": 10.25},
    "RGTI": {"shares": 20, "ac": 31.16},
    "RXRX": {"shares": 200, "ac": 4.61},
    "SCD.V": {"shares": 2500, "ac": 0.2285},
    "SOUN": {"shares": 50, "ac": 9.50},
    "TEM": {"shares": 10, "ac": 63.64},
    "TMC": {"shares": 100, "ac": 5.27},
    "TOI.V": {"shares": 5, "ac": 115.85},
    "TSLA.TO": {"shares": 31.1267, "ac": 35.72},
    "VEE.TO": {"shares": 32, "ac": 41.06},
    "VFV.TO": {"shares": 32.8581, "ac": 128.76},
    "VNM": {"shares": 40, "ac": 17.67},
    "WELL.TO": {"shares": 180, "ac": 4.05},
    "WPM.TO": {"shares": 6, "ac": 146.66},
    "XEF.TO": {"shares": 29.43, "ac": 41.71},
    "XID.TO": {"shares": 13.7926, "ac": 49.38},
    "XSU.TO": {"shares": 12.18, "ac": 46.39},
    "ZCN.TO": {"shares": 25.13, "ac": 34.91},
    "ZJPN.TO": {"shares": 13.21, "ac": 45.04},
}

SIG_COLOR = {
    "STRONG BUY": "#00e676",
    "BUY": "#69f0ae",
    "HOLD": "#ffd740",
    "SELL": "#ff5252",
    "STRONG SELL": "#d50000"
}

# ═════════════════════════════════════════════════════
# DATA LAYER (LIVE)
# ═════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def fetch_data(ticker):
    df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
    df.dropna(inplace=True)

    price = float(df["Close"].iloc[-1]) if not df.empty else None

    return {"price": price, "hist": df}


# ═════════════════════════════════════════════════════
# INDICATORS ENGINE
# ═════════════════════════════════════════════════════

def compute_indicators(df):
    close = df["Close"]

    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))

    sma50 = close.rolling(50).mean()
    sma200 = close.rolling(200).mean()

    ema12 = close.ewm(span=12).mean()
    ema26 = close.ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    macd_hist = macd - signal

    vol_ratio = df["Volume"] / df["Volume"].rolling(20).mean()

    return {
        "RSI": float(rsi.iloc[-1]),
        "SMA50": float(sma50.iloc[-1]),
        "SMA200": float(sma200.iloc[-1]),
        "MACD_hist": float(macd_hist.iloc[-1]),
        "Vol_ratio": float(vol_ratio.iloc[-1])
    }


# ═════════════════════════════════════════════════════
# SIGNAL ENGINE (REAL SCORING)
# ═════════════════════════════════════════════════════

def generate_signal(price, ind):
    score = 0

    if price > ind["SMA200"]:
        score += 2
    else:
        score -= 2

    if ind["SMA50"] > ind["SMA200"]:
        score += 2
    else:
        score -= 1

    if ind["MACD_hist"] > 0:
        score += 2
    else:
        score -= 2

    if ind["RSI"] < 30:
        score += 2
    elif ind["RSI"] > 70:
        score -= 2

    if ind["Vol_ratio"] > 1.5:
        score += 1

    if score >= 5:
        sig = "STRONG BUY"
    elif score >= 2:
        sig = "BUY"
    elif score <= -5:
        sig = "STRONG SELL"
    elif score <= -2:
        sig = "SELL"
    else:
        sig = "HOLD"

    confidence = min(100, abs(score) * 12)

    return sig, score, confidence


# ═════════════════════════════════════════════════════
# SUMMARY ENGINE
# ═════════════════════════════════════════════════════

def build_summary(portfolio):
    rows = []

    for tk, pos in portfolio.items():
        d = fetch_data(tk)
        price = d["price"]
        hist = d["hist"]

        if price is None or hist.empty:
            continue

        ind = compute_indicators(hist)
        sig, score, conf = generate_signal(price, ind)

        mv = price * pos["shares"]
        cb = pos["ac"] * pos["shares"]
        pnl = mv - cb
        pnlp = pnl / cb * 100 if cb else 0

        rows.append({
            "Ticker": tk,
            "Price": price,
            "Mkt Value": mv,
            "P&L $": pnl,
            "P&L %": pnlp,
            "Signal": sig,
            "Score": score,
            "Conf %": conf,
            "RSI": ind["RSI"],
            "MACD": ind["MACD_hist"],
            "SMA50": ind["SMA50"],
            "SMA200": ind["SMA200"],
        })

    return pd.DataFrame(rows)


# ═════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "📊 Portfolio Overview",
    "🔍 Ticker Deep Dive",
    "📉 Signals Summary",
    "🛠️ Trading Tools"
])

selected = st.sidebar.selectbox("Ticker", list(PORTFOLIO.keys()))


# ═════════════════════════════════════════════════════
# PAGE 1 — PORTFOLIO OVERVIEW
# ═════════════════════════════════════════════════════

if page == "📊 Portfolio Overview":
    st.title("📊 Portfolio Overview")

    df = build_summary(PORTFOLIO)

    total = df["Mkt Value"].sum()
    pnl = df["P&L $"].sum()

    c1, c2 = st.columns(2)
    c1.metric("Total Value", f"${total:,.0f}")
    c2.metric("Total P&L", f"${pnl:,.0f}")

    st.dataframe(df.sort_values("P&L %", ascending=False), use_container_width=True)


# ═════════════════════════════════════════════════════
# PAGE 2 — TICKER DEEP DIVE (YOUR VERSION PRESERVED)
# ═════════════════════════════════════════════════════

elif page == "🔍 Ticker Deep Dive":
    ticker = selected
    pos = PORTFOLIO[ticker]
    st.markdown(f"# 🔍 {ticker}")

    with st.spinner("Loading..."):
        d = fetch_data(ticker)

    price = d["price"]
    if not price:
        st.error("No data")
        st.stop()

    hist = d["hist"]
    ind = compute_indicators(hist)
    sig, score, conf = generate_signal(price, ind)

    cv = price * pos["shares"]
    cb = pos["ac"] * pos["shares"]
    pnl = cv - cb
    pnlp = pnl / cb * 100 if cb else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Price", f"${price:.2f}")
    c2.metric("P&L", f"${pnl:,.0f}", delta=f"{pnlp:+.1f}%")
    c3.metric("Score", score)
    c4.metric("Confidence", f"{conf}%")

    st.markdown(f"### Signal: **{sig}**")


# ═════════════════════════════════════════════════════
# PAGE 3 — SIGNALS SUMMARY
# ═════════════════════════════════════════════════════

elif page == "📉 Signals Summary":
    st.title("📉 Signals Summary")

    df = build_summary(PORTFOLIO)

    filt = st.selectbox("Filter", ["ALL", "BUY", "STRONG BUY", "HOLD", "SELL", "STRONG SELL"])
    if filt != "ALL":
        df = df[df["Signal"] == filt]

    df = df.sort_values("Score", ascending=False)
    st.dataframe(df, use_container_width=True)


# ═════════════════════════════════════════════════════
# PAGE 4 — TRADING TOOLS (SIMPLIFIED CORE)
# ═════════════════════════════════════════════════════

elif page == "🛠️ Trading Tools":
    st.title("🛠️ Trading Tools")

    tool = st.selectbox("Tool", [
        "Position Sizer",
        "Risk/Reward Calculator"
    ])

    if tool == "Position Sizer":
        capital = st.number_input("Capital", 10000)
        risk = st.number_input("Risk %", 2.0)
        entry = st.number_input("Entry", 100.0)
        stop = st.number_input("Stop", 95.0)

        risk_amt = capital * risk / 100
        shares = risk_amt / (entry - stop)

        st.metric("Shares", f"{shares:.2f}")
        st.metric("Position", f"${shares*entry:.0f}")

    elif tool == "Risk/Reward Calculator":
        entry = st.number_input("Entry", 100.0)
        stop = st.number_input("Stop", 95.0)
        target = st.number_input("Target", 120.0)
        shares = st.number_input("Shares", 10)

        risk = (entry - stop) * shares
        reward = (target - entry) * shares

        st.metric("Risk", f"${risk:.0f}")
        st.metric("Reward", f"${reward:.0f}")
        st.metric("R/R", f"{reward/risk:.2f}x")
