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

 
