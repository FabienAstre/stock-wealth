import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings("ignore")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TFSA Portfolio Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: #1c1f26;
        border-radius: 10px;
        padding: 16px 20px;
        border: 1px solid #2d3139;
        margin-bottom: 8px;
    }
    .signal-BUY    { color: #00e676; font-weight: 700; font-size: 13px; }
    .signal-SELL   { color: #ff5252; font-weight: 700; font-size: 13px; }
    .signal-HOLD   { color: #ffd740; font-weight: 700; font-size: 13px; }
    .signal-STRONG-BUY  { color: #00e676; font-weight: 900; font-size: 14px; }
    .signal-STRONG-SELL { color: #ff1744; font-weight: 900; font-size: 14px; }
    .news-item {
        background: #1c1f26;
        border-left: 3px solid #3d5afe;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 0 8px 8px 0;
    }
    .pnl-pos { color: #00e676; }
    .pnl-neg { color: #ff5252; }
    .stDataFrame { font-size: 12px; }
    div[data-testid="metric-container"] {
        background-color: #1c1f26;
        border: 1px solid #2d3139;
        border-radius: 10px;
        padding: 12px 16px;
    }
    .ticker-header { font-size: 22px; font-weight: 700; margin-bottom: 4px; }
    .section-title { 
        font-size: 18px; font-weight: 600; 
        border-bottom: 2px solid #3d5afe; 
        padding-bottom: 6px; margin-bottom: 16px; 
    }
</style>
""", unsafe_allow_html=True)

# ── Portfolio data ─────────────────────────────────────────────────────────────
PORTFOLIO = {
    "AAPL.TO": {"shares": 29.99,  "ac": 32.86},
    "ABCL":    {"shares": 159.9965,"ac": 4.2607},
    "AEHR":    {"shares": 15,     "ac": 20.56},
    "AMZN.TO": {"shares": 79.99,  "ac": 17.19},
    "APLD":    {"shares": 25,     "ac": 24.72},
    "APPS.TO": {"shares": 39.842, "ac": 17.68},
    "ASML.TO": {"shares": 45,     "ac": 26.20},
    "BAM.TO":  {"shares": 10.08,  "ac": 72.44},
    "BBAI":    {"shares": 60,     "ac": 7.655},
    "BEP-UN.TO":{"shares":30.3548,"ac": 39.07},
    "BRK.TO":  {"shares": 20,     "ac": 33.38},
    "CEGS.TO": {"shares": 50,  "ac": 21.78},
    "CLBT":    {"shares": 40,     "ac": 18.65},
    "CMPS":    {"shares": 80,     "ac": 5.00},
    "COPP.TO": {"shares": 17,     "ac": 51.35},
    "CRCL":    {"shares": 14,     "ac": 95.28},
    "CRWV":    {"shares": 12.9979,"ac": 109.50},
    "CU.TO":   {"shares": 30.26,  "ac": 37.39},
    "DRUG.CN": {"shares": 8,      "ac": 73.92},
    "ENB.TO":  {"shares": 20,     "ac": 62.53},
    "EOSE":    {"shares": 60,     "ac": 12.09},
    "HELP":    {"shares": 80,     "ac": 8.47},
    "IMVT":    {"shares": 20,     "ac": 26.48},
    "ISRG.NE": {"shares": 25,     "ac": 26.86},
    "JOBY":    {"shares": 60,     "ac": 11.27},
    "LMT.TO":  {"shares": 30.14,  "ac": 31.03},
    "LUNR":    {"shares": 45,     "ac": 11.08},
    "MDA.TO":  {"shares": 50,     "ac": 30.38},
    "META.TO": {"shares": 30,     "ac": 34.75},
    "MSFT.TO": {"shares": 60.11,  "ac": 27.40},
    "NNE":     {"shares": 10,     "ac": 42.58},
    "NU":      {"shares": 40,     "ac": 14.98},
    "NVDA.TO": {"shares": 80,     "ac": 22.96},
    "NVTS":    {"shares": 80,     "ac": 7.84},
    "NXT":     {"shares": 8,      "ac": 72.18},
    "OKLO":    {"shares": 9,      "ac": 121.28},
    "ONE.V":   {"shares": 400,    "ac": 0.8275},
    "PHOS.CN": {"shares": 500,    "ac": 0.5943},
    "PNG.V":   {"shares": 200,    "ac": 5.41},
    "QBTS":    {"shares": 25,     "ac": 25.34},
    "RARE":    {"shares": 20,     "ac": 29.56},
    "RDDT":    {"shares": 7,      "ac": 114.74},
    "RDW":     {"shares": 40,     "ac": 10.25},
    "RGTI":    {"shares": 20,     "ac": 31.16},
    "RXRX":    {"shares": 200,    "ac": 4.61},
    "SCD.V":   {"shares": 2500,   "ac": 0.2285},
    "SOUN":    {"shares": 50,     "ac": 9.50},
    "TEM":     {"shares": 10,     "ac": 63.64},
    "TMC":     {"shares": 100,    "ac": 5.27},
    "TOI.V":   {"shares": 5,      "ac": 115.85},
    "TSLA.TO": {"shares": 31.1267,"ac": 35.72},
    "VEE.TO":  {"shares": 32,     "ac": 41.06},
    "VFV.TO":  {"shares": 32.8581,"ac": 128.76},
    "VNM":     {"shares": 40,     "ac": 17.67},
    "WELL.TO": {"shares": 180,    "ac": 4.05},
    "WPM.TO":  {"shares": 6,      "ac": 146.66},
    "XEF.TO":  {"shares": 29.43,  "ac": 41.71},
    "XID.TO":  {"shares": 13.7926,"ac": 49.38},
    "XSU.TO":  {"shares": 12.18,  "ac": 46.39},
    "ZCN.TO":  {"shares": 25.13,  "ac": 34.91},
    "ZJPN.TO": {"shares": 13.21,  "ac": 45.04},
}

# ── Technical signal engine ────────────────────────────────────────────────────
def compute_signals(hist: pd.DataFrame) -> dict:
    """Compute RSI, MACD, Bollinger, SMA signals → composite verdict."""
    if hist is None or len(hist) < 30:
        return {"signal": "HOLD", "score": 0, "details": {}}

    close = hist["Close"].squeeze()
    signals = {}
    score = 0  # positive = bullish, negative = bearish

    # ── RSI ──
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    rsi   = 100 - (100 / (1 + rs))
    rsi_val = float(rsi.iloc[-1]) if not rsi.empty else 50
    signals["RSI"] = round(rsi_val, 1)
    if   rsi_val < 30: score += 2
    elif rsi_val < 45: score += 1
    elif rsi_val > 70: score -= 2
    elif rsi_val > 55: score -= 1

    # ── MACD ──
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd  = ema12 - ema26
    signal_line = macd.ewm(span=9, adjust=False).mean()
    macd_hist   = macd - signal_line
    signals["MACD_hist"] = round(float(macd_hist.iloc[-1]), 4) if not macd_hist.empty else 0
    if macd_hist.iloc[-1] > 0 and macd_hist.iloc[-2] <= 0: score += 2  # bullish crossover
    elif macd_hist.iloc[-1] < 0 and macd_hist.iloc[-2] >= 0: score -= 2  # bearish crossover
    elif macd_hist.iloc[-1] > 0: score += 1
    elif macd_hist.iloc[-1] < 0: score -= 1

    # ── SMA 50 / 200 (Golden/Death Cross) ──
    sma50  = close.rolling(50).mean()
    sma200 = close.rolling(200).mean()
    price  = float(close.iloc[-1])
    s50    = float(sma50.iloc[-1])  if not sma50.empty else price
    s200   = float(sma200.iloc[-1]) if not sma200.empty else price
    signals["SMA50"]  = round(s50,  2)
    signals["SMA200"] = round(s200, 2)
    signals["Price"]  = round(price, 2)
    if price > s50:  score += 1
    else:             score -= 1
    if price > s200: score += 1
    else:             score -= 1
    if s50 > s200:   score += 1   # golden cross territory
    else:             score -= 1   # death cross territory

    # ── Bollinger Bands ──
    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    upper = sma20 + 2 * std20
    lower = sma20 - 2 * std20
    bb_pos = (price - float(lower.iloc[-1])) / (float(upper.iloc[-1]) - float(lower.iloc[-1]) + 1e-9)
    signals["BB_pos"] = round(bb_pos, 2)
    if   bb_pos < 0.2: score += 1
    elif bb_pos > 0.8: score -= 1

    # ── Volume trend ──
    if "Volume" in hist.columns:
        vol = hist["Volume"].squeeze()
        avg_vol = float(vol.rolling(20).mean().iloc[-1])
        last_vol = float(vol.iloc[-1])
        if avg_vol > 0:
            vol_ratio = last_vol / avg_vol
            signals["Vol_ratio"] = round(vol_ratio, 2)
            if vol_ratio > 1.5 and price > float(close.iloc[-2]): score += 1

    # ── Composite verdict ──
    if   score >= 5:  verdict = "STRONG BUY"
    elif score >= 2:  verdict = "BUY"
    elif score <= -5: verdict = "STRONG SELL"
    elif score <= -2: verdict = "SELL"
    else:             verdict = "HOLD"

    return {"signal": verdict, "score": score, "details": signals}


# ── Data fetcher ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_ticker_data(ticker: str):
    try:
        t = yf.Ticker(ticker)

        # Fetch history first — more reliable than .info
        hist_1y = t.history(period="1y", interval="1d")
        hist_5d = t.history(period="5d", interval="15m")
        hist_1d = t.history(period="1d", interval="5m")

        # Price: try .info, fall back to last close, then fast_info
        price = None
        try:
            inf = t.info or {}
            price = (
                inf.get("currentPrice")
                or inf.get("regularMarketPrice")
                or inf.get("previousClose")
            )
        except Exception:
            inf = {}

        # Fallback 1: last row of 1y history
        if price is None and not hist_1y.empty:
            price = float(hist_1y["Close"].squeeze().iloc[-1])

        # Fallback 2: fast_info (lightweight, avoids heavy scraping)
        if price is None:
            try:
                price = t.fast_info.get("last_price") or t.fast_info.get("lastPrice")
            except Exception:
                pass

        sig = compute_signals(hist_1y)
        return {
            "ticker":     ticker,
            "price":      price,
            "info":       inf,
            "hist_1y":    hist_1y,
            "hist_5d":    hist_5d,
            "hist_1d":    hist_1d,
            "signal":     sig["signal"],
            "score":      sig["score"],
            "indicators": sig["details"],
        }
    except Exception as e:
        return {
            "ticker": ticker, "price": None, "error": str(e),
            "signal": "HOLD", "score": 0, "indicators": {}, "info": {},
            "hist_1y": pd.DataFrame(), "hist_5d": pd.DataFrame(), "hist_1d": pd.DataFrame(),
        }

@st.cache_data(ttl=600)
def fetch_news(ticker: str):
    try:
        t = yf.Ticker(ticker)
        news = t.news or []
        items = []
        for n in news[:5]:
            ct = n.get("content", {})
            title = ct.get("title") or n.get("title", "")
            link  = ct.get("canonicalUrl", {}).get("url") or n.get("link", "")
            pub   = ct.get("pubDate") or ""
            if pub:
                try:
                    pub = datetime.fromisoformat(pub.replace("Z","")).strftime("%b %d, %Y")
                except: pass
            if title:
                items.append({"title": title, "link": link, "date": pub})
        return items
    except:
        return []


# ── Portfolio summary ──────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def build_portfolio_summary():
    rows = []
    for ticker, pos in PORTFOLIO.items():
        d = fetch_ticker_data(ticker)
        price = d.get("price")
        if price is None:
            continue
        shares = pos["shares"]
        ac     = pos["ac"]
        cv     = price * shares
        cb     = ac * shares
        pnl    = cv - cb
        pnl_p  = (pnl / cb * 100) if cb else 0
        rows.append({
            "Ticker":   ticker,
            "Price":    price,
            "Shares":   shares,
            "AC":       ac,
            "Mkt Value":cv,
            "Cost":     cb,
            "P&L $":    pnl,
            "P&L %":    pnl_p,
            "Signal":   d.get("signal", "HOLD"),
            "Score":    d.get("score", 0),
            "RSI":      d.get("indicators", {}).get("RSI", "-"),
            "SMA50":    d.get("indicators", {}).get("SMA50", "-"),
        })
    return pd.DataFrame(rows)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    page = st.radio("View", ["📊 Portfolio Overview", "🔍 Ticker Deep Dive", "📰 News Feed", "📉 Signals Summary"])
    st.markdown("---")
    if page == "🔍 Ticker Deep Dive":
        selected = st.selectbox("Select ticker", sorted(PORTFOLIO.keys()))
    st.markdown("---")
    st.caption("Data via Yahoo Finance · Refreshes every 5 min")
    if st.button("🔄 Force Refresh"):
        st.cache_data.clear()
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Portfolio Overview
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Portfolio Overview":
    st.markdown("# 📊 TFSA Portfolio Dashboard")
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    with st.spinner("Loading all positions…"):
        df = build_portfolio_summary()

    if df.empty:
        st.error("No data loaded. Check your internet connection.")
        st.stop()

    total_val  = df["Mkt Value"].sum()
    total_cost = df["Cost"].sum()
    total_pnl  = df["P&L $"].sum()
    total_pnl_p = (total_pnl / total_cost * 100) if total_cost else 0

    # ── Top metrics ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Portfolio Value",  f"${total_val:,.0f}")
    c2.metric("Cost Basis",       f"${total_cost:,.0f}")
    c3.metric("Total P&L",        f"${total_pnl:,.0f}",   delta=f"{total_pnl_p:+.1f}%")
    c4.metric("Positions loaded", f"{len(df)} / {len(PORTFOLIO)}")

    # ── Signal distribution ──
    st.markdown("---")
    st.markdown("### 🚦 Signal Distribution")
    sig_counts = df["Signal"].value_counts()
    cols = st.columns(5)
    for i, (sig, color) in enumerate([
        ("STRONG BUY","#00e676"), ("BUY","#69f0ae"),
        ("HOLD","#ffd740"),
        ("SELL","#ff5252"), ("STRONG SELL","#ff1744")
    ]):
        cnt = sig_counts.get(sig, 0)
        cols[i].markdown(
            f'<div style="background:#1c1f26;border-radius:10px;padding:12px;'
            f'text-align:center;border-top:3px solid {color}">'
            f'<div style="font-size:22px;font-weight:700;color:{color}">{cnt}</div>'
            f'<div style="font-size:11px;color:#aaa">{sig}</div></div>',
            unsafe_allow_html=True
        )

    # ── Main table ──
    st.markdown("---")
    st.markdown("### 📋 All Positions")

    # Color coding helper
    def color_signal(val):
        colors = {
            "STRONG BUY": "color:#00e676;font-weight:900",
            "BUY":         "color:#69f0ae;font-weight:700",
            "HOLD":        "color:#ffd740;font-weight:700",
            "SELL":        "color:#ff5252;font-weight:700",
            "STRONG SELL": "color:#ff1744;font-weight:900",
        }
        return colors.get(val, "")

    def color_pnl(val):
        return "color:#00e676" if val >= 0 else "color:#ff5252"

    display_df = df[["Ticker","Price","Shares","AC","Mkt Value","P&L $","P&L %","Signal","RSI"]].copy()
    display_df = display_df.sort_values("Mkt Value", ascending=False)
    display_df["Mkt Value"] = display_df["Mkt Value"].map("${:,.0f}".format)
    display_df["P&L $"]     = display_df["P&L $"].map("${:,.0f}".format)
    display_df["P&L %"]     = display_df["P&L %"].map("{:+.1f}%".format)
    display_df["Price"]     = display_df["Price"].map("${:.2f}".format)
    display_df["AC"]        = display_df["AC"].map("${:.2f}".format)
    display_df["Shares"]    = display_df["Shares"].map("{:.2f}".format)

    st.dataframe(display_df, use_container_width=True, height=700)

    # ── Winners / Losers ──
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏆 Top 5 Winners")
        top5 = df.nlargest(5, "P&L %")[["Ticker","P&L %","P&L $","Signal"]]
        top5["P&L %"] = top5["P&L %"].map("{:+.1f}%".format)
        top5["P&L $"] = top5["P&L $"].map("${:,.0f}".format)
        st.dataframe(top5, use_container_width=True, hide_index=True)
    with col2:
        st.markdown("### ⚠️ Top 5 Losers")
        bot5 = df.nsmallest(5, "P&L %")[["Ticker","P&L %","P&L $","Signal"]]
        bot5["P&L %"] = bot5["P&L %"].map("{:+.1f}%".format)
        bot5["P&L $"] = bot5["P&L $"].map("${:,.0f}".format)
        st.dataframe(bot5, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Ticker Deep Dive
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Ticker Deep Dive":
    ticker = selected
    pos    = PORTFOLIO[ticker]
    st.markdown(f"# 🔍 {ticker}")

    with st.spinner(f"Loading {ticker}…"):
        d = fetch_ticker_data(ticker)
        news = fetch_news(ticker)

    price = d.get("price")
    if price is None:
        st.error(f"Could not fetch data for {ticker}. Yahoo Finance may not support this symbol.")
        st.stop()

    inf    = d.get("info", {})
    shares = pos["shares"]
    ac     = pos["ac"]
    cv     = price * shares
    cb     = ac * shares
    pnl    = cv - cb
    pnl_p  = pnl / cb * 100 if cb else 0
    sig    = d.get("signal", "HOLD")
    score  = d.get("score", 0)
    ind    = d.get("indicators", {})

    sig_color = {
        "STRONG BUY": "#00e676", "BUY": "#69f0ae",
        "HOLD": "#ffd740",
        "SELL": "#ff5252", "STRONG SELL": "#ff1744"
    }.get(sig, "#aaa")

    # ── Header row ──
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Current Price",  f"${price:.2f}")
    c2.metric("Avg Cost",       f"${ac:.2f}")
    c3.metric("Market Value",   f"${cv:,.0f}")
    c4.metric("P&L",            f"${pnl:,.0f}", delta=f"{pnl_p:+.1f}%")
    c5.markdown(
        f'<div style="background:#1c1f26;border-radius:10px;padding:12px;text-align:center;'
        f'border:2px solid {sig_color};margin-top:4px">'
        f'<div style="font-size:11px;color:#aaa">SIGNAL</div>'
        f'<div style="font-size:20px;font-weight:900;color:{sig_color}">{sig}</div>'
        f'<div style="font-size:11px;color:#aaa">Score: {score:+d}</div></div>',
        unsafe_allow_html=True
    )

    # ── Charts ──
    st.markdown("---")
    chart_tab, ind_tab = st.tabs(["📈 Price Chart", "📊 Indicators"])

    with chart_tab:
        hist = d.get("hist_1y")
        if hist is not None and not hist.empty:
            close = hist["Close"].squeeze().reset_index()
            close.columns = ["Date", "Close"]
            st.line_chart(close.set_index("Date")["Close"])
        else:
            st.info("No historical data available.")

    with ind_tab:
        rsi = ind.get("RSI", "N/A")
        sma50 = ind.get("SMA50", "N/A")
        sma200 = ind.get("SMA200", "N/A")
        macd_h = ind.get("MACD_hist", "N/A")
        bb_pos = ind.get("BB_pos", "N/A")
        vol_r  = ind.get("Vol_ratio", "N/A")

        ci1, ci2, ci3 = st.columns(3)
        with ci1:
            st.markdown(f"**RSI (14):** {rsi}")
            rsi_v = rsi if isinstance(rsi, (int,float)) else 50
            if rsi_v < 30:   st.success("Oversold → Bullish signal")
            elif rsi_v > 70: st.warning("Overbought → Bearish signal")
            else:             st.info("Neutral zone")

        with ci2:
            st.markdown(f"**SMA 50:** {sma50}")
            st.markdown(f"**SMA 200:** {sma200}")
            if isinstance(sma50,(int,float)) and isinstance(price,(int,float)):
                if price > sma50: st.success("Price above SMA50 ✓")
                else:             st.warning("Price below SMA50 ✗")

        with ci3:
            st.markdown(f"**MACD Histogram:** {macd_h}")
            st.markdown(f"**Bollinger position:** {bb_pos}")
            st.markdown(f"**Volume ratio:** {vol_r}")

        # Indicator summary table
        rows_ind = [
            ("RSI (14)",          rsi, "Oversold (<30 = bullish)" if isinstance(rsi,(int,float)) and rsi<30 else ("Overbought (>70 = bearish)" if isinstance(rsi,(int,float)) and rsi>70 else "Neutral")),
            ("MACD Histogram",    macd_h, "Bullish momentum" if isinstance(macd_h,(int,float)) and macd_h>0 else "Bearish momentum"),
            ("Price vs SMA50",    f"{'Above' if isinstance(sma50,(int,float)) and price>sma50 else 'Below'}", "Bullish" if isinstance(sma50,(int,float)) and price>sma50 else "Bearish"),
            ("Price vs SMA200",   f"{'Above' if isinstance(sma200,(int,float)) and price>sma200 else 'Below'}", "Bullish" if isinstance(sma200,(int,float)) and price>sma200 else "Bearish"),
            ("Bollinger Band pos",bb_pos, "Near lower band (buy zone)" if isinstance(bb_pos,(int,float)) and bb_pos<0.2 else ("Near upper band (sell zone)" if isinstance(bb_pos,(int,float)) and bb_pos>0.8 else "Mid-range")),
            ("Volume ratio",      vol_r, "High volume" if isinstance(vol_r,(int,float)) and vol_r>1.5 else "Normal"),
        ]
        df_ind = pd.DataFrame(rows_ind, columns=["Indicator","Value","Interpretation"])
        st.dataframe(df_ind, use_container_width=True, hide_index=True)

    # ── Company info ──
    st.markdown("---")
    st.markdown("### 🏢 Company Info")
    name    = inf.get("longName") or inf.get("shortName", ticker)
    sector  = inf.get("sector","N/A")
    industry= inf.get("industry","N/A")
    mktcap  = inf.get("marketCap")
    pe      = inf.get("trailingPE")
    fpe     = inf.get("forwardPE")
    ps52h   = inf.get("fiftyTwoWeekHigh")
    ps52l   = inf.get("fiftyTwoWeekLow")
    analys  = inf.get("recommendationMean")
    target  = inf.get("targetMeanPrice")

    ci1, ci2, ci3, ci4 = st.columns(4)
    ci1.markdown(f"**Name:** {name}\n\n**Sector:** {sector}\n\n**Industry:** {industry}")
    ci2.markdown(f"**Market Cap:** {'${:,.0f}B'.format(mktcap/1e9) if mktcap else 'N/A'}\n\n**P/E (trailing):** {round(pe,1) if pe else 'N/A'}\n\n**P/E (forward):** {round(fpe,1) if fpe else 'N/A'}")
    ci3.markdown(f"**52W High:** {'${:.2f}'.format(ps52h) if ps52h else 'N/A'}\n\n**52W Low:** {'${:.2f}'.format(ps52l) if ps52l else 'N/A'}\n\n**Analyst target:** {'${:.2f}'.format(target) if target else 'N/A'}")
    ci4.markdown(f"**Analyst rating:** {round(analys,2) if analys else 'N/A'} (1=Strong Buy, 5=Sell)")

    # ── News ──
    st.markdown("---")
    st.markdown(f"### 📰 Latest News — {ticker}")
    if news:
        for n in news:
            link_html = f'<a href="{n["link"]}" target="_blank" style="color:#5c7cfa;text-decoration:none">{n["title"]}</a>' if n.get("link") else n["title"]
            st.markdown(
                f'<div class="news-item">{link_html}'
                f'<div style="font-size:11px;color:#888;margin-top:4px">{n.get("date","")}</div></div>',
                unsafe_allow_html=True
            )
    else:
        st.info("No recent news found for this ticker.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — News Feed (all tickers)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📰 News Feed":
    st.markdown("# 📰 Portfolio News Feed")
    st.info("Shows latest news for each ticker. Loading may take a moment.")

    tickers_to_show = st.multiselect(
        "Filter tickers", sorted(PORTFOLIO.keys()), default=list(PORTFOLIO.keys())[:10]
    )
    if not tickers_to_show:
        st.warning("Select at least one ticker.")
        st.stop()

    for ticker in tickers_to_show:
        news = fetch_news(ticker)
        if news:
            st.markdown(f"#### {ticker}")
            for n in news[:3]:
                link_html = f'<a href="{n["link"]}" target="_blank" style="color:#5c7cfa;text-decoration:none">{n["title"]}</a>' if n.get("link") else n["title"]
                st.markdown(
                    f'<div class="news-item">{link_html}'
                    f'<div style="font-size:11px;color:#888;margin-top:4px">{n.get("date","")}</div></div>',
                    unsafe_allow_html=True
                )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Signals Summary
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📉 Signals Summary":
    st.markdown("# 📉 Technical Signals — All Positions")

    with st.spinner("Computing signals for all tickers…"):
        df = build_portfolio_summary()

    if df.empty:
        st.error("No data loaded.")
        st.stop()

    # Filter by signal
    sig_filter = st.selectbox("Filter by signal", ["ALL", "STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"])
    if sig_filter != "ALL":
        filtered = df[df["Signal"] == sig_filter]
    else:
        filtered = df

    filtered = filtered.sort_values("Score", ascending=False)

    for _, row in filtered.iterrows():
        sig   = row["Signal"]
        color = {
            "STRONG BUY":"#00e676","BUY":"#69f0ae",
            "HOLD":"#ffd740",
            "SELL":"#ff5252","STRONG SELL":"#ff1744"
        }.get(sig,"#aaa")
        pnl_color = "#00e676" if row["P&L %"] >= 0 else "#ff5252"
        st.markdown(
            f'<div style="background:#1c1f26;border-radius:10px;padding:12px 16px;'
            f'margin-bottom:8px;border-left:4px solid {color};'
            f'display:flex;align-items:center;justify-content:space-between">'
            f'<div><span style="font-size:25px;font-weight:700;color:#aaa">{row["Ticker"]}</span>'
            f' &nbsp; <span style="font-size:12px;color:#aaa">${row["Price"]:.2f} | RSI: {row["RSI"]}</span></div>'
            f'<div style="text-align:right">'
            f'<span style="font-size:14px;font-weight:800;color:{color}">{sig}</span>'
            f' &nbsp; <span style="font-size:12px;color:{pnl_color}">{row["P&L %"]:+.1f}%</span>'
            f'<br><span style="font-size:11px;color:#888">Score: {row["Score"]:+d} | SMA50: ${row["SMA50"]}</span>'
            f'</div></div>',
            unsafe_allow_html=True
        )

    # Actionable summary
    st.markdown("---")
    st.markdown("### ⚡ Actionable Summary")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🟢 Strong Buy / Buy signals:**")
        buys = df[df["Signal"].isin(["BUY","STRONG BUY"])].sort_values("Score",ascending=False)
        for _, r in buys.iterrows():
            st.markdown(f"- **{r['Ticker']}** — Score {r['Score']:+d} | RSI {r['RSI']} | {r['P&L %']:+.1f}%")
    with c2:
        st.markdown("**🔴 Sell / Strong Sell signals:**")
        sells = df[df["Signal"].isin(["SELL","STRONG SELL"])].sort_values("Score")
        for _, r in sells.iterrows():
            st.markdown(f"- **{r['Ticker']}** — Score {r['Score']:+d} | RSI {r['RSI']} | {r['P&L %']:+.1f}%")
