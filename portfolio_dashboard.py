import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TFSA Portfolio Dashboard v2",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.main { background-color: #0e1117; }
.metric-card {
    background: #1c1f26; border-radius: 10px;
    padding: 16px 20px; border: 1px solid #2d3139; margin-bottom: 8px;
}
div[data-testid="metric-container"] {
    background-color: #1c1f26; border: 1px solid #2d3139;
    border-radius: 10px; padding: 12px 16px;
}
.news-item {
    background: #1c1f26; border-left: 3px solid #3d5afe;
    padding: 10px 14px; margin-bottom: 8px; border-radius: 0 8px 8px 0;
}
.signal-chip {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 12px; font-weight: 700; letter-spacing: .04em;
}
.chip-STRONG-BUY  { background:#003d1f; color:#00e676; border:1px solid #00e676; }
.chip-BUY         { background:#003d1f; color:#69f0ae; border:1px solid #69f0ae; }
.chip-HOLD        { background:#3d3000; color:#ffd740; border:1px solid #ffd740; }
.chip-SELL        { background:#3d0000; color:#ff5252; border:1px solid #ff5252; }
.chip-STRONG-SELL { background:#3d0000; color:#ff1744; border:1px solid #ff1744; }
.ticker-STRONG-BUY  { color:#00e676; font-weight:900; }
.ticker-BUY         { color:#69f0ae; font-weight:700; }
.ticker-HOLD        { color:#ffd740; font-weight:700; }
.ticker-SELL        { color:#ff5252; font-weight:700; }
.ticker-STRONG-SELL { color:#ff1744; font-weight:900; }
.ai-box {
    background: linear-gradient(135deg,#0d1b2a,#1a1f35);
    border: 1px solid #3d5afe; border-radius: 12px;
    padding: 18px 22px; margin: 12px 0;
}
.ai-title { color:#7986cb; font-size:13px; font-weight:700;
            text-transform:uppercase; letter-spacing:.08em; margin-bottom:8px; }
.earnings-box {
    background:#1a2035; border:1px solid #5c6bc0;
    border-radius:10px; padding:14px 18px; margin:8px 0;
}
.consensus-BUY    { color:#00e676; }
.consensus-SELL   { color:#ff5252; }
.consensus-HOLD   { color:#ffd740; }
.stDataFrame { font-size:12px; }
</style>
""", unsafe_allow_html=True)

# ── Trades persistence ─────────────────────────────────────────────────────────
TRADES_FILE = Path("trades.json")

def load_trades() -> list:
    if TRADES_FILE.exists():
        try:
            return json.loads(TRADES_FILE.read_text())
        except:
            return []
    return []

def save_trades(trades: list):
    TRADES_FILE.write_text(json.dumps(trades, indent=2))

def compute_positions(trades: list) -> dict:
    """Aggregate trades → {ticker: {shares, ac, cost_basis}}."""
    positions = {}
    for t in trades:
        tk   = t["ticker"].upper().strip()
        sh   = float(t["shares"])
        pr   = float(t["price"])
        side = t["side"]
        if tk not in positions:
            positions[tk] = {"shares": 0.0, "total_cost": 0.0}
        if side == "BUY":
            positions[tk]["total_cost"] += sh * pr
            positions[tk]["shares"]     += sh
        else:  # SELL
            if positions[tk]["shares"] > 0:
                # reduce at average cost
                ac = positions[tk]["total_cost"] / positions[tk]["shares"]
                sold = min(sh, positions[tk]["shares"])
                positions[tk]["total_cost"] -= sold * ac
                positions[tk]["shares"]     -= sold
    # clean zero positions
    return {
        k: {
            "shares": round(v["shares"], 6),
            "ac":     round(v["total_cost"] / v["shares"], 4) if v["shares"] > 0 else 0
        }
        for k, v in positions.items() if v["shares"] > 0.001
    }

# ── Seed with original portfolio if no trades file yet ────────────────────────
DEFAULT_PORTFOLIO = {
    "AAPL.TO": {"shares": 29.99,    "ac": 32.86},
    "ABCL":    {"shares": 159.9965, "ac": 4.2607},
    "AEHR":    {"shares": 15,       "ac": 20.56},
    "AMZN.TO": {"shares": 79.99,    "ac": 17.19},
    "APLD":    {"shares": 25,       "ac": 24.72},
    "APPS.NE": {"shares": 39.842,   "ac": 17.68},
    "ASML.TO": {"shares": 45,       "ac": 26.20},
    "BAM.TO":  {"shares": 10.08,    "ac": 72.44},
    "BBAI":    {"shares": 60,       "ac": 7.655},
    "BEP-UN.TO":{"shares":30.3548,  "ac": 39.07},
    "BRK.TO":  {"shares": 20,       "ac": 33.38},
    "CEGS.TO": {"shares": 43.05,    "ac": 22.01},
    "CGL.TO":  {"shares": 15,       "ac": 22.19},
    "CLBT":    {"shares": 40,       "ac": 18.65},
    "CMPS":    {"shares": 80,       "ac": 5.00},
    "COPP.TO": {"shares": 17,       "ac": 51.35},
    "CRCL":    {"shares": 14,       "ac": 95.28},
    "CRWV":    {"shares": 12.9979,  "ac": 109.50},
    "CU.TO":   {"shares": 30.26,    "ac": 37.39},
    "DRUG.CN": {"shares": 6,        "ac": 59.93},
    "ENB.TO":  {"shares": 20,       "ac": 62.53},
    "EOSE":    {"shares": 60,       "ac": 12.09},
    "HELP":    {"shares": 80,       "ac": 8.47},
    "IMVT":    {"shares": 10,       "ac": 26.47},
    "ISRG.NE": {"shares": 25,       "ac": 26.86},
    "JOBY":    {"shares": 45,       "ac": 12.14},
    "LMT.TO":  {"shares": 30.14,    "ac": 31.03},
    "LUNR":    {"shares": 45,       "ac": 11.08},
    "MDA.TO":  {"shares": 50,       "ac": 30.38},
    "META.TO": {"shares": 30,       "ac": 34.75},
    "MSFT.TO": {"shares": 60.11,    "ac": 27.40},
    "NNE":     {"shares": 10,       "ac": 42.58},
    "NU":      {"shares": 40,       "ac": 14.98},
    "NVDA.TO": {"shares": 80,       "ac": 22.96},
    "NVTS":    {"shares": 60,       "ac": 7.21},
    "NXT":     {"shares": 8,        "ac": 72.18},
    "OKLO":    {"shares": 9,        "ac": 121.28},
    "ONE.V":   {"shares": 400,      "ac": 0.8275},
    "PHOS.CN": {"shares": 500,      "ac": 0.5943},
    "PNG.V":   {"shares": 200,      "ac": 5.41},
    "QBTS":    {"shares": 25,       "ac": 25.34},
    "RARE":    {"shares": 20,       "ac": 29.56},
    "RDDT":    {"shares": 7,        "ac": 114.74},
    "RDW":     {"shares": 40,       "ac": 10.25},
    "RGTI":    {"shares": 20,       "ac": 31.16},
    "RXRX":    {"shares": 200,      "ac": 4.61},
    "SCD.V":   {"shares": 2500,     "ac": 0.2285},
    "SOUN":    {"shares": 50,       "ac": 9.50},
    "TEM":     {"shares": 10,       "ac": 63.64},
    "TMC":     {"shares": 100,      "ac": 5.27},
    "TOI.V":   {"shares": 5,        "ac": 115.85},
    "TSLA.TO": {"shares": 31.1267,  "ac": 35.72},
    "VEE.TO":  {"shares": 32,       "ac": 41.06},
    "VFV.TO":  {"shares": 32.8581,  "ac": 128.76},
    "VNM":     {"shares": 40,       "ac": 17.67},
    "WELL.TO": {"shares": 180,      "ac": 4.05},
    "WPM.TO":  {"shares": 6,        "ac": 146.66},
    "XEF.TO":  {"shares": 29.43,    "ac": 41.71},
    "XID.TO":  {"shares": 13.7926,  "ac": 49.38},
    "XSU.TO":  {"shares": 12.18,    "ac": 46.39},
    "ZCN.TO":  {"shares": 25.13,    "ac": 34.91},
    "ZJPN.TO": {"shares": 13.21,    "ac": 45.04},
}

def seed_trades_from_default():
    """If no trades file, seed from the default portfolio snapshot."""
    trades = []
    for tk, pos in DEFAULT_PORTFOLIO.items():
        trades.append({
            "id":     f"seed_{tk}",
            "date":   "2024-01-01",
            "ticker": tk,
            "side":   "BUY",
            "shares": pos["shares"],
            "price":  pos["ac"],
            "note":   "Initial import"
        })
    save_trades(trades)
    return trades

if not TRADES_FILE.exists():
    seed_trades_from_default()

# ── Technical signals ──────────────────────────────────────────────────────────
def compute_signals(hist: pd.DataFrame) -> dict:
    if hist is None or len(hist) < 26:
        return {"signal": "HOLD", "score": 0, "details": {}, "confidence": 0}
    close  = hist["Close"].squeeze()
    score  = 0
    sigs   = {}
    total  = 0   # max possible score counter

    # RSI
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    rsi   = 100 - (100 / (1 + rs))
    rv    = float(rsi.iloc[-1]) if len(rsi) >= 14 else 50
    sigs["RSI"] = round(rv, 1)
    total += 2
    if   rv < 30: score += 2
    elif rv < 45: score += 1
    elif rv > 70: score -= 2
    elif rv > 55: score -= 1

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd  = ema12 - ema26
    sig_l = macd.ewm(span=9, adjust=False).mean()
    mh    = macd - sig_l
    mv    = float(mh.iloc[-1])
    mp    = float(mh.iloc[-2]) if len(mh) > 1 else mv
    sigs["MACD_hist"] = round(mv, 4)
    total += 2
    if   mv > 0 and mp <= 0: score += 2
    elif mv < 0 and mp >= 0: score -= 2
    elif mv > 0: score += 1
    elif mv < 0: score -= 1

    # SMA
    sma50  = close.rolling(50).mean()
    sma200 = close.rolling(200).mean()
    price  = float(close.iloc[-1])
    s50    = float(sma50.iloc[-1])  if len(sma50.dropna())  >= 1 else price
    s200   = float(sma200.iloc[-1]) if len(sma200.dropna()) >= 1 else price
    sigs.update({"SMA50": round(s50,2), "SMA200": round(s200,2), "Price": round(price,2)})
    total += 3
    if price > s50:  score += 1
    else:             score -= 1
    if price > s200: score += 1
    else:             score -= 1
    if s50 > s200:   score += 1
    else:             score -= 1

    # Bollinger
    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    upper = sma20 + 2 * std20
    lower = sma20 - 2 * std20
    bb_p  = (price - float(lower.iloc[-1])) / (float(upper.iloc[-1]) - float(lower.iloc[-1]) + 1e-9)
    sigs["BB_pos"] = round(bb_p, 2)
    total += 1
    if   bb_p < 0.2: score += 1
    elif bb_p > 0.8: score -= 1

    # Volume
    if "Volume" in hist.columns:
        vol    = hist["Volume"].squeeze()
        avg_v  = float(vol.rolling(20).mean().iloc[-1])
        last_v = float(vol.iloc[-1])
        vr     = last_v / avg_v if avg_v > 0 else 1
        sigs["Vol_ratio"] = round(vr, 2)
        total += 1
        if vr > 1.5 and price > float(close.iloc[-2]): score += 1

    # Momentum (5-day return)
    if len(close) >= 6:
        mom = (price / float(close.iloc[-6]) - 1) * 100
        sigs["Momentum_5d"] = round(mom, 2)
        total += 1
        if   mom >  5: score += 1
        elif mom < -5: score -= 1

    confidence = round(abs(score) / max(total, 1) * 100)

    if   score >= 5:  verdict = "STRONG BUY"
    elif score >= 2:  verdict = "BUY"
    elif score <= -5: verdict = "STRONG SELL"
    elif score <= -2: verdict = "SELL"
    else:             verdict = "HOLD"

    return {"signal": verdict, "score": score, "details": sigs, "confidence": confidence}


# ── AI Prediction using Claude API ────────────────────────────────────────────
def get_ai_prediction(ticker: str, indicators: dict, info: dict,
                       pnl_pct: float, signal: str, score: int,
                       api_key: str) -> str:
    """Call Claude API to generate a nuanced prediction narrative."""
    if not api_key:
        return None

    name     = info.get("longName") or info.get("shortName", ticker)
    sector   = info.get("sector", "N/A")
    mktcap   = info.get("marketCap")
    pe       = info.get("trailingPE")
    fpe      = info.get("forwardPE")
    target   = info.get("targetMeanPrice")
    rec      = info.get("recommendationMean")
    rec_key  = info.get("recommendationKey", "")
    price    = indicators.get("Price", "N/A")
    rsi      = indicators.get("RSI", "N/A")
    sma50    = indicators.get("SMA50", "N/A")
    sma200   = indicators.get("SMA200", "N/A")
    macd_h   = indicators.get("MACD_hist", "N/A")
    bb_pos   = indicators.get("BB_pos", "N/A")
    mom      = indicators.get("Momentum_5d", "N/A")

    prompt = f"""You are a senior portfolio analyst at a top-tier hedge fund. 
Analyze this stock and give a concise, actionable prediction (4-6 sentences max).

Stock: {ticker} ({name})
Sector: {sector}
Market Cap: {'${:,.0f}B'.format(mktcap/1e9) if mktcap else 'N/A'}
Current Price: {price}
My P&L on this position: {pnl_pct:+.1f}%

Technical indicators:
- RSI(14): {rsi}
- MACD Histogram: {macd_h}
- Price vs SMA50: {price} vs {sma50} ({'above' if isinstance(sma50,(int,float)) and isinstance(price,(int,float)) and price>sma50 else 'below'})
- Price vs SMA200: {price} vs {sma200} ({'above' if isinstance(sma200,(int,float)) and isinstance(price,(int,float)) and price>sma200 else 'below'})
- Bollinger Band position: {bb_pos} (0=lower band, 1=upper band)
- 5-day momentum: {mom}%

Fundamentals:
- Trailing P/E: {pe}
- Forward P/E: {fpe}
- Analyst mean target: {target}
- Analyst consensus: {rec_key} (score {rec}/5)

Technical signal: {signal} (score: {score:+d})

Give: 
1. A 1-sentence price outlook for next 30-90 days
2. The single biggest risk right now
3. The single biggest catalyst to watch
4. A clear verdict: BUY MORE / HOLD / TRIM / SELL with a one-line reason

Be blunt, specific, and data-driven. No generic disclaimers."""

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 400,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            return data["content"][0]["text"]
        else:
            return f"API error {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return f"Error calling Claude API: {e}"


# ── Data fetchers ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_ticker_data(ticker: str) -> dict:
    try:
        t    = yf.Ticker(ticker)
        inf  = t.info or {}
        hist = t.history(period="1y", interval="1d")
        price = (inf.get("currentPrice")
              or inf.get("regularMarketPrice")
              or inf.get("previousClose"))
        if price is None and not hist.empty:
            price = float(hist["Close"].iloc[-1])
        sig = compute_signals(hist)
        return {
            "ticker": ticker, "price": price, "info": inf,
            "hist": hist, "signal": sig["signal"],
            "score": sig["score"], "confidence": sig["confidence"],
            "indicators": sig["details"],
        }
    except Exception as e:
        return {"ticker": ticker, "price": None, "error": str(e),
                "signal": "HOLD", "score": 0, "confidence": 0, "indicators": {}}


@st.cache_data(ttl=600)
def fetch_news(ticker: str) -> list:
    try:
        t    = yf.Ticker(ticker)
        news = t.news or []
        items = []
        for n in news[:6]:
            ct    = n.get("content", {})
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


@st.cache_data(ttl=3600)
def fetch_earnings(ticker: str) -> dict:
    """Fetch upcoming earnings date and analyst consensus."""
    try:
        t   = yf.Ticker(ticker)
        inf = t.info or {}
        cal = t.calendar

        next_earnings = None
        if cal is not None and not cal.empty:
            # calendar is a DataFrame with dates as columns
            try:
                if hasattr(cal, 'columns'):
                    # New yfinance format: dict-like
                    if "Earnings Date" in cal.index:
                        val = cal.loc["Earnings Date"]
                        if hasattr(val, '__iter__'):
                            dates = [v for v in val if pd.notna(v)]
                            if dates:
                                next_earnings = str(dates[0])[:10]
                        else:
                            next_earnings = str(val)[:10]
            except:
                pass

        if next_earnings is None:
            ne = inf.get("nextFiscalYearEnd") or inf.get("mostRecentQuarter")
            if ne:
                next_earnings = datetime.fromtimestamp(ne).strftime("%Y-%m-%d") if isinstance(ne, (int,float)) else str(ne)[:10]

        # Consensus
        rec_mean = inf.get("recommendationMean")
        rec_key  = inf.get("recommendationKey", "").upper()
        num_analysts = inf.get("numberOfAnalystOpinions", 0)
        target_mean  = inf.get("targetMeanPrice")
        target_high  = inf.get("targetHighPrice")
        target_low   = inf.get("targetLowPrice")
        price        = inf.get("currentPrice") or inf.get("regularMarketPrice")

        upside = None
        if target_mean and price:
            upside = (target_mean / price - 1) * 100

        return {
            "next_earnings": next_earnings,
            "rec_mean":      rec_mean,
            "rec_key":       rec_key,
            "num_analysts":  num_analysts,
            "target_mean":   target_mean,
            "target_high":   target_high,
            "target_low":    target_low,
            "upside":        upside,
        }
    except Exception as e:
        return {"error": str(e)}


@st.cache_data(ttl=300)
def build_portfolio_summary(positions: dict) -> pd.DataFrame:
    rows = []
    for ticker, pos in positions.items():
        d      = fetch_ticker_data(ticker)
        price  = d.get("price")
        if price is None:
            continue
        shares = pos["shares"]
        ac     = pos["ac"]
        cv     = price * shares
        cb     = ac * shares
        pnl    = cv - cb
        pnl_p  = pnl / cb * 100 if cb else 0
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
            "Confidence": d.get("confidence", 0),
            "RSI":      d.get("indicators", {}).get("RSI", "-"),
            "SMA50":    d.get("indicators", {}).get("SMA50", "-"),
            "SMA200":   d.get("indicators", {}).get("SMA200", "-"),
        })
    return pd.DataFrame(rows)


# ── Signal chip HTML ───────────────────────────────────────────────────────────
def signal_chip(sig: str) -> str:
    css = sig.replace(" ", "-")
    return f'<span class="signal-chip chip-{css}">{sig}</span>'

def ticker_colored(ticker: str, sig: str) -> str:
    css = sig.replace(" ", "-")
    return f'<span class="ticker-{css}">{ticker}</span>'

def consensus_label(rec_key: str) -> str:
    rk = rec_key.upper()
    if "STRONG_BUY" in rk or "STRONGBUY" in rk: return ("STRONG BUY", "#00e676")
    if "BUY" in rk:    return ("BUY",   "#69f0ae")
    if "SELL" in rk:   return ("SELL",  "#ff5252")
    if "HOLD" in rk or "NEUTRAL" in rk: return ("HOLD", "#ffd740")
    return (rec_key or "N/A", "#aaa")


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    page = st.radio("Navigate", [
        "📊 Portfolio Overview",
        "🔍 Ticker Deep Dive",
        "🤖 AI Predictions",
        "📰 News Feed",
        "📉 Signals Summary",
        "💼 Trades Manager",
    ])
    st.markdown("---")
    if page in ("🔍 Ticker Deep Dive", "🤖 AI Predictions"):
        trades    = load_trades()
        positions = compute_positions(trades)
        selected  = st.selectbox("Select ticker", sorted(positions.keys()))
    st.markdown("---")

    # Claude API key input
    st.markdown("### 🤖 AI Predictions")
    api_key = st.text_input(
        "Anthropic API key",
        type="password",
        help="Get yours free at console.anthropic.com",
        placeholder="sk-ant-..."
    )
    if api_key:
        st.success("API key set ✓")
    else:
        st.caption("Add your key to enable AI predictions.")
    st.markdown("---")
    if st.button("🔄 Force Refresh"):
        st.cache_data.clear()
        st.rerun()
    st.caption("Data via Yahoo Finance · Refreshes every 5 min")


# ── Load current positions ─────────────────────────────────────────────────────
trades    = load_trades()
positions = compute_positions(trades)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Portfolio Overview
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Portfolio Overview":
    st.markdown("# 📊 TFSA Portfolio Dashboard")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · {len(positions)} positions")

    with st.spinner("Loading all positions…"):
        df = build_portfolio_summary(positions)

    if df.empty:
        st.error("No positions loaded. Check internet connection or add trades.")
        st.stop()

    total_val   = df["Mkt Value"].sum()
    total_cost  = df["Cost"].sum()
    total_pnl   = df["P&L $"].sum()
    total_pnl_p = total_pnl / total_cost * 100 if total_cost else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Portfolio Value", f"${total_val:,.0f}")
    c2.metric("Cost Basis",      f"${total_cost:,.0f}")
    c3.metric("Total P&L",       f"${total_pnl:,.0f}", delta=f"{total_pnl_p:+.1f}%")
    c4.metric("Active Positions",f"{len(df)}")

    # Signal distribution
    st.markdown("---")
    st.markdown("### 🚦 Signal Distribution")
    sig_counts = df["Signal"].value_counts()
    cols = st.columns(5)
    for i, (sig, color) in enumerate([
        ("STRONG BUY","#00e676"),("BUY","#69f0ae"),
        ("HOLD","#ffd740"),
        ("SELL","#ff5252"),("STRONG SELL","#ff1744"),
    ]):
        cnt = sig_counts.get(sig, 0)
        cols[i].markdown(
            f'<div style="background:#1c1f26;border-radius:10px;padding:12px;'
            f'text-align:center;border-top:3px solid {color}">'
            f'<div style="font-size:22px;font-weight:700;color:{color}">{cnt}</div>'
            f'<div style="font-size:11px;color:#aaa">{sig}</div></div>',
            unsafe_allow_html=True
        )

    # Table
    st.markdown("---")
    st.markdown("### 📋 All Positions")

    disp = df.sort_values("Mkt Value", ascending=False).copy()

    # Build colored HTML table
    rows_html = ""
    for _, row in disp.iterrows():
        sig      = row["Signal"]
        sig_css  = sig.replace(" ", "-")
        pnl_c    = "#00e676" if row["P&L %"] >= 0 else "#ff5252"
        price_vs = ""
        if isinstance(row["SMA50"], (int,float)) and isinstance(row["Price"], (int,float)):
            price_vs = "▲" if row["Price"] > row["SMA50"] else "▼"
        rows_html += f"""
        <tr>
          <td style="color:var(--ticker-col,{'#00e676' if 'BUY' in sig else '#ff5252' if 'SELL' in sig else '#ffd740'});font-weight:700">{row['Ticker']}</td>
          <td>${row['Price']:.2f}</td>
          <td>{row['Shares']:.2f}</td>
          <td>${row['AC']:.2f}</td>
          <td>${row['Mkt Value']:,.0f}</td>
          <td style="color:{pnl_c}">{row['P&L %']:+.1f}%</td>
          <td style="color:{pnl_c}">${row['P&L $']:,.0f}</td>
          <td><span class="signal-chip chip-{sig_css}">{sig}</span></td>
          <td>{row['RSI']}</td>
          <td>{row['Confidence']}%</td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-x:auto">
    <table style="width:100%;border-collapse:collapse;font-size:12px">
      <thead>
        <tr style="border-bottom:1px solid #333;color:#888;font-size:11px">
          <th style="padding:8px;text-align:left">Ticker</th>
          <th style="padding:8px">Price</th>
          <th style="padding:8px">Shares</th>
          <th style="padding:8px">Avg Cost</th>
          <th style="padding:8px">Mkt Value</th>
          <th style="padding:8px">P&L %</th>
          <th style="padding:8px">P&L $</th>
          <th style="padding:8px">Signal</th>
          <th style="padding:8px">RSI</th>
          <th style="padding:8px">Confidence</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)

    # Winners/Losers
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏆 Top 5 Winners")
        top5 = df.nlargest(5,"P&L %")[["Ticker","P&L %","Signal"]]
        for _,r in top5.iterrows():
            c = "#00e676" if r["P&L %"]>=0 else "#ff5252"
            sig_css = r["Signal"].replace(" ","-")
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'padding:7px 0;border-bottom:.5px solid #2d3139">'
                f'<span style="color:#00e676;font-weight:700">{r["Ticker"]}</span>'
                f'<span style="color:{c}">{r["P&L %"]:+.1f}%</span>'
                f'<span class="signal-chip chip-{sig_css}">{r["Signal"]}</span></div>',
                unsafe_allow_html=True
            )
    with col2:
        st.markdown("### ⚠️ Top 5 Losers")
        bot5 = df.nsmallest(5,"P&L %")[["Ticker","P&L %","Signal"]]
        for _,r in bot5.iterrows():
            c = "#00e676" if r["P&L %"]>=0 else "#ff5252"
            sig_css = r["Signal"].replace(" ","-")
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'padding:7px 0;border-bottom:.5px solid #2d3139">'
                f'<span style="color:#ff5252;font-weight:700">{r["Ticker"]}</span>'
                f'<span style="color:{c}">{r["P&L %"]:+.1f}%</span>'
                f'<span class="signal-chip chip-{sig_css}">{r["Signal"]}</span></div>',
                unsafe_allow_html=True
            )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Ticker Deep Dive
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Ticker Deep Dive":
    ticker = selected
    pos    = positions[ticker]
    st.markdown(f"# 🔍 {ticker}")

    with st.spinner(f"Loading {ticker}…"):
        d        = fetch_ticker_data(ticker)
        news     = fetch_news(ticker)
        earnings = fetch_earnings(ticker)

    price = d.get("price")
    if price is None:
        st.error(f"Could not fetch data for {ticker}.")
        st.stop()

    inf    = d.get("info", {})
    shares = pos["shares"]
    ac     = pos["ac"]
    cv     = price * shares
    cb     = ac * shares
    pnl    = cv - cb
    pnl_p  = pnl / cb * 100 if cb else 0
    sig    = d.get("signal","HOLD")
    score  = d.get("score",0)
    conf   = d.get("confidence",0)
    ind    = d.get("indicators",{})

    sig_color = {
        "STRONG BUY":"#00e676","BUY":"#69f0ae",
        "HOLD":"#ffd740","SELL":"#ff5252","STRONG SELL":"#ff1744"
    }.get(sig,"#aaa")

    # Header
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Price",       f"${price:.2f}")
    c2.metric("Avg Cost",    f"${ac:.2f}")
    c3.metric("Mkt Value",   f"${cv:,.0f}")
    c4.metric("P&L",         f"${pnl:,.0f}", delta=f"{pnl_p:+.1f}%")
    c5.markdown(
        f'<div style="background:#1c1f26;border-radius:10px;padding:12px;text-align:center;'
        f'border:2px solid {sig_color};margin-top:4px">'
        f'<div style="font-size:11px;color:#aaa">SIGNAL ({conf}% conf.)</div>'
        f'<div style="font-size:20px;font-weight:900;color:{sig_color}">{sig}</div>'
        f'<div style="font-size:11px;color:#aaa">Score: {score:+d}/10</div></div>',
        unsafe_allow_html=True
    )

    # ── Earnings + Consensus row ──
    st.markdown("---")
    ec1, ec2, ec3, ec4 = st.columns(4)

    ne = earnings.get("next_earnings","N/A")
    with ec1:
        days_to = None
        if ne and ne != "N/A":
            try:
                dt = datetime.strptime(ne[:10], "%Y-%m-%d")
                days_to = (dt - datetime.now()).days
            except: pass
        label = f"🗓️ {ne}" if ne and ne != "N/A" else "🗓️ N/A"
        sublabel = f"{days_to} days away" if days_to is not None and days_to >= 0 else ("past" if days_to is not None else "")
        color_e = "#ffd740" if days_to is not None and 0 <= days_to <= 30 else "#aaa"
        st.markdown(
            f'<div class="earnings-box">'
            f'<div style="font-size:11px;color:#888">Next Earnings</div>'
            f'<div style="font-size:15px;font-weight:700;color:{color_e}">{ne or "N/A"}</div>'
            f'<div style="font-size:11px;color:#888">{sublabel}</div></div>',
            unsafe_allow_html=True
        )

    rec_key = earnings.get("rec_key","")
    rec_lbl, rec_col = consensus_label(rec_key)
    n_anal  = earnings.get("num_analysts",0)
    with ec2:
        st.markdown(
            f'<div class="earnings-box">'
            f'<div style="font-size:11px;color:#888">Analyst Consensus ({n_anal} analysts)</div>'
            f'<div style="font-size:18px;font-weight:900;color:{rec_col}">{rec_lbl}</div>'
            f'<div style="font-size:11px;color:#888">Rating: {earnings.get("rec_mean","N/A")}/5</div></div>',
            unsafe_allow_html=True
        )

    tgt = earnings.get("target_mean")
    upside = earnings.get("upside")
    with ec3:
        up_col = "#00e676" if upside and upside > 0 else "#ff5252"
        st.markdown(
            f'<div class="earnings-box">'
            f'<div style="font-size:11px;color:#888">Analyst Price Target</div>'
            f'<div style="font-size:18px;font-weight:700;color:#fff">'
            f'{"${:.2f}".format(tgt) if tgt else "N/A"}</div>'
            f'<div style="font-size:12px;color:{up_col}">'
            f'{"Upside: {:+.1f}%".format(upside) if upside is not None else ""}</div></div>',
            unsafe_allow_html=True
        )

    tgt_h = earnings.get("target_high")
    tgt_l = earnings.get("target_low")
    with ec4:
        st.markdown(
            f'<div class="earnings-box">'
            f'<div style="font-size:11px;color:#888">Target Range</div>'
            f'<div style="font-size:15px;font-weight:700;color:#fff">'
            f'{"${:.2f}".format(tgt_l) if tgt_l else "N/A"}'
            f' → {"${:.2f}".format(tgt_h) if tgt_h else "N/A"}</div>'
            f'<div style="font-size:11px;color:#888">Low / High</div></div>',
            unsafe_allow_html=True
        )

    # ── AI Prediction ──
    st.markdown("---")
    st.markdown("### 🤖 AI Analysis")
    if api_key:
        ai_btn = st.button(f"Generate AI prediction for {ticker}", key="ai_btn")
        if ai_btn or st.session_state.get(f"ai_{ticker}"):
            with st.spinner("Claude is analyzing…"):
                ai_text = get_ai_prediction(
                    ticker, ind, inf, pnl_p, sig, score, api_key
                )
            st.session_state[f"ai_{ticker}"] = ai_text
            if ai_text:
                st.markdown(
                    f'<div class="ai-box">'
                    f'<div class="ai-title">🤖 Claude AI Analysis — {ticker}</div>'
                    f'<div style="font-size:13px;line-height:1.75;color:#e0e0e0">'
                    f'{ai_text.replace(chr(10),"<br>")}</div></div>',
                    unsafe_allow_html=True
                )
    else:
        st.info("Add your Anthropic API key in the sidebar to enable AI predictions.")

    # ── Charts ──
    st.markdown("---")
    tab_chart, tab_ind = st.tabs(["📈 Price Chart (1Y)", "📊 Indicators"])

    with tab_chart:
        hist = d.get("hist")
        if hist is not None and not hist.empty:
            chart_df = hist["Close"].squeeze().reset_index()
            chart_df.columns = ["Date","Close"]
            st.line_chart(chart_df.set_index("Date")["Close"])
        else:
            st.info("No chart data available.")

    with tab_ind:
        rsi_v  = ind.get("RSI","N/A")
        sma50  = ind.get("SMA50","N/A")
        sma200 = ind.get("SMA200","N/A")
        macd_h = ind.get("MACD_hist","N/A")
        bb_p   = ind.get("BB_pos","N/A")
        vol_r  = ind.get("Vol_ratio","N/A")
        mom    = ind.get("Momentum_5d","N/A")

        rows_i = [
            ("RSI (14)", rsi_v,
             "🟢 Oversold — bullish" if isinstance(rsi_v,(int,float)) and rsi_v<30
             else "🔴 Overbought — bearish" if isinstance(rsi_v,(int,float)) and rsi_v>70
             else "🟡 Neutral"),
            ("MACD Histogram", macd_h,
             "🟢 Bullish momentum" if isinstance(macd_h,(int,float)) and macd_h>0
             else "🔴 Bearish momentum"),
            ("vs SMA 50",
             f"{'ABOVE ▲' if isinstance(sma50,(int,float)) and price>sma50 else 'BELOW ▼'} (${sma50})",
             "🟢 Bullish" if isinstance(sma50,(int,float)) and price>sma50 else "🔴 Bearish"),
            ("vs SMA 200",
             f"{'ABOVE ▲' if isinstance(sma200,(int,float)) and price>sma200 else 'BELOW ▼'} (${sma200})",
             "🟢 Bullish" if isinstance(sma200,(int,float)) and price>sma200 else "🔴 Bearish"),
            ("Bollinger Band pos.", bb_p,
             "🟢 Near lower band — buy zone" if isinstance(bb_p,(int,float)) and bb_p<0.2
             else "🔴 Near upper band — sell zone" if isinstance(bb_p,(int,float)) and bb_p>0.8
             else "🟡 Mid-range"),
            ("5-day Momentum", f"{mom}%" if isinstance(mom,(int,float)) else mom,
             "🟢 Strong positive" if isinstance(mom,(int,float)) and mom>5
             else "🔴 Strong negative" if isinstance(mom,(int,float)) and mom<-5
             else "🟡 Flat"),
            ("Volume ratio", vol_r,
             "🟢 High volume" if isinstance(vol_r,(int,float)) and vol_r>1.5 else "🟡 Normal"),
        ]
        df_i = pd.DataFrame(rows_i, columns=["Indicator","Value","Interpretation"])
        st.dataframe(df_i, use_container_width=True, hide_index=True)

    # ── Company info ──
    st.markdown("---")
    st.markdown("### 🏢 Company Info")
    name     = inf.get("longName") or inf.get("shortName", ticker)
    sector   = inf.get("sector","N/A")
    industry = inf.get("industry","N/A")
    mktcap   = inf.get("marketCap")
    pe       = inf.get("trailingPE")
    fpe      = inf.get("forwardPE")
    beta     = inf.get("beta")
    div_y    = inf.get("dividendYield")

    ci1,ci2,ci3 = st.columns(3)
    ci1.markdown(f"**{name}**\n\nSector: {sector}\n\nIndustry: {industry}")
    ci2.markdown(
        f"Market Cap: {'${:,.1f}B'.format(mktcap/1e9) if mktcap else 'N/A'}\n\n"
        f"P/E trailing: {round(pe,1) if pe else 'N/A'}\n\n"
        f"P/E forward: {round(fpe,1) if fpe else 'N/A'}"
    )
    ci3.markdown(
        f"Beta: {round(beta,2) if beta else 'N/A'}\n\n"
        f"Dividend yield: {'{:.2%}'.format(div_y) if div_y else 'N/A'}\n\n"
        f"52W: ${inf.get('fiftyTwoWeekLow','N/A')} → ${inf.get('fiftyTwoWeekHigh','N/A')}"
    )

    # ── News ──
    st.markdown("---")
    st.markdown(f"### 📰 Latest News — {ticker}")
    if news:
        for n in news:
            link_html = (f'<a href="{n["link"]}" target="_blank" '
                         f'style="color:#5c7cfa;text-decoration:none">{n["title"]}</a>'
                         if n.get("link") else n["title"])
            st.markdown(
                f'<div class="news-item">{link_html}'
                f'<div style="font-size:11px;color:#888;margin-top:3px">{n.get("date","")}</div></div>',
                unsafe_allow_html=True
            )
    else:
        st.info("No recent news found.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — AI Predictions (batch)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🤖 AI Predictions":
    st.markdown("# 🤖 AI Predictions")

    if not api_key:
        st.warning("Add your Anthropic API key in the sidebar to use this feature.")
        st.stop()

    st.info("Select tickers and click Generate. Each call uses ~400 tokens (~$0.002).")

    tickers_sel = st.multiselect(
        "Choose tickers to analyze",
        sorted(positions.keys()),
        default=sorted(positions.keys())[:5]
    )

    if st.button("🚀 Generate AI Predictions", type="primary"):
        for tk in tickers_sel:
            with st.spinner(f"Analyzing {tk}…"):
                d      = fetch_ticker_data(tk)
                pos_tk = positions[tk]
                price  = d.get("price",0)
                cb     = pos_tk["ac"] * pos_tk["shares"]
                cv     = (price or 0) * pos_tk["shares"]
                pnl_p  = (cv - cb) / cb * 100 if cb else 0
                ai_txt = get_ai_prediction(
                    tk, d.get("indicators",{}), d.get("info",{}),
                    pnl_p, d.get("signal","HOLD"), d.get("score",0), api_key
                )
            sig     = d.get("signal","HOLD")
            sig_css = sig.replace(" ","-")
            sig_col = {"STRONG BUY":"#00e676","BUY":"#69f0ae","HOLD":"#ffd740",
                       "SELL":"#ff5252","STRONG SELL":"#ff1744"}.get(sig,"#aaa")
            st.markdown(
                f'<div class="ai-box" style="margin-bottom:16px">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">'
                f'<div class="ai-title">{tk} — {d.get("info",{}).get("shortName",tk)}</div>'
                f'<span class="signal-chip chip-{sig_css}">{sig} (score {d.get("score",0):+d})</span></div>'
                f'<div style="font-size:13px;line-height:1.75;color:#e0e0e0">'
                f'{(ai_txt or "No response").replace(chr(10),"<br>")}</div></div>',
                unsafe_allow_html=True
            )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — News Feed
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📰 News Feed":
    st.markdown("# 📰 Portfolio News Feed")
    tickers_sel = st.multiselect(
        "Select tickers", sorted(positions.keys()),
        default=list(sorted(positions.keys()))[:8]
    )
    if not tickers_sel:
        st.warning("Select at least one ticker.")
        st.stop()
    for tk in tickers_sel:
        news = fetch_news(tk)
        if news:
            d   = fetch_ticker_data(tk)
            sig = d.get("signal","HOLD")
            sig_css = sig.replace(" ","-")
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px;margin:14px 0 6px">'
                f'<span style="font-size:16px;font-weight:700">{tk}</span>'
                f'<span class="signal-chip chip-{sig_css}">{sig}</span></div>',
                unsafe_allow_html=True
            )
            for n in news[:3]:
                lh = (f'<a href="{n["link"]}" target="_blank" '
                      f'style="color:#5c7cfa;text-decoration:none">{n["title"]}</a>'
                      if n.get("link") else n["title"])
                st.markdown(
                    f'<div class="news-item">{lh}'
                    f'<div style="font-size:11px;color:#888;margin-top:3px">{n.get("date","")}</div></div>',
                    unsafe_allow_html=True
                )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — Signals Summary
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📉 Signals Summary":
    st.markdown("# 📉 Technical Signals — All Positions")

    with st.spinner("Computing signals…"):
        df = build_portfolio_summary(positions)

    if df.empty:
        st.error("No data.")
        st.stop()

    sig_filter = st.selectbox(
        "Filter", ["ALL","STRONG BUY","BUY","HOLD","SELL","STRONG SELL"]
    )
    filt = df if sig_filter=="ALL" else df[df["Signal"]==sig_filter]
    filt = filt.sort_values("Score", ascending=False)

    for _, row in filt.iterrows():
        sig     = row["Signal"]
        sig_css = sig.replace(" ","-")
        color   = {"STRONG BUY":"#00e676","BUY":"#69f0ae","HOLD":"#ffd740",
                   "SELL":"#ff5252","STRONG SELL":"#ff1744"}.get(sig,"#aaa")
        pnl_col = "#00e676" if row["P&L %"]>=0 else "#ff5252"
        st.markdown(
            f'<div style="background:#1c1f26;border-radius:10px;padding:12px 16px;'
            f'margin-bottom:7px;border-left:4px solid {color};'
            f'display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">'
            f'<div>'
            f'<span style="font-size:15px;font-weight:700;color:{color}">{row["Ticker"]}</span>'
            f' <span style="font-size:12px;color:#aaa">RSI: {row["RSI"]} | '
            f'SMA50: ${row["SMA50"]} | Confidence: {row["Confidence"]}%</span>'
            f'</div>'
            f'<div style="text-align:right">'
            f'<span class="signal-chip chip-{sig_css}">{sig}</span>'
            f' <span style="font-size:12px;color:{pnl_col};margin-left:8px">{row["P&L %"]:+.1f}%</span>'
            f'<br><span style="font-size:11px;color:#888">Score: {row["Score"]:+d} | '
            f'Value: ${row["Mkt Value"]:,.0f}</span>'
            f'</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🟢 Buy signals:**")
        for _,r in df[df["Signal"].isin(["BUY","STRONG BUY"])].sort_values("Score",ascending=False).iterrows():
            st.markdown(f"- **{r['Ticker']}** · Score {r['Score']:+d} · RSI {r['RSI']} · {r['P&L %']:+.1f}%")
    with c2:
        st.markdown("**🔴 Sell signals:**")
        for _,r in df[df["Signal"].isin(["SELL","STRONG SELL"])].sort_values("Score").iterrows():
            st.markdown(f"- **{r['Ticker']}** · Score {r['Score']:+d} · RSI {r['RSI']} · {r['P&L %']:+.1f}%")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — Trades Manager
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💼 Trades Manager":
    st.markdown("# 💼 Trades Manager")
    st.caption("All trades are saved locally in trades.json. Your positions update automatically.")

    # ── Add new trade ──
    st.markdown("### ➕ Add New Trade")
    with st.form("add_trade", clear_on_submit=True):
        fc1, fc2, fc3, fc4, fc5, fc6 = st.columns([2,1,1,1,1,2])
        with fc1:
            new_ticker = st.text_input("Ticker", placeholder="e.g. NVDA.TO").upper().strip()
        with fc2:
            new_side = st.selectbox("Side", ["BUY","SELL"])
        with fc3:
            new_shares = st.number_input("Shares", min_value=0.0001, value=10.0, format="%.4f")
        with fc4:
            new_price = st.number_input("Price", min_value=0.0001, value=100.0, format="%.4f")
        with fc5:
            new_date = st.date_input("Date", value=datetime.today())
        with fc6:
            new_note = st.text_input("Note (optional)", placeholder="e.g. Earnings dip buy")

        submitted = st.form_submit_button("✅ Add Trade", type="primary")

        if submitted:
            if not new_ticker:
                st.error("Ticker is required.")
            else:
                trd = load_trades()
                trd.append({
                    "id":     f"{new_ticker}_{datetime.now().timestamp():.0f}",
                    "date":   str(new_date),
                    "ticker": new_ticker,
                    "side":   new_side,
                    "shares": new_shares,
                    "price":  new_price,
                    "note":   new_note,
                })
                save_trades(trd)
                st.cache_data.clear()
                st.success(f"✅ {new_side} {new_shares} {new_ticker} @ ${new_price:.4f} added!")
                st.rerun()

    # ── Current positions ──
    st.markdown("---")
    st.markdown("### 📋 Current Positions (computed from trades)")
    pos_rows = []
    for tk, p in sorted(positions.items()):
        pos_rows.append({"Ticker": tk, "Shares": p["shares"], "Avg Cost": p["ac"],
                         "Est. Cost Basis": p["shares"]*p["ac"]})
    if pos_rows:
        df_pos = pd.DataFrame(pos_rows)
        df_pos["Est. Cost Basis"] = df_pos["Est. Cost Basis"].map("${:,.2f}".format)
        df_pos["Avg Cost"]        = df_pos["Avg Cost"].map("${:.4f}".format)
        df_pos["Shares"]          = df_pos["Shares"].map("{:.4f}".format)
        st.dataframe(df_pos, use_container_width=True, hide_index=True)

    # ── Trade history ──
    st.markdown("---")
    st.markdown("### 📜 Trade History")

    all_trades = load_trades()
    # Filter
    tf1, tf2 = st.columns([3,1])
    with tf1:
        search = st.text_input("Search by ticker", placeholder="e.g. NVDA")
    with tf2:
        side_f = st.selectbox("Side filter", ["ALL","BUY","SELL"])

    filtered = all_trades
    if search:
        filtered = [t for t in filtered if search.upper() in t["ticker"].upper()]
    if side_f != "ALL":
        filtered = [t for t in filtered if t["side"] == side_f]
    filtered = sorted(filtered, key=lambda x: x.get("date",""), reverse=True)

    if filtered:
        for i, t in enumerate(filtered):
            col_d = "#69f0ae" if t["side"]=="BUY" else "#ff5252"
            total = float(t["shares"]) * float(t["price"])
            with st.container():
                cc1,cc2,cc3,cc4,cc5,cc6 = st.columns([2,1,1,1,1,1])
                cc1.markdown(f'<span style="font-weight:700;font-size:14px">{t["ticker"]}</span>', unsafe_allow_html=True)
                cc2.markdown(f'<span style="color:{col_d};font-weight:700">{t["side"]}</span>', unsafe_allow_html=True)
                cc3.write(f'{float(t["shares"]):.4f} sh')
                cc4.write(f'@ ${float(t["price"]):.4f}')
                cc5.write(f'${total:,.2f}')
                cc6.write(t.get("date",""))
                if t.get("note"):
                    st.caption(f'📝 {t["note"]}')

                # Delete button
                if st.button(f"🗑️ Delete", key=f"del_{t['id']}_{i}"):
                    updated = [x for x in all_trades if x["id"] != t["id"]]
                    save_trades(updated)
                    st.cache_data.clear()
                    st.rerun()
                st.markdown('<hr style="border:none;border-top:.5px solid #2d3139;margin:4px 0">', unsafe_allow_html=True)
    else:
        st.info("No trades found.")

    # ── Export ──
    st.markdown("---")
    st.markdown("### 📤 Export")
    ec1, ec2 = st.columns(2)
    with ec1:
        df_export = pd.DataFrame(all_trades)
        if not df_export.empty:
            st.download_button(
                "⬇️ Download trades.csv",
                df_export.to_csv(index=False),
                file_name="trades.csv",
                mime="text/csv"
            )
    with ec2:
        st.download_button(
            "⬇️ Download trades.json",
            json.dumps(all_trades, indent=2),
            file_name="trades.json",
            mime="application/json"
        )
