import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Portfolio Dashboard", layout="wide")

st.title("📊 Portfolio Dashboard")

# =========================
# 📥 INPUT (YOUR PORTFOLIO)
# =========================
PORTFOLIO = {
    "AAPL.TO": {"shares": 29.99, "ac": 32.86},
    "ABCL": {"shares": 159.9965, "ac": 4.2607},
    "AEHR": {"shares": 15, "ac": 20.56},
    "AMZN.TO": {"shares": 79.99, "ac": 17.19},
    "APLD": {"shares": 25, "ac": 24.72},
    # 👉 KEEP ADDING FULL LIST HERE (same format)
}

# =========================
# 📡 FETCH LIVE PRICES
# =========================
tickers = list(PORTFOLIO.keys())

@st.cache_data(ttl=300)
def get_prices(tickers):
    data = yf.download(tickers, period="1d", interval="1m", progress=False)
    return data["Close"].iloc[-1]

prices = get_prices(tickers)

# =========================
# 🧮 BUILD DATAFRAME
# =========================
rows = []
for ticker, data in PORTFOLIO.items():
    price = prices.get(ticker, None)
    if price is None:
        continue

    shares = data["shares"]
    ac = data["ac"]

    rows.append({
        "Ticker": ticker,
        "Price": price,
        "Shares": shares,
        "Avg Cost": ac
    })

df = pd.DataFrame(rows)

# =========================
# CORE METRICS
# =========================
df["Market Value"] = df["Price"] * df["Shares"]
df["Cost Basis"] = df["Avg Cost"] * df["Shares"]
df["PnL"] = df["Market Value"] - df["Cost Basis"]
df["Return %"] = (df["Price"] - df["Avg Cost"]) / df["Avg Cost"] * 100

total_value = df["Market Value"].sum()
total_cost = df["Cost Basis"].sum()

df["Weight %"] = df["Market Value"] / total_value * 100

# =========================
# 📊 PORTFOLIO OVERVIEW (UPGRADED)
# =========================
st.subheader("📊 Portfolio Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Portfolio Value", f"${total_value:,.0f}")
col2.metric("Total PnL", f"${df['PnL'].sum():,.0f}")
col3.metric("Return %", f"{((total_value-total_cost)/total_cost)*100:.2f}%")
col4.metric("Positions", len(df))

# Advanced risk stats
top5 = df.sort_values("Weight %", ascending=False).head(5)["Weight %"].sum()
median_weight = df["Weight %"].median()

st.info(f"Top 5 Concentration: {top5:.1f}% | Median Position: {median_weight:.2f}%")

# =========================
# ⚠️ RISK SYSTEM (REAL)
# =========================
st.subheader("⚠️ Risk System")

def risk_flag(row):
    flags = []

    if row["Weight %"] > 10:
        flags.append("Overweight")

    if row["Return %"] < -25:
        flags.append("Deep Drawdown")

    if row["Market Value"] < total_value * 0.01:
        flags.append("Too Small")

    return ", ".join(flags)

df["Risk"] = df.apply(risk_flag, axis=1)

risk_df = df[df["Risk"] != ""]

st.dataframe(risk_df[["Ticker", "Weight %", "Return %", "Risk"]])

# =========================
# 📈 SIGNAL ENGINE (UPGRADED)
# =========================
def signal(row):
    if row["Return %"] > 30 and row["Weight %"] > 5:
        return "Trim Winner"

    if row["Return %"] < -20:
        return "Cut / Review"

    if row["Weight %"] < 2 and row["Return %"] > -10:
        return "Add"

    return "Hold"

df["Signal"] = df.apply(signal, axis=1)

# =========================
# 📋 SIGNAL SUMMARY TABLE (CLEAN)
# =========================
st.subheader("📋 Signal Summary")

signal_summary = (
    df.groupby("Signal")
    .agg(
        Count=("Ticker", "count"),
        Capital=("Market Value", "sum")
    )
    .reset_index()
)

signal_summary["Capital %"] = signal_summary["Capital"] / total_value * 100

st.dataframe(signal_summary.sort_values("Capital %", ascending=False))

# =========================
# 🚀 TOP TRADES TO EXECUTE (RANKED)
# =========================
st.subheader("🚀 Top Trades to Execute")

# Ranking logic
adds = df[df["Signal"] == "Add"].sort_values("Weight %")
trims = df[df["Signal"] == "Trim Winner"].sort_values("Return %", ascending=False)
cuts = df[df["Signal"] == "Cut / Review"].sort_values("Return %")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### ➕ Add (Underweight)")
    st.dataframe(adds.head(10)[["Ticker", "Weight %", "Return %"]])

with col2:
    st.markdown("### ➖ Trim (Winners)")
    st.dataframe(trims.head(10)[["Ticker", "Return %", "Weight %"]])

with col3:
    st.markdown("### ❌ Cut / Review")
    st.dataframe(cuts.head(10)[["Ticker", "Return %"]])

# =========================
# 📉 POSITION SIZING ENGINE
# =========================
st.subheader("📉 Position Sizing")

target_weight = 5

df["Target Value"] = total_value * (target_weight / 100)
df["Trade Needed ($)"] = df["Target Value"] - df["Market Value"]

st.dataframe(df[[
    "Ticker",
    "Market Value",
    "Weight %",
    "Target Value",
    "Trade Needed ($)"
]].sort_values("Trade Needed ($)"))

# =========================
# 📊 FULL TABLE
# =========================
st.subheader("📊 Full Portfolio Table")

st.dataframe(df.sort_values("Market Value", ascending=False))
