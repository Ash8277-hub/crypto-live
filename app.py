import streamlit as st
import pandas as pd
import firebase_admin, json, os
from firebase_admin import credentials, firestore
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Live Crypto Prices", layout="wide")

# Initialize Firebase using Streamlit secrets or serviceAccount.json
def init_firebase():
    try:
        # Check if Firebase is already initialized to avoid duplicate initialization
        if not firebase_admin._apps:
            # Load credentials from secrets
            if "FIREBASE_SERVICE_ACCOUNT" in st.secrets["general"]:
                cred_dict = json.loads(st.secrets["general"]["FIREBASE_SERVICE_ACCOUNT"])
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
            else:
                st.error("FIREBASE_SERVICE_ACCOUNT not found in secrets.toml")
                return None
        # Return Firestore client
        return firestore.client()
    except Exception as e:
        st.error(f"Error initializing Firebase: {e}")
        return None

db = init_firebase()
if db is None:
    st.stop()

@st.cache_data(ttl=30)
def load_data(limit=500):
    docs = db.collection("prices").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit).stream()
    rows = []
    for d in docs:
        data = d.to_dict()
        ts = data.get("timestamp")
        prices = data.get("prices", {})
        row = {"timestamp": ts}
        for coin, pmap in prices.items():
            row[coin] = pmap.get("usd")
        rows.append(row)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    return df

# Calculate price changes
def calculate_price_changes(df, coins):
    changes = {}
    for coin in coins:
        latest = df[coin].iloc[-1]
        previous = df[coin].iloc[-2] if len(df) > 1 else latest
        change = ((latest - previous) / previous * 100) if previous != 0 else 0
        changes[coin] = {"price": latest, "change": change}
    return changes

st.title("Live Cryptocurrency Price Dashboard")
df = load_data()

if df.empty:
    st.info("No data yet. Trigger the GitHub Action or run the fetch script locally.")
else:
    st.write("Latest snapshot:")
    st.dataframe(df.tail(10))

    coins = [c for c in df.columns if c != "timestamp"]
    
    # Price change indicators
    st.subheader("Price Changes (Latest)")
    changes = calculate_price_changes(df, coins)
    cols = st.columns(4)
    for i, (coin, data) in enumerate(changes.items()):
        with cols[i % 4]:
            color = "green" if data["change"] >= 0 else "red"
            st.metric(
                label=coin,
                value=f"${data['price']:.2f}",
                delta=f"{data['change']:.2f}%",
                delta_color="normal"
            )

    # Chart selection
    chart_type = st.selectbox("Select Chart Type", ["Line Chart", "Bar Chart", "Column Chart"])
    
    # Plotly charts
    if chart_type == "Line Chart":
        fig = px.line(df, x="timestamp", y=coins, title="Cryptocurrency Prices Over Time")
        fig.update_layout(xaxis_title="Time", yaxis_title="Price (USD)", legend_title="Coins")
    elif chart_type == "Bar Chart":
        fig = px.bar(df.tail(10), x="timestamp", y=coins, title="Recent Cryptocurrency Prices", barmode="group")
        fig.update_layout(xaxis_title="Time", yaxis_title="Price (USD)", legend_title="Coins")
    else:  # Column Chart
        fig = go.Figure()
        for coin in coins:
            fig.add_trace(go.Bar(x=df["timestamp"], y=df[coin], name=coin))
        fig.update_layout(
            title="Cryptocurrency Prices Over Time",
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            legend_title="Coins",
            barmode="stack"
        )
    
    st.plotly_chart(fig, use_container_width=True)
