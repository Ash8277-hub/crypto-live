# app.py
import streamlit as st
import pandas as pd
import firebase_admin, json, os
from firebase_admin import credentials, firestore
from datetime import datetime

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
            # coin -> {'usd': 123.45}
            row[coin] = pmap.get("usd")
        rows.append(row)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    return df

st.title("Live Cryptocurrency Price Dashboard")
df = load_data()

if df.empty:
    st.info("No data yet. Trigger the GitHub Action or run the fetch script locally.")
else:
    st.write("Latest snapshot:")
    st.dataframe(df.tail(10))

    coins = [c for c in df.columns if c != "timestamp"]
    st.line_chart(df.set_index("timestamp")[coins])
