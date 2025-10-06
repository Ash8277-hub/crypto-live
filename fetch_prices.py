# fetch_prices.py
import requests
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore
import os, json

# --- CONFIG: Coins and Currency ---
COINS = ["bitcoin", "ethereum", "cardano"]   # Add any coins you like
VS = "usd"                                   # Currency

# --- INITIALIZE FIREBASE ---
# Ensure serviceAccount.json exists in repo root
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccount.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- FUNCTION TO FETCH PRICES ---
def fetch_prices():
    ids = ",".join(COINS)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies={VS}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("Error fetching prices:", e)
        return

    # Prepare Firestore document
    doc = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prices": data
    }

    # Save to Firestore collection "prices" (auto-generated doc ID)
    db.collection("prices").add(doc)
    print("Saved:", doc)

# --- MAIN ---
if __name__ == "__main__":
    fetch_prices()
