# fetch_prices.py
import requests
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore
import os, json

# --- CONFIG ---
COINS = ["bitcoin","ethereum","cardano"]   # change coins as you like
VS = "usd"
# --------------

# initialize firebase admin (expects serviceAccount.json in repo root)
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccount.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

def fetch_prices():
    ids = ",".join(COINS)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies={VS}"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    doc = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prices": data
    }
    # Save to Firestore collection "prices" (auto-generated doc id)
    db.collection("prices").add(doc)
    print("Saved:", doc)

if __name__ == "__main__":
    fetch_prices()

