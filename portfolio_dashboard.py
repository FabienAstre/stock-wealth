"""
TFSA Portfolio Dashboard v3
- Sortable columns on every table
- ChatGPT AI predictions (GPT-4o)
- Fixed earnings dates & analyst consensus
- Extra trading tools: Fear & Greed, sector heatmap, correlation matrix,
  position sizer, stop-loss calculator, dividend calendar
- No trades manager (removed)
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TFSA Dashboard v3",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.main{background:#0e1117}
div[data-testid="metric-container"]{
    background:#1c1f26;border:1px solid #2d3139;
    border-radius:10px;padding:12px 16px}
.signal-chip{display:inline-block;padding:3px 10px;border-radius:20px;
    font-size:11px;font-weight:700;letter-spacing:.04em;white-space:nowrap}
.chip-STRONG-BUY {background:#003d1f;color:#00e676;border:1px solid #00e676}
.chip-BUY        {background:#003d1f;color:#69f0ae;border:1px solid #69f0ae}
.chip-HOLD       {background:#3d3000;color:#ffd740;border:1px solid #ffd740}
.chip-SELL       {background:#3d0000;color:#ff5252;border:1px solid #ff5252}
.chip-STRONG-SELL{background:#3d0000;color:#ff1744;border:1px solid #ff1744}
.news-item{background:#1c1f26;border-left:3px solid #3d5afe;
    padding:10px 14px;margin-bottom:8px;border-radius:0 8px 8px 0}
.ai-box{background:linear-gradient(135deg,#0d1b2a,#1a1f35);
    border:1px solid #3d5afe;border-radius:12px;padding:18px 22px;margin:12px 0}
.earn-box{background:#1a2035;border:1px solid #5c6bc0;
    border-radius:10px;padding:14px 18px;margin:6px 0}
.tool-card{background:#1c1f26;border:1px solid #2d3139;
    border-radius:12px;padding:16px 20px;margin-bottom:12px}
/* sortable table */
.sort-table{width:100%;border-collapse:collapse;font-size:12px}
.sort-table th{padding:8px 10px;text-align:left;border-bottom:1px solid #333;
    color:#aaa;font-size:11px;cursor:pointer;user-select:none;
    background:#161920;position:sticky;top:0;white-space:nowrap}
.sort-table th:hover{color:#fff;background:#1e2230}
.sort-table td{padding:6px 10px;border-bottom:.5px solid #1e2230}
.sort-table tr:hover td{background:#1a1f2e}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# PORTFOLIO
# ─────────────────────────────────────────────────────────────────
PORTFOLIO = {
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
    "DRUG.CN": {"shares": 8,        "ac": 73.92},
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

# ─────────────────────────────────────────────────────────────────
# TECHNICAL SIGNALS
# ─────────────────────────────────────────────────────────────────
def compute_signals(hist: pd.DataFrame) -> dict:
    if hist is None or len(hist) < 26:
        return {"signal": "HOLD", "score": 0, "details": {}, "confidence": 0}

    close  = hist["Close"].squeeze()
    score  = 0
    max_sc = 0
    ind    = {}

    # RSI
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    rsi   = 100 - (100 / (1 + rs))
    rv    = float(rsi.iloc[-1]) if len(rsi.dropna()) >= 1 else 50.0
    ind["RSI"] = round(rv, 1)
    max_sc += 2
    if   rv < 30: score += 2
    elif rv < 45: score += 1
    elif rv > 70: score -= 2
    elif rv > 55: score -= 1

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd  = ema12 - ema26
    sig_l = macd.ewm(span=9,  adjust=False).mean()
    mh    = macd - sig_l
    mv    = float(mh.iloc[-1])
    mp    = float(mh.iloc[-2]) if len(mh) > 1 else mv
    ind["MACD_hist"] = round(mv, 4)
    max_sc += 2
    if   mv > 0 and mp <= 0: score += 2
    elif mv < 0 and mp >= 0: score -= 2
    elif mv > 0: score += 1
    elif mv < 0: score -= 1

    # SMA 50 / 200
    sma50  = close.rolling(50).mean()
    sma200 = close.rolling(200).mean()
    price  = float(close.iloc[-1])
    s50    = float(sma50.dropna().iloc[-1])  if len(sma50.dropna())  >= 1 else price
    s200   = float(sma200.dropna().iloc[-1]) if len(sma200.dropna()) >= 1 else price
    ind.update({"SMA50": round(s50,2), "SMA200": round(s200,2), "Price": round(price,2)})
    max_sc += 3
    score += 1 if price > s50  else -1
    score += 1 if price > s200 else -1
    score += 1 if s50   > s200 else -1

    # Bollinger
    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    upper = sma20 + 2*std20
    lower = sma20 - 2*std20
    bb_p  = (price - float(lower.iloc[-1])) / (float(upper.iloc[-1]) - float(lower.iloc[-1]) + 1e-9)
    ind["BB_pos"] = round(bb_p, 2)
    max_sc += 1
    if   bb_p < 0.2: score += 1
    elif bb_p > 0.8: score -= 1

    # Volume
    if "Volume" in hist.columns:
        vol   = hist["Volume"].squeeze()
        avgv  = float(vol.rolling(20).mean().iloc[-1])
        lastv = float(vol.iloc[-1])
        vr    = lastv / avgv if avgv > 0 else 1.0
        ind["Vol_ratio"] = round(vr, 2)
        max_sc += 1
        if vr > 1.5 and price > float(close.iloc[-2]): score += 1

    # 5-day momentum
    if len(close) >= 6:
        mom = (price / float(close.iloc[-6]) - 1) * 100
        ind["Mom_5d"] = round(mom, 2)
        max_sc += 1
        if   mom >  5: score += 1
        elif mom < -5: score -= 1

    confidence = round(abs(score) / max(max_sc, 1) * 100)

    if   score >= 5:  verdict = "STRONG BUY"
    elif score >= 2:  verdict = "BUY"
    elif score <= -5: verdict = "STRONG SELL"
    elif score <= -2: verdict = "SELL"
    else:             verdict = "HOLD"

    return {"signal": verdict, "score": score,
            "details": ind, "confidence": confidence}

# ─────────────────────────────────────────────────────────────────
# DATA FETCHERS
# ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_ticker(ticker: str) -> dict:
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
        return {"ticker": ticker, "price": price, "info": inf,
                "hist": hist, "signal": sig["signal"],
                "score": sig["score"], "confidence": sig["confidence"],
                "indicators": sig["details"]}
    except Exception as e:
        return {"ticker": ticker, "price": None, "error": str(e),
                "signal": "HOLD", "score": 0, "confidence": 0,
                "indicators": {}, "hist": pd.DataFrame(), "info": {}}


@st.cache_data(ttl=600)
def fetch_news(ticker: str) -> list:
    try:
        items = []
        for n in (yf.Ticker(ticker).news or [])[:6]:
            ct    = n.get("content", {})
            title = ct.get("title") or n.get("title", "")
            link  = ct.get("canonicalUrl", {}).get("url") or n.get("link", "")
            pub   = ct.get("pubDate") or ""
            if pub:
                try: pub = datetime.fromisoformat(pub.replace("Z","")).strftime("%b %d, %Y")
                except: pass
            if title:
                items.append({"title": title, "link": link, "date": pub})
        return items
    except:
        return []


@st.cache_data(ttl=1800)
def fetch_earnings_consensus(ticker: str) -> dict:
    """
    Robust fetcher for earnings date, analyst consensus, and price targets.
    Tries multiple yfinance attributes in order.
    """
    result = {
        "next_earnings": None,
        "rec_key": None, "rec_mean": None,
        "num_analysts": 0,
        "target_mean": None, "target_high": None, "target_low": None,
        "upside": None,
    }
    try:
        t   = yf.Ticker(ticker)
        inf = t.info or {}

        # ── Earnings date ── multiple fallback paths
        next_earn = None

        # Path 1: earningsTimestamp in info
        et = inf.get("earningsTimestamp")
        if et and isinstance(et, (int, float)) and et > 0:
            try:
                dt = datetime.utcfromtimestamp(et)
                if dt > datetime.utcnow() - timedelta(days=1):
                    next_earn = dt.strftime("%Y-%m-%d")
            except: pass

        # Path 2: earningsDate list in info
        if not next_earn:
            ed_raw = inf.get("earningsDate")
            if ed_raw:
                if isinstance(ed_raw, (list, tuple)) and len(ed_raw) > 0:
                    try:
                        v = ed_raw[0]
                        if isinstance(v, (int, float)):
                            dt = datetime.utcfromtimestamp(v)
                        else:
                            dt = pd.Timestamp(v).to_pydatetime()
                        if dt > datetime.utcnow() - timedelta(days=1):
                            next_earn = dt.strftime("%Y-%m-%d")
                    except: pass
                elif isinstance(ed_raw, str):
                    next_earn = ed_raw[:10]

        # Path 3: t.calendar
        if not next_earn:
            try:
                cal = t.calendar
                if cal is not None:
                    # could be dict or DataFrame
                    if isinstance(cal, dict):
                        ed = cal.get("Earnings Date") or cal.get("earningsDate")
                        if ed:
                            if isinstance(ed, (list, tuple)):
                                dates = [d for d in ed if pd.notna(d)]
                                if dates:
                                    next_earn = str(dates[0])[:10]
                            else:
                                next_earn = str(ed)[:10]
                    elif isinstance(cal, pd.DataFrame) and not cal.empty:
                        for col in cal.columns:
                            for row_key in ["Earnings Date", "earningsDate"]:
                                try:
                                    val = cal.at[row_key, col]
                                    if pd.notna(val):
                                        next_earn = str(val)[:10]
                                        break
                                except: pass
                            if next_earn: break
            except: pass

        # Path 4: earnings_dates table (most reliable for future dates)
        if not next_earn:
            try:
                ed_df = t.earnings_dates
                if ed_df is not None and not ed_df.empty:
                    future = ed_df[ed_df.index > pd.Timestamp.now(tz="UTC")]
                    if not future.empty:
                        next_earn = future.index[-1].strftime("%Y-%m-%d")
            except: pass

        result["next_earnings"] = next_earn

        # ── Analyst consensus & targets ──
        result["rec_mean"]     = inf.get("recommendationMean")
        result["rec_key"]      = (inf.get("recommendationKey") or "").replace("_"," ").upper()
        result["num_analysts"] = inf.get("numberOfAnalystOpinions") or 0
        result["target_mean"]  = inf.get("targetMeanPrice")
        result["target_high"]  = inf.get("targetHighPrice")
        result["target_low"]   = inf.get("targetLowPrice")

        price = inf.get("currentPrice") or inf.get("regularMarketPrice")
        if result["target_mean"] and price:
            result["upside"] = (result["target_mean"] / price - 1) * 100

    except Exception as e:
        result["error"] = str(e)

    return result


@st.cache_data(ttl=300)
def build_summary(portfolio: dict) -> pd.DataFrame:
    rows = []
    for tk, pos in portfolio.items():
        d     = fetch_ticker(tk)
        price = d.get("price")
        if not price:
            continue
        cv   = price * pos["shares"]
        cb   = pos["ac"] * pos["shares"]
        pnl  = cv - cb
        pnlp = pnl / cb * 100 if cb else 0
        ind  = d.get("indicators", {})
        rows.append({
            "Ticker":    tk,
            "Price":     round(price, 2),
            "Shares":    pos["shares"],
            "Avg Cost":  pos["ac"],
            "Mkt Value": round(cv, 2),
            "Cost":      round(cb, 2),
            "P&L $":     round(pnl, 2),
            "P&L %":     round(pnlp, 2),
            "Signal":    d.get("signal", "HOLD"),
            "Score":     d.get("score", 0),
            "Conf %":    d.get("confidence", 0),
            "RSI":       ind.get("RSI", "-"),
            "MACD":      ind.get("MACD_hist", "-"),
            "BB Pos":    ind.get("BB_pos", "-"),
            "Mom 5d%":   ind.get("Mom_5d", "-"),
            "SMA50":     ind.get("SMA50", "-"),
            "SMA200":    ind.get("SMA200", "-"),
            "Vol Ratio": ind.get("Vol_ratio", "-"),
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────
# CHATGPT AI
# ─────────────────────────────────────────────────────────────────
def gpt_predict(ticker, ind, info, pnl_pct, signal, score, api_key, model="gpt-4o") -> str:
    if not api_key:
        return None
    name   = info.get("longName") or info.get("shortName", ticker)
    sector = info.get("sector","N/A")
    mktcap = info.get("marketCap")
    pe     = info.get("trailingPE")
    fpe    = info.get("forwardPE")
    target = info.get("targetMeanPrice")
    rec    = info.get("recommendationMean")
    rec_k  = info.get("recommendationKey","")
    price  = ind.get("Price","N/A")

    prompt = f"""You are a senior hedge fund analyst. Analyze this stock position and give a sharp, 
data-driven verdict in exactly this format:

**30-90 Day Outlook:** (1 sentence — direction and magnitude)
**Biggest Risk:** (1 sentence — specific, not generic)
**Key Catalyst to Watch:** (1 sentence — specific event or metric)
**Verdict:** BUY MORE / HOLD / TRIM / SELL — (one-line reason)

Stock: {ticker} ({name})
Sector: {sector}  |  Market Cap: {'${:,.1f}B'.format(mktcap/1e9) if mktcap else 'N/A'}
Price: {price}  |  My P&L: {pnl_pct:+.1f}%

Technicals: RSI={ind.get('RSI','N/A')} | MACD hist={ind.get('MACD_hist','N/A')} | 
BB pos={ind.get('BB_pos','N/A')} | 5d mom={ind.get('Mom_5d','N/A')}% | 
Price vs SMA50={'Above' if isinstance(ind.get('SMA50'),float) and isinstance(price,float) and price>ind.get('SMA50',0) else 'Below'}
Signal: {signal} (score {score:+d})

Fundamentals: P/E={pe} | Fwd P/E={fpe} | Analyst target={target} | Consensus={rec_k} ({rec}/5)

Be blunt. No disclaimers."""

    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}",
                     "Content-Type": "application/json"},
            json={"model": model, "max_tokens": 350,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        return f"OpenAI error {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return f"Error: {e}"


# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────
SIG_COLOR = {
    "STRONG BUY":"#00e676","BUY":"#69f0ae",
    "HOLD":"#ffd740","SELL":"#ff5252","STRONG SELL":"#ff1744",
}

def sig_chip(sig):
    css = sig.replace(" ","-")
    col = SIG_COLOR.get(sig,"#aaa")
    return f'<span class="signal-chip chip-{css}">{sig}</span>'

def ticker_color(tk, sig):
    col = SIG_COLOR.get(sig,"#ccc")
    return f'<b style="color:{col}">{tk}</b>'

def fmt_opt(v, fmt="$.2f"):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "N/A"
    if fmt == "$.2f":    return f"${v:,.2f}"
    if fmt == "$.1fB":   return f"${v/1e9:,.1f}B"
    if fmt == "+.1f%":   return f"{v:+.1f}%"
    if fmt == ".1f":     return f"{v:.1f}"
    if fmt == ".2f":     return f"{v:.2f}"
    return str(v)

def consensus_style(rec_key):
    rk = (rec_key or "").upper()
    if "STRONG BUY" in rk or "STRONGBUY" in rk: return ("#00e676", "STRONG BUY")
    if "BUY"   in rk: return ("#69f0ae", "BUY")
    if "SELL"  in rk: return ("#ff5252", "SELL")
    if "HOLD"  in rk or "NEUTRAL" in rk: return ("#ffd740", "HOLD")
    return ("#aaa", rec_key or "N/A")


# ─────────────────────────────────────────────────────────────────
# SORTABLE TABLE (JS-powered)
# ─────────────────────────────────────────────────────────────────
def sortable_table(df_in: pd.DataFrame, table_id="tbl", height=600):
    """Render a JS-sortable HTML table with colored tickers & signal chips."""
    cols = list(df_in.columns)
    header = "".join(
        f'<th onclick="sortTable(\'{table_id}\',{i})" title="Click to sort">'
        f'{c} <span style="font-size:9px">⇅</span></th>'
        for i, c in enumerate(cols)
    )

    def cell(col, val, sig="HOLD"):
        if col == "Ticker":
            return f'<td>{ticker_color(val, sig)}</td>'
        if col == "Signal":
            return f'<td>{sig_chip(val)}</td>'
        if col == "P&L %":
            c = "#00e676" if isinstance(val, (int,float)) and val >= 0 else "#ff5252"
            txt = f"{val:+.2f}%" if isinstance(val,(int,float)) else val
            return f'<td style="color:{c};font-weight:600">{txt}</td>'
        if col == "P&L $":
            c = "#00e676" if isinstance(val,(int,float)) and val >= 0 else "#ff5252"
            txt = f"${val:,.0f}" if isinstance(val,(int,float)) else val
            return f'<td style="color:{c}">{txt}</td>'
        if col in ("Mkt Value","Cost","Price","Avg Cost"):
            txt = f"${val:,.2f}" if isinstance(val,(int,float)) else val
            return f'<td>{txt}</td>'
        if col in ("Shares",):
            return f'<td>{val:.4f}</td>'
        return f'<td>{val}</td>'

    rows_html = ""
    for _, row in df_in.iterrows():
        sig = row.get("Signal","HOLD")
        rows_html += "<tr>" + "".join(cell(c, row[c], sig) for c in cols) + "</tr>"

    html = f"""
<div style="overflow-x:auto;max-height:{height}px;overflow-y:auto">
<table class="sort-table" id="{table_id}">
  <thead><tr>{header}</tr></thead>
  <tbody id="{table_id}_body">{rows_html}</tbody>
</table>
</div>
<script>
(function(){{
  var dir_{table_id} = {{}};
  window.sortTable = window.sortTable || function(id, col){{
    var tb = document.getElementById(id+'_body');
    if(!tb) return;
    var rows = Array.from(tb.querySelectorAll('tr'));
    dir_{table_id}[col] = !(dir_{table_id}[col]);
    var asc = dir_{table_id}[col];
    rows.sort(function(a,b){{
      var av = a.cells[col] ? a.cells[col].innerText.replace(/[$%+,]/g,'') : '';
      var bv = b.cells[col] ? b.cells[col].innerText.replace(/[$%+,]/g,'') : '';
      var an = parseFloat(av), bn = parseFloat(bv);
      if(!isNaN(an) && !isNaN(bn)) return asc ? an-bn : bn-an;
      return asc ? av.localeCompare(bv) : bv.localeCompare(av);
    }});
    rows.forEach(function(r){{ tb.appendChild(r); }});
  }};
}})();
</script>
"""
    st.components.v1.html(html, height=height+40, scrolling=False)


# ─────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    page = st.radio("Navigate", [
        "📊 Portfolio Overview",
        "🔍 Ticker Deep Dive",
        "🤖 AI Predictions",
        "📰 News Feed",
        "📉 Signals Summary",
        "🛠️ Trading Tools",
    ])
    st.markdown("---")
    if page in ("🔍 Ticker Deep Dive", "🤖 AI Predictions"):
        selected = st.selectbox("Ticker", sorted(PORTFOLIO.keys()))
    st.markdown("---")
    st.markdown("### 🤖 ChatGPT AI")
    gpt_key = st.text_input("OpenAI API key", type="password",
                             help="platform.openai.com → API Keys",
                             placeholder="sk-...")
    gpt_model = st.selectbox("Model", ["gpt-4o","gpt-4o-mini","gpt-4-turbo"])
    if gpt_key: st.success("API key set ✓")
    else: st.caption("Add key to enable AI predictions.")
    st.markdown("---")
    if st.button("🔄 Refresh data"):
        st.cache_data.clear()
        st.rerun()
    st.caption("Yahoo Finance · refreshes every 5 min")


# ══════════════════════════════════════════════════════════════════
# PAGE 1 — PORTFOLIO OVERVIEW
# ══════════════════════════════════════════════════════════════════
if page == "📊 Portfolio Overview":
    st.markdown("# 📊 TFSA Portfolio Dashboard")
    st.caption(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · {len(PORTFOLIO)} positions")

    with st.spinner("Loading portfolio…"):
        df = build_summary(PORTFOLIO)

    if df.empty:
        st.error("No data loaded.")
        st.stop()

    tv  = df["Mkt Value"].sum()
    tc  = df["Cost"].sum()
    tpl = df["P&L $"].sum()
    tpp = tpl/tc*100 if tc else 0

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Portfolio Value",  f"${tv:,.0f}")
    c2.metric("Cost Basis",       f"${tc:,.0f}")
    c3.metric("Total P&L",        f"${tpl:,.0f}", delta=f"{tpp:+.1f}%")
    c4.metric("Positions loaded", str(len(df)))

    # Signal distribution
    st.markdown("---")
    sc = df["Signal"].value_counts()
    cols5 = st.columns(5)
    for i,(sig,col) in enumerate([("STRONG BUY","#00e676"),("BUY","#69f0ae"),
                                    ("HOLD","#ffd740"),("SELL","#ff5252"),("STRONG SELL","#ff1744")]):
        cnt = sc.get(sig,0)
        cols5[i].markdown(
            f'<div style="background:#1c1f26;border-radius:10px;padding:12px;'
            f'text-align:center;border-top:3px solid {col}">'
            f'<div style="font-size:22px;font-weight:700;color:{col}">{cnt}</div>'
            f'<div style="font-size:11px;color:#aaa">{sig}</div></div>',
            unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 All Positions — click any column header to sort")

    disp = df[["Ticker","Price","Shares","Avg Cost","Mkt Value",
               "P&L $","P&L %","Signal","Score","Conf %","RSI","MACD",
               "BB Pos","Mom 5d%","Vol Ratio"]].sort_values("Mkt Value", ascending=False)
    sortable_table(disp, "main_tbl", height=620)

    st.markdown("---")
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("### 🏆 Top 5 Winners")
        for _,r in df.nlargest(5,"P&L %").iterrows():
            c = "#00e676" if r["P&L %"]>=0 else "#ff5252"
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;padding:7px 0;'
                f'border-bottom:.5px solid #2d3139">'
                f'{ticker_color(r["Ticker"],r["Signal"])}'
                f'<span style="color:{c}">{r["P&L %"]:+.2f}%</span>'
                f'{sig_chip(r["Signal"])}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown("### ⚠️ Top 5 Losers")
        for _,r in df.nsmallest(5,"P&L %").iterrows():
            c = "#00e676" if r["P&L %"]>=0 else "#ff5252"
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;padding:7px 0;'
                f'border-bottom:.5px solid #2d3139">'
                f'{ticker_color(r["Ticker"],r["Signal"])}'
                f'<span style="color:{c}">{r["P&L %"]:+.2f}%</span>'
                f'{sig_chip(r["Signal"])}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# PAGE 2 — TICKER DEEP DIVE
# ══════════════════════════════════════════════════════════════════
elif page == "🔍 Ticker Deep Dive":
    ticker = selected
    pos    = PORTFOLIO[ticker]
    st.markdown(f"# 🔍 {ticker}")

    with st.spinner(f"Loading {ticker}…"):
        d    = fetch_ticker(ticker)
        news = fetch_news(ticker)
        ec   = fetch_earnings_consensus(ticker)

    price = d.get("price")
    if not price:
        st.error(f"No data for {ticker}.")
        st.stop()

    inf   = d.get("info",{})
    cv    = price * pos["shares"]
    cb    = pos["ac"] * pos["shares"]
    pnl   = cv - cb
    pnlp  = pnl/cb*100 if cb else 0
    sig   = d.get("signal","HOLD")
    score = d.get("score",0)
    conf  = d.get("confidence",0)
    ind   = d.get("indicators",{})
    sc    = SIG_COLOR.get(sig,"#aaa")

    # Header metrics
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Price",     f"${price:.2f}")
    c2.metric("Avg Cost",  f"${pos['ac']:.2f}")
    c3.metric("Mkt Value", f"${cv:,.0f}")
    c4.metric("P&L",       f"${pnl:,.0f}", delta=f"{pnlp:+.1f}%")
    c5.markdown(
        f'<div style="background:#1c1f26;border-radius:10px;padding:12px;'
        f'text-align:center;border:2px solid {sc};margin-top:4px">'
        f'<div style="font-size:10px;color:#aaa">SIGNAL · {conf}% conf</div>'
        f'<div style="font-size:18px;font-weight:900;color:{sc}">{sig}</div>'
        f'<div style="font-size:10px;color:#aaa">Score {score:+d}/10</div></div>',
        unsafe_allow_html=True)

    # ── Earnings + consensus ──────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🗓️ Earnings & Analyst Data")

    ea1,ea2,ea3,ea4 = st.columns(4)

    # Next earnings
    ne = ec.get("next_earnings")
    days_away = None
    earn_col  = "#aaa"
    if ne:
        try:
            dt = datetime.strptime(ne[:10],"%Y-%m-%d")
            days_away = (dt - datetime.now()).days
            earn_col  = "#ffd740" if 0<=days_away<=30 else ("#ff5252" if days_away<0 else "#69f0ae")
        except: pass
    with ea1:
        st.markdown(
            f'<div class="earn-box">'
            f'<div style="font-size:10px;color:#888">Next Earnings</div>'
            f'<div style="font-size:16px;font-weight:700;color:{earn_col}">'
            f'{ne if ne else "Not found"}</div>'
            f'<div style="font-size:11px;color:#888">'
            f'{"In "+str(days_away)+" days" if days_away is not None and days_away>=0 else ("Past" if days_away is not None else "")}'
            f'</div></div>', unsafe_allow_html=True)

    # Consensus
    rec_col, rec_lbl = consensus_style(ec.get("rec_key",""))
    n_anal = ec.get("num_analysts",0)
    rm     = ec.get("rec_mean")
    with ea2:
        st.markdown(
            f'<div class="earn-box">'
            f'<div style="font-size:10px;color:#888">Analyst Consensus ({n_anal} analysts)</div>'
            f'<div style="font-size:18px;font-weight:900;color:{rec_col}">{rec_lbl}</div>'
            f'<div style="font-size:11px;color:#888">Score: {fmt_opt(rm,".2f")}/5</div>'
            f'</div>', unsafe_allow_html=True)

    # Target
    tgt  = ec.get("target_mean")
    up   = ec.get("upside")
    up_c = "#00e676" if up and up>0 else "#ff5252"
    with ea3:
        st.markdown(
            f'<div class="earn-box">'
            f'<div style="font-size:10px;color:#888">Mean Price Target</div>'
            f'<div style="font-size:18px;font-weight:700;color:#fff">{fmt_opt(tgt,"$.2f")}</div>'
            f'<div style="font-size:12px;color:{up_c}">'
            f'{"Upside "+fmt_opt(up,"+.1f%") if up is not None else ""}</div>'
            f'</div>', unsafe_allow_html=True)

    # Range
    tlo = ec.get("target_low")
    thi = ec.get("target_high")
    with ea4:
        st.markdown(
            f'<div class="earn-box">'
            f'<div style="font-size:10px;color:#888">Target Range (Low → High)</div>'
            f'<div style="font-size:16px;font-weight:700;color:#fff">'
            f'{fmt_opt(tlo,"$.2f")} → {fmt_opt(thi,"$.2f")}</div>'
            f'</div>', unsafe_allow_html=True)

    # ── AI Prediction ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🤖 ChatGPT Analysis")
    if gpt_key:
        if st.button(f"Generate GPT prediction for {ticker}"):
            with st.spinner("GPT is thinking…"):
                txt = gpt_predict(ticker, ind, inf, pnlp, sig, score, gpt_key, gpt_model)
            st.session_state[f"gpt_{ticker}"] = txt
        if f"gpt_{ticker}" in st.session_state:
            st.markdown(
                f'<div class="ai-box"><div style="font-size:11px;color:#7986cb;'
                f'font-weight:700;margin-bottom:8px">GPT-4o · {ticker}</div>'
                f'<div style="font-size:13px;line-height:1.8;color:#e0e0e0">'
                f'{st.session_state[f"gpt_{ticker}"].replace(chr(10),"<br>")}'
                f'</div></div>', unsafe_allow_html=True)
    else:
        st.info("Enter your OpenAI API key in the sidebar to enable AI predictions.")

    # ── Chart + Indicators ────────────────────────────────────────
    st.markdown("---")
    tab1, tab2 = st.tabs(["📈 Price Chart (1Y)", "📊 Indicators"])
    with tab1:
        hist = d.get("hist")
        if hist is not None and not hist.empty:
            cd = hist["Close"].squeeze().reset_index()
            cd.columns = ["Date","Close"]
            st.line_chart(cd.set_index("Date"))
        else:
            st.info("No chart data.")
    with tab2:
        rsi_v  = ind.get("RSI","N/A")
        sma50  = ind.get("SMA50","N/A")
        sma200 = ind.get("SMA200","N/A")
        macdh  = ind.get("MACD_hist","N/A")
        bbp    = ind.get("BB_pos","N/A")
        volr   = ind.get("Vol_ratio","N/A")
        mom    = ind.get("Mom_5d","N/A")

        tbl_data = [
            ("RSI (14)", rsi_v,
             "🟢 Oversold" if isinstance(rsi_v,(int,float)) and rsi_v<30
             else "🔴 Overbought" if isinstance(rsi_v,(int,float)) and rsi_v>70 else "🟡 Neutral"),
            ("MACD Histogram", macdh,
             "🟢 Bullish" if isinstance(macdh,(int,float)) and macdh>0 else "🔴 Bearish"),
            ("vs SMA 50",
             f"{'ABOVE ▲' if isinstance(sma50,(int,float)) and price>sma50 else 'BELOW ▼'} (${sma50})",
             "🟢" if isinstance(sma50,(int,float)) and price>sma50 else "🔴"),
            ("vs SMA 200",
             f"{'ABOVE ▲' if isinstance(sma200,(int,float)) and price>sma200 else 'BELOW ▼'} (${sma200})",
             "🟢" if isinstance(sma200,(int,float)) and price>sma200 else "🔴"),
            ("Bollinger Pos", bbp,
             "🟢 Buy zone" if isinstance(bbp,(int,float)) and bbp<0.2
             else "🔴 Sell zone" if isinstance(bbp,(int,float)) and bbp>0.8 else "🟡 Mid"),
            ("5d Momentum", f"{mom}%", "🟢 Strong" if isinstance(mom,(int,float)) and mom>5
             else "🔴 Weak" if isinstance(mom,(int,float)) and mom<-5 else "🟡 Flat"),
            ("Volume Ratio", volr,
             "🟢 High volume" if isinstance(volr,(int,float)) and volr>1.5 else "🟡 Normal"),
        ]
        st.dataframe(pd.DataFrame(tbl_data, columns=["Indicator","Value","Signal"]),
                     use_container_width=True, hide_index=True)

    # ── Company info + News ───────────────────────────────────────
    st.markdown("---")
    ci1,ci2,ci3 = st.columns(3)
    name     = inf.get("longName") or inf.get("shortName",ticker)
    sector   = inf.get("sector","N/A")
    industry = inf.get("industry","N/A")
    mktcap   = inf.get("marketCap")
    pe       = inf.get("trailingPE")
    fpe      = inf.get("forwardPE")
    beta     = inf.get("beta")
    divy     = inf.get("dividendYield")
    w52h     = inf.get("fiftyTwoWeekHigh")
    w52l     = inf.get("fiftyTwoWeekLow")
    ci1.markdown(f"**{name}**\n\nSector: {sector}\n\nIndustry: {industry}")
    ci2.markdown(
        f"Market Cap: {fmt_opt(mktcap,'$.1fB')}\n\n"
        f"P/E trailing: {fmt_opt(pe,'.1f')}\n\n"
        f"P/E forward: {fmt_opt(fpe,'.1f')}")
    ci3.markdown(
        f"Beta: {fmt_opt(beta,'.2f')}\n\n"
        f"Dividend: {'{:.2%}'.format(divy) if divy else 'N/A'}\n\n"
        f"52W: {fmt_opt(w52l,'$.2f')} → {fmt_opt(w52h,'$.2f')}")

    st.markdown("---")
    st.markdown(f"### 📰 News — {ticker}")
    for n in (news or []):
        lh = (f'<a href="{n["link"]}" target="_blank" style="color:#5c7cfa;text-decoration:none">'
              f'{n["title"]}</a>' if n.get("link") else n["title"])
        st.markdown(
            f'<div class="news-item">{lh}'
            f'<div style="font-size:10px;color:#888;margin-top:3px">{n.get("date","")}</div></div>',
            unsafe_allow_html=True)
    if not news:
        st.info("No recent news.")


# ══════════════════════════════════════════════════════════════════
# PAGE 3 — AI PREDICTIONS (BATCH)
# ══════════════════════════════════════════════════════════════════
elif page == "🤖 AI Predictions":
    st.markdown("# 🤖 ChatGPT Batch Predictions")
    if not gpt_key:
        st.warning("Enter your OpenAI API key in the sidebar.")
        st.stop()

    tks = st.multiselect("Select tickers", sorted(PORTFOLIO.keys()),
                          default=sorted(PORTFOLIO.keys())[:5])
    st.caption(f"Model: {gpt_model} · ~$0.002 per ticker with gpt-4o-mini")

    if st.button("🚀 Generate all predictions", type="primary"):
        for tk in tks:
            with st.spinner(f"Analyzing {tk}…"):
                d    = fetch_ticker(tk)
                pos  = PORTFOLIO[tk]
                pr   = d.get("price",0) or 0
                cb   = pos["ac"]*pos["shares"]
                cv   = pr*pos["shares"]
                pnlp = (cv-cb)/cb*100 if cb else 0
                txt  = gpt_predict(tk, d.get("indicators",{}),
                                   d.get("info",{}), pnlp,
                                   d.get("signal","HOLD"),
                                   d.get("score",0), gpt_key, gpt_model)
            sig     = d.get("signal","HOLD")
            sig_css = sig.replace(" ","-")
            sc_     = SIG_COLOR.get(sig,"#aaa")
            st.markdown(
                f'<div class="ai-box" style="margin-bottom:14px">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:8px">'
                f'<span style="font-size:14px;font-weight:700;color:{sc_}">{tk}</span>'
                f'{sig_chip(sig)}</div>'
                f'<div style="font-size:13px;line-height:1.8;color:#e0e0e0">'
                f'{(txt or "No response").replace(chr(10),"<br>")}</div></div>',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# PAGE 4 — NEWS FEED
# ══════════════════════════════════════════════════════════════════
elif page == "📰 News Feed":
    st.markdown("# 📰 Portfolio News Feed")
    tks = st.multiselect("Select tickers", sorted(PORTFOLIO.keys()),
                          default=list(sorted(PORTFOLIO.keys()))[:8])
    if not tks:
        st.warning("Select at least one ticker.")
        st.stop()
    for tk in tks:
        news = fetch_news(tk)
        if not news: continue
        d   = fetch_ticker(tk)
        sig = d.get("signal","HOLD")
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;margin:14px 0 6px">'
            f'{ticker_color(tk,sig)} {sig_chip(sig)}</div>',
            unsafe_allow_html=True)
        for n in news[:3]:
            lh = (f'<a href="{n["link"]}" target="_blank" style="color:#5c7cfa;text-decoration:none">'
                  f'{n["title"]}</a>' if n.get("link") else n["title"])
            st.markdown(
                f'<div class="news-item">{lh}'
                f'<div style="font-size:10px;color:#888;margin-top:3px">{n.get("date","")}</div></div>',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# PAGE 5 — SIGNALS SUMMARY
# ══════════════════════════════════════════════════════════════════
elif page == "📉 Signals Summary":
    st.markdown("# 📉 Signals Summary")

    with st.spinner("Computing signals…"):
        df = build_summary(PORTFOLIO)

    if df.empty:
        st.error("No data.")
        st.stop()

    sf = st.selectbox("Filter", ["ALL","STRONG BUY","BUY","HOLD","SELL","STRONG SELL"])
    filt = df if sf=="ALL" else df[df["Signal"]==sf]
    filt = filt.sort_values("Score",ascending=False)

    cols_show = ["Ticker","Price","P&L %","Signal","Score","Conf %",
                 "RSI","MACD","BB Pos","Mom 5d%","SMA50","SMA200"]
    sortable_table(filt[cols_show].reset_index(drop=True), "sig_tbl", height=580)

    st.markdown("---")
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("**🟢 Buy signals:**")
        buys = df[df["Signal"].isin(["BUY","STRONG BUY"])].sort_values("Score",ascending=False)
        for _,r in buys.iterrows():
            st.markdown(
                f'{ticker_color(r["Ticker"],r["Signal"])} {sig_chip(r["Signal"])} '
                f'Score {r["Score"]:+d} · RSI {r["RSI"]} · {r["P&L %"]:+.1f}%',
                unsafe_allow_html=True)
    with c2:
        st.markdown("**🔴 Sell signals:**")
        sells = df[df["Signal"].isin(["SELL","STRONG SELL"])].sort_values("Score")
        for _,r in sells.iterrows():
            st.markdown(
                f'{ticker_color(r["Ticker"],r["Signal"])} {sig_chip(r["Signal"])} '
                f'Score {r["Score"]:+d} · RSI {r["RSI"]} · {r["P&L %"]:+.1f}%',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# PAGE 6 — TRADING TOOLS
# ══════════════════════════════════════════════════════════════════
elif page == "🛠️ Trading Tools":
    st.markdown("# 🛠️ Trading Tools")

    tool = st.selectbox("Choose tool", [
        "📐 Position Sizer",
        "🛑 Stop-Loss & Take-Profit Calculator",
        "📊 Correlation Matrix",
        "💰 Dividend Calendar",
        "🔥 Sector Heatmap",
        "📈 52-Week Range Tracker",
        "⚖️ Risk / Reward Calculator",
        "🧾 Portfolio Concentration Check",
    ])

    # ── POSITION SIZER ───────────────────────────────────────────
    if tool == "📐 Position Sizer":
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.markdown("### 📐 Position Sizer")
        st.markdown("How many shares should you buy based on your risk tolerance?")
        tc1,tc2,tc3 = st.columns(3)
        portfolio_val = tc1.number_input("Portfolio value ($)", value=57829, step=1000)
        risk_pct      = tc2.number_input("Max risk per trade (%)", value=2.0, step=0.5, min_value=0.1, max_value=10.0)
        entry_price   = tc3.number_input("Entry price ($)", value=100.0, step=1.0)
        stop_loss     = tc1.number_input("Stop-loss price ($)", value=92.0, step=1.0)
        target_price  = tc2.number_input("Target price ($)", value=115.0, step=1.0)
        commission    = tc3.number_input("Commission per trade ($)", value=0.0, step=1.0)

        if entry_price > stop_loss > 0:
            risk_amt  = portfolio_val * risk_pct / 100
            risk_per  = entry_price - stop_loss
            shares    = risk_amt / risk_per
            position  = shares * entry_price
            pos_pct   = position / portfolio_val * 100
            rr        = (target_price - entry_price) / risk_per if risk_per > 0 else 0
            profit    = (target_price - entry_price) * shares - commission*2
            loss_max  = risk_amt + commission*2

            st.markdown("---")
            r1,r2,r3,r4 = st.columns(4)
            r1.metric("Shares to buy",      f"{shares:.1f}")
            r2.metric("Position size",      f"${position:,.0f}")
            r3.metric("% of portfolio",     f"{pos_pct:.1f}%")
            r4.metric("Risk/Reward ratio",  f"{rr:.2f}x")
            r5,r6 = st.columns(2)
            r5.metric("Max loss",   f"${loss_max:,.0f}", delta=f"-{risk_pct:.1f}%")
            r6.metric("Max profit", f"${profit:,.0f}",   delta=f"+{profit/portfolio_val*100:.1f}%")

            if rr < 1.5:
                st.warning("⚠️ Risk/reward below 1.5x — consider adjusting target or stop-loss.")
            elif rr >= 3:
                st.success("✅ Excellent risk/reward ratio (≥3x).")
            if pos_pct > 5:
                st.warning(f"⚠️ Position is {pos_pct:.1f}% of portfolio — above 5% single-position limit.")
        else:
            st.info("Set entry price above stop-loss to see results.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── STOP-LOSS CALCULATOR ──────────────────────────────────────
    elif tool == "🛑 Stop-Loss & Take-Profit Calculator":
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.markdown("### 🛑 Stop-Loss & Take-Profit Calculator")

        tk_sel  = st.selectbox("Pick a position", sorted(PORTFOLIO.keys()))
        pos_sl  = PORTFOLIO[tk_sel]
        d_sl    = fetch_ticker(tk_sel)
        price_sl= d_sl.get("price",0) or pos_sl["ac"]
        ind_sl  = d_sl.get("indicators",{})

        st.markdown(f"**Current price:** ${price_sl:.2f} · **Your avg cost:** ${pos_sl['ac']:.2f}")

        col_sl1, col_sl2 = st.columns(2)
        method = col_sl1.selectbox("Stop-loss method",
                    ["% below entry","ATR-based (2x)","Support (manual)","Trailing %"])
        rr_target = col_sl2.selectbox("Risk/Reward target", ["1.5x","2x","2.5x","3x","4x"])
        rr_mult   = float(rr_target.replace("x",""))

        entry = st.number_input("Entry / current price ($)", value=float(price_sl), step=0.5)

        if method == "% below entry":
            sl_pct = st.slider("Stop-loss %", 2.0, 20.0, 7.0, 0.5)
            sl_p   = entry * (1 - sl_pct/100)
        elif method == "ATR-based (2x)":
            hist_sl = d_sl.get("hist")
            atr_val = 0
            if hist_sl is not None and len(hist_sl) >= 14:
                h = hist_sl["High"].squeeze()
                l = hist_sl["Low"].squeeze()
                c = hist_sl["Close"].squeeze()
                tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
                atr_val = float(tr.rolling(14).mean().iloc[-1])
            sl_p = entry - 2*atr_val
            st.info(f"ATR(14) = ${atr_val:.2f} · Stop = entry − 2×ATR = ${sl_p:.2f}")
        elif method == "Support (manual)":
            sl_p = st.number_input("Support / stop price ($)", value=entry*0.93, step=0.5)
        else:  # trailing
            sl_pct = st.slider("Trailing stop %", 2.0, 20.0, 8.0, 0.5)
            sl_p   = entry * (1 - sl_pct/100)

        risk_per = entry - sl_p
        tp1      = entry + rr_mult * risk_per
        tp2      = entry + (rr_mult*1.5) * risk_per

        r1,r2,r3 = st.columns(3)
        r1.metric("Stop-loss",    f"${sl_p:.2f}", delta=f"{(sl_p/entry-1)*100:.1f}%")
        r2.metric(f"TP1 ({rr_target})", f"${tp1:.2f}", delta=f"+{(tp1/entry-1)*100:.1f}%")
        r3.metric(f"TP2 ({rr_mult*1.5:.1f}x)", f"${tp2:.2f}", delta=f"+{(tp2/entry-1)*100:.1f}%")

        shares_held = pos_sl["shares"]
        st.markdown(f"""
| | Price | $ on {shares_held:.1f} sh |
|---|---|---|
| **Stop-loss** | ${sl_p:.2f} | **-${risk_per*shares_held:,.0f}** |
| **Take Profit 1** | ${tp1:.2f} | **+${(tp1-entry)*shares_held:,.0f}** |
| **Take Profit 2** | ${tp2:.2f} | **+${(tp2-entry)*shares_held:,.0f}** |
""")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── CORRELATION MATRIX ────────────────────────────────────────
    elif tool == "📊 Correlation Matrix":
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Correlation Matrix")
        st.caption("Shows how your positions move together. High correlation = less diversification.")

        top_tickers = sorted(PORTFOLIO.keys())
        sel_tickers = st.multiselect("Select up to 15 tickers", top_tickers,
                                     default=list(top_tickers)[:12])
        if len(sel_tickers) < 2:
            st.warning("Select at least 2 tickers.")
        else:
            with st.spinner("Fetching price data…"):
                price_data = {}
                for tk in sel_tickers:
                    d_c = fetch_ticker(tk)
                    h   = d_c.get("hist")
                    if h is not None and not h.empty:
                        price_data[tk] = h["Close"].squeeze()
            if price_data:
                df_prices = pd.DataFrame(price_data).dropna()
                df_ret    = df_prices.pct_change().dropna()
                corr      = df_ret.corr().round(2)

                # Color-coded heatmap via st.dataframe with background gradient
                def color_corr(val):
                    if val >= 0.8:  return "background-color:#3d0000;color:#ff5252"
                    if val >= 0.5:  return "background-color:#3d2200;color:#ffa726"
                    if val <= -0.3: return "background-color:#003d1f;color:#00e676"
                    return ""
                st.dataframe(
                    corr.style.applymap(color_corr).format("{:.2f}"),
                    use_container_width=True)
                st.caption("🔴 >0.8 = highly correlated (move together) · 🟢 <-0.3 = negatively correlated (hedge)")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── DIVIDEND CALENDAR ─────────────────────────────────────────
    elif tool == "💰 Dividend Calendar":
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.markdown("### 💰 Dividend Calendar")

        divs = []
        with st.spinner("Fetching dividend data…"):
            for tk, pos_d in PORTFOLIO.items():
                d_d  = fetch_ticker(tk)
                inf_d= d_d.get("info",{})
                dy   = inf_d.get("dividendYield")
                dr   = inf_d.get("dividendRate")
                exd  = inf_d.get("exDividendDate")
                price_d = d_d.get("price") or 0
                if dy and dy > 0:
                    annual = (dr or 0) * pos_d["shares"]
                    ex_str = ""
                    if exd:
                        try: ex_str = datetime.utcfromtimestamp(exd).strftime("%Y-%m-%d")
                        except: pass
                    divs.append({
                        "Ticker":        tk,
                        "Yield %":       round(dy*100, 2),
                        "Annual Rate $": round(dr or 0, 4),
                        "Your Annual $": round(annual, 2),
                        "Ex-Div Date":   ex_str or "N/A",
                        "Shares":        pos_d["shares"],
                    })

        if divs:
            df_div = pd.DataFrame(divs).sort_values("Yield %", ascending=False)
            total_divs = df_div["Your Annual $"].sum()
            st.metric("Total annual dividend income", f"${total_divs:,.2f}")
            st.dataframe(df_div, use_container_width=True, hide_index=True)
        else:
            st.info("No dividend-paying stocks found in portfolio (data may be limited for some tickers).")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── SECTOR HEATMAP ────────────────────────────────────────────
    elif tool == "🔥 Sector Heatmap":
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.markdown("### 🔥 Sector Heatmap by P&L")

        with st.spinner("Building heatmap…"):
            df_hm = build_summary(PORTFOLIO)

        if not df_hm.empty:
            sector_map = {
                "VFV.TO":"Core ETF","ZCN.TO":"Core ETF","XEF.TO":"Core ETF",
                "VEE.TO":"Core ETF","ZJPN.TO":"Core ETF","XSU.TO":"Core ETF","XID.TO":"Core ETF",
                "NVDA.TO":"AI/Semis","AMZN.TO":"Mega Tech","MSFT.TO":"Mega Tech",
                "AAPL.TO":"Mega Tech","META.TO":"Mega Tech","ASML.TO":"AI/Semis",
                "CRWV":"AI Infra","APLD":"AI Infra","BBAI":"AI Infra",
                "SOUN":"AI Infra","HELP":"AI Infra","NXT":"AI Infra",
                "OKLO":"Nuclear","NNE":"Nuclear","CEGS.TO":"Nuclear",
                "RGTI":"Quantum","QBTS":"Quantum",
                "RXRX":"Biotech","CMPS":"Biotech","RARE":"Biotech",
                "IMVT":"Biotech","ABCL":"Biotech","DRUG.CN":"Biotech","TEM":"Biotech",
                "LUNR":"Space","RDW":"Space","MDA.TO":"Space","JOBY":"Space",
                "LMT.TO":"Defense",
                "ENB.TO":"Energy","BEP-UN.TO":"Energy","CU.TO":"Energy","EOSE":"Energy",
                "BAM.TO":"Financials","BRK.TO":"Financials","NU":"Financials","TOI.V":"Financials",
                "WPM.TO":"Precious Metals","CGL.TO":"Precious Metals",
                "COPP.TO":"Materials","TMC":"Materials","PHOS.CN":"Materials",
                "PNG.V":"Materials","ONE.V":"Materials","SCD.V":"Materials",
                "AEHR":"Semis","NVTS":"Semis",
                "RDDT":"Consumer","TSLA.TO":"Consumer",
                "ISRG.NE":"MedTech",
                "VNM":"Emerging Mkts",
                "CLBT":"Other","APPS.NE":"Other","CRCL":"Other","WELL.TO":"Other",
            }
            df_hm["Sector"] = df_hm["Ticker"].map(sector_map).fillna("Other")
            sec_grp = df_hm.groupby("Sector").agg(
                Total_Value=("Mkt Value","sum"),
                Total_PnL=("P&L $","sum"),
                PnL_Pct=("P&L %","mean"),
                Count=("Ticker","count")
            ).reset_index().sort_values("Total_Value",ascending=False)

            for _,row in sec_grp.iterrows():
                pnl_c  = "#00e676" if row["PnL_Pct"]>=0 else "#ff5252"
                bar_w  = min(row["Total_Value"]/df_hm["Mkt Value"].sum()*100*4, 100)
                bar_c  = "#00e676" if row["PnL_Pct"]>=0 else "#ff5252"
                st.markdown(
                    f'<div style="background:#1c1f26;border-radius:8px;padding:10px 14px;'
                    f'margin-bottom:6px;border-left:4px solid {bar_c}">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center">'
                    f'<span style="font-weight:600;font-size:13px">{row["Sector"]}</span>'
                    f'<span style="font-size:12px;color:#aaa">{int(row["Count"])} positions · '
                    f'${row["Total_Value"]:,.0f}</span>'
                    f'<span style="font-size:13px;font-weight:700;color:{pnl_c}">'
                    f'{row["PnL_Pct"]:+.1f}% avg · ${row["Total_PnL"]:+,.0f}</span></div>'
                    f'<div style="margin-top:6px;height:6px;background:#2d3139;border-radius:3px">'
                    f'<div style="width:{bar_w:.0f}%;height:100%;background:{bar_c};border-radius:3px"></div>'
                    f'</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── 52-WEEK RANGE TRACKER ─────────────────────────────────────
    elif tool == "📈 52-Week Range Tracker":
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.markdown("### 📈 52-Week Range Tracker")
        st.caption("Where is each stock sitting in its 52-week range? Near highs = extended. Near lows = potential value.")

        with st.spinner("Loading…"):
            rows_52 = []
            for tk in sorted(PORTFOLIO.keys()):
                d52 = fetch_ticker(tk)
                inf52 = d52.get("info",{})
                lo  = inf52.get("fiftyTwoWeekLow")
                hi  = inf52.get("fiftyTwoWeekHigh")
                pr  = d52.get("price")
                if lo and hi and pr and hi > lo:
                    pos52 = (pr - lo)/(hi - lo)*100
                    rows_52.append({"Ticker":tk,"Price":pr,"52W Low":lo,
                                    "52W High":hi,"Range Pos %":round(pos52,1),
                                    "Signal":d52.get("signal","HOLD")})

        if rows_52:
            df52 = pd.DataFrame(rows_52).sort_values("Range Pos %")
            for _,r in df52.iterrows():
                pos_  = r["Range Pos %"]
                bar_c = "#ff5252" if pos_>80 else ("#00e676" if pos_<20 else "#ffd740")
                sig_c = SIG_COLOR.get(r["Signal"],"#aaa")
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;'
                    f'padding:7px 0;border-bottom:.5px solid #1e2230">'
                    f'<span style="width:80px;font-weight:700;color:{sig_c}">{r["Ticker"]}</span>'
                    f'<span style="width:65px;font-size:11px;color:#888">${r["52W Low"]:.2f} lo</span>'
                    f'<div style="flex:1;height:10px;background:#2d3139;border-radius:5px;position:relative">'
                    f'<div style="position:absolute;left:{pos_:.0f}%;top:-2px;width:14px;height:14px;'
                    f'background:{bar_c};border-radius:50%;transform:translateX(-50%)"></div></div>'
                    f'<span style="width:65px;text-align:right;font-size:11px;color:#888">${r["52W High"]:.2f} hi</span>'
                    f'<span style="width:55px;text-align:right;font-weight:600;color:{bar_c}">{pos_:.0f}%</span>'
                    f'</div>', unsafe_allow_html=True)
            st.caption("🔴 >80% of range = near highs (extended) · 🟢 <20% = near lows (potential value)")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── RISK/REWARD CALCULATOR ────────────────────────────────────
    elif tool == "⚖️ Risk / Reward Calculator":
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.markdown("### ⚖️ Risk / Reward Calculator")

        rc1,rc2 = st.columns(2)
        entry_p  = rc1.number_input("Entry price", value=100.0, step=0.5)
        stop_p   = rc1.number_input("Stop-loss",   value=92.0,  step=0.5)
        target1  = rc2.number_input("Target 1",    value=115.0, step=0.5)
        target2  = rc2.number_input("Target 2",    value=130.0, step=0.5)
        shares_  = rc1.number_input("Shares",      value=10.0,  step=1.0)
        prob_win = rc2.slider("Win probability estimate (%)", 30, 80, 55)

        if entry_p > stop_p > 0:
            risk  = (entry_p - stop_p) * shares_
            rw1   = (target1 - entry_p) / (entry_p - stop_p)
            rw2   = (target2 - entry_p) / (entry_p - stop_p)
            exp_v = (prob_win/100 * (target1-entry_p)*shares_) - ((1-prob_win/100) * risk)

            m1,m2,m3,m4 = st.columns(4)
            m1.metric("Max risk $",   f"${risk:,.0f}")
            m2.metric("R/R to T1",    f"{rw1:.2f}x")
            m3.metric("R/R to T2",    f"{rw2:.2f}x")
            m4.metric("Expected value", f"${exp_v:,.0f}",
                      delta="Positive edge" if exp_v>0 else "Negative edge")
            if exp_v > 0:
                st.success(f"✅ Positive expected value. Trade has edge at {prob_win}% win rate.")
            else:
                st.error("❌ Negative expected value. Improve target, reduce stop, or skip trade.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── CONCENTRATION CHECK ───────────────────────────────────────
    elif tool == "🧾 Portfolio Concentration Check":
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)
        st.markdown("### 🧾 Portfolio Concentration Check")

        with st.spinner("Loading…"):
            df_c = build_summary(PORTFOLIO)

        if not df_c.empty:
            tv_c = df_c["Mkt Value"].sum()
            df_c["Weight %"] = (df_c["Mkt Value"]/tv_c*100).round(2)
            df_c = df_c.sort_values("Weight %",ascending=False)

            top5_w  = df_c.head(5)["Weight %"].sum()
            top10_w = df_c.head(10)["Weight %"].sum()

            ca,cb_,cc = st.columns(3)
            ca.metric("Top 5 concentration",  f"{top5_w:.1f}%",
                      delta="OK" if top5_w<40 else "High")
            cb_.metric("Top 10 concentration",f"{top10_w:.1f}%",
                       delta="OK" if top10_w<60 else "High")
            cc.metric("Positions", str(len(df_c)),
                      delta="Too many" if len(df_c)>30 else "OK")

            st.markdown("---")
            for _,r in df_c.iterrows():
                w    = r["Weight %"]
                bar_ = min(w*6, 100)
                col  = "#ff5252" if w>8 else ("#ffd740" if w>4 else "#69f0ae")
                sig_ = r.get("Signal","HOLD")
                sig_c= SIG_COLOR.get(sig_,"#aaa")
                flag = " ⚠️ Overweight" if w>8 else (" 👀 Watch" if w>4 else "")
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;padding:5px 0;'
                    f'border-bottom:.5px solid #1e2230">'
                    f'<span style="width:85px;font-weight:700;color:{sig_c}">{r["Ticker"]}{flag}</span>'
                    f'<div style="flex:1;height:8px;background:#2d3139;border-radius:4px">'
                    f'<div style="width:{bar_:.0f}%;height:100%;background:{col};border-radius:4px"></div>'
                    f'</div>'
                    f'<span style="width:50px;text-align:right;font-weight:600;color:{col}">{w:.1f}%</span>'
                    f'</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
