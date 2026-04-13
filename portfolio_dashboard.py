import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Portfolio Dashboard", layout="wide")

st.title("📊 Portfolio Dashboard")

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

# =========================
# PRICE LOADING
# =========================
@st.cache_data(ttl=300)
def get_prices(tickers):
    data = yf.download(tickers, period="1d", interval="1m", progress=False)
    return data["Close"].iloc[-1]

tickers = list(PORTFOLIO.keys())
prices = get_prices(tickers)

# =========================
# BUILD DATAFRAME
# =========================
rows = []

for t, v in PORTFOLIO.items():
    price = prices.get(t, None)
    if price is None:
        continue

    rows.append({
        "Ticker": t,
        "Price": price,
        "Shares": v["shares"],
        "Avg Cost": v["ac"]
    })

df = pd.DataFrame(rows)

# =========================
# CALCULATIONS
# =========================
df["Market Value"] = df["Price"] * df["Shares"]
df["Cost Basis"] = df["Avg Cost"] * df["Shares"]
df["PnL"] = df["Market Value"] - df["Cost Basis"]
df["Return %"] = (df["Price"] - df["Avg Cost"]) / df["Avg Cost"] * 100

total_value = df["Market Value"].sum()
total_cost = df["Cost Basis"].sum()

df["Weight %"] = df["Market Value"] / total_value * 100

# =========================
# PORTFOLIO OVERVIEW
# =========================
st.subheader("📊 Portfolio Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Portfolio Value", f"${total_value:,.0f}")
c2.metric("Total PnL", f"${df['PnL'].sum():,.0f}")
c3.metric("Return %", f"{((total_value-total_cost)/total_cost)*100:.2f}%")
c4.metric("Positions", len(df))

top5 = df.sort_values("Weight %", ascending=False).head(5)["Weight %"].sum()

st.info(f"Top 5 Concentration: {top5:.1f}% | Largest Position: {df['Weight %'].max():.1f}%")

# =========================
# RISK SYSTEM
# =========================
st.subheader("⚠️ Risk System")

def risk(row):
    flags = []
    if row["Weight %"] > 10:
        flags.append("Overweight")
    if row["Return %"] < -25:
        flags.append("Drawdown")
    if row["Weight %"] < 1:
        flags.append("Too Small")
    return ", ".join(flags)

df["Risk"] = df.apply(risk, axis=1)

risk_df = df[df["Risk"] != ""]

st.dataframe(risk_df[["Ticker", "Weight %", "Return %", "Risk"]])

# =========================
# SIGNAL SYSTEM
# =========================
def signal(row):
    if row["Return %"] > 30 and row["Weight %"] > 5:
        return "Trim"
    elif row["Return %"] < -20:
        return "Review"
    elif row["Weight %"] < 2:
        return "Add"
    else:
        return "Hold"

df["Signal"] = df.apply(signal, axis=1)

# =========================
# SIGNAL SUMMARY
# =========================
st.subheader("📋 Signal Summary")

summary = df.groupby("Signal").agg(
    Count=("Ticker", "count"),
    Capital=("Market Value", "sum")
).reset_index()

summary["Capital %"] = summary["Capital"] / total_value * 100

st.dataframe(summary)

# =========================
# TOP TRADES
# =========================
st.subheader("🚀 Top Trades to Execute")

add = df[df["Signal"] == "Add"].sort_values("Weight %")
trim = df[df["Signal"] == "Trim"].sort_values("Return %", ascending=False)
review = df[df["Signal"] == "Review"].sort_values("Return %")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("➕ Add")
    st.dataframe(add[["Ticker", "Weight %", "Return %"]].head(10))

with c2:
    st.markdown("➖ Trim")
    st.dataframe(trim[["Ticker", "Return %", "Weight %"]].head(10))

with c3:
    st.markdown("⚠️ Review")
    st.dataframe(review[["Ticker", "Return %"]].head(10))

# =========================
# POSITION SIZING
# =========================
st.subheader("📉 Position Sizing Guide")

target = 0.05 * total_value

df["Target Value"] = target
df["Rebalance ($)"] = df["Target Value"] - df["Market Value"]

st.dataframe(df[["Ticker", "Market Value", "Weight %", "Target Value", "Rebalance ($)"]])
