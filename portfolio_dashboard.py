import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

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

# =========================
# MARKET DATA
# =========================
@st.cache_data(ttl=300)
def get_price_data(ticker):
    try:
        data = yf.Ticker(ticker).history(period="6mo")
        return data
    except:
        return None


def get_last_price(df):
    if df is None or df.empty:
        return None
    return float(df["Close"].iloc[-1])


# =========================
# INDICATORS
# =========================
def rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def compute_indicators(df):
    df = df.copy()
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()
    df["RSI"] = rsi(df["Close"])
    return df


# =========================
# SIGNAL ENGINE (RULE-BASED)
# =========================
def signal_logic(last_price, ma20, ma50, rsi_val):
    if any(pd.isna([ma20, ma50, rsi_val])):
        return "No Signal"

    if ma20 > ma50 and rsi_val < 70:
        return "Positive Trend"
    elif ma20 < ma50 and rsi_val > 60:
        return "Weak Trend"
    else:
        return "Neutral"


# =========================
# BUILD PORTFOLIO TABLE
# =========================
def build_df():
    rows = []

    for t, v in PORTFOLIO.items():
        df = get_price_data(t)
        price = get_last_price(df)

        shares = v["shares"]
        ac = v["ac"]
        cost = shares * ac

        if price:
            market = shares * price
            pnl = market - cost
            return_pct = pnl / cost * 100
        else:
            market, pnl, return_pct = None, None, None

        if df is not None and not df.empty:
            df = compute_indicators(df)
            last = df.iloc[-1]

            ma20 = last["MA20"]
            ma50 = last["MA50"]
            rsi_val = last["RSI"]

            signal = signal_logic(price, ma20, ma50, rsi_val)
            volatility = df["Close"].pct_change().std() * 100
        else:
            ma20 = ma50 = rsi_val = signal = volatility = None

        rows.append({
            "Ticker": t,
            "Shares": shares,
            "AC": ac,
            "Cost": cost,
            "Price": price,
            "Market Value": market,
            "PnL": pnl,
            "Return %": return_pct,
            "RSI": rsi_val,
            "MA20": ma20,
            "MA50": ma50,
            "Signal": signal,
            "Volatility %": volatility
        })

    return pd.DataFrame(rows)


df = build_df()

# =========================
# RISK SYSTEM
# =========================
def risk_score(row):
    if pd.isna(row["Volatility %"]):
        return "Unknown"

    size_risk = row["Cost"]
    vol = row["Volatility %"]

    if size_risk > 10000 and vol > 3:
        return "High"
    elif vol > 2:
        return "Medium"
    return "Low"


df["Risk"] = df.apply(risk_score, axis=1)


# =========================
# TOP TRADES
# =========================
def top_trades(df):
    return df.sort_values("Return %", ascending=False)[
        ["Ticker", "Return %", "Signal", "Risk"]
    ].head(8)


# =========================
# UI
# =========================
st.set_page_config(layout="wide")

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Portfolio Overview",
        "🔍 Ticker Deep Dive",
        "📰 News Feed",
        "📉 Signals Summary",
        "🛠️ Trading Tools"
    ]
)

# =========================
# OVERVIEW
# =========================
if page == "📊 Portfolio Overview":
    st.title("Portfolio Overview (Live)")

    col1, col2, col3 = st.columns(3)
    col1.metric("Holdings", len(df))
    col2.metric("Total Cost", f"${df['Cost'].sum():,.0f}")
    col3.metric("Total Market Value", f"${df['Market Value'].sum():,.0f}")

    st.subheader("Top Trades to Execute")
    st.dataframe(top_trades(df), use_container_width=True)

    st.subheader("Full Portfolio")
    st.dataframe(df, use_container_width=True)


# =========================
# TICKER VIEW
# =========================
elif page == "🔍 Ticker Deep Dive":
    st.title("Ticker Deep Dive")

    ticker = st.selectbox("Select Ticker", list(PORTFOLIO.keys()))
    row = df[df["Ticker"] == ticker].iloc[0]

    st.write(row)


# =========================
# NEWS (placeholder)
# =========================
elif page == "📰 News Feed":
    st.title("News Feed")
    st.info("Ready for API integration (Yahoo / Finnhub / NewsAPI)")
    st.write("Hook news per ticker here")


# =========================
# SIGNALS
# =========================
elif page == "📉 Signals Summary":
    st.title("Signals Summary")

    signal_df = df[["Ticker", "Signal", "Risk", "RSI", "Return %"]]
    st.dataframe(signal_df, use_container_width=True)


# =========================
# TOOLS
# =========================
elif page == "🛠️ Trading Tools":
    st.title("Trading Tools")

    st.write("### Performance Distribution")
    st.bar_chart(df.set_index("Ticker")["Return %"])

    st.write("### Risk Exposure")
    st.bar_chart(df["Risk"].value_counts())


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
 
 
