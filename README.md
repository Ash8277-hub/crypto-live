# Crypto Live Price Tracker

A simple cryptocurrency price tracker that fetches live prices from [CoinGecko](https://www.coingecko.com/) every 5 minutes using GitHub Actions, stores them in Firebase Firestore, and displays them on a Streamlit dashboard.

## Features
- Fetches prices for Bitcoin, Ethereum, and Cardano (configurable) via CoinGecko API.
- Stores price data in Firebase Firestore (free Spark plan).
- Displays a live dashboard with price history and charts using Streamlit Community Cloud.
- Runs on a fully free stack: Firebase Spark, GitHub Actions, Streamlit Community Cloud.

## Setup Instructions
1. **Create a Firebase Project**:
   - Go to [Firebase Console](https://console.firebase.google.com/), create a project (Spark plan).
   - Enable Firestore in Native mode.
   - Download a service account JSON from Google Cloud Console (IAM & Admin → Service Accounts → Keys → JSON).

2. **Set Up GitHub Repo**:
   - Create a repo with the files in this project.
   - Add the Firebase service account JSON as a base64-encoded GitHub Secret named `FIREBASE_SERVICE_ACCOUNT` (see instructions in the guide).

3. **Deploy Streamlit App**:
   - Push the repo to GitHub.
   - In [Streamlit Community Cloud](https://streamlit.io/cloud), create a new app, select this repo, and set `app.py` as the entry point.
   - Add the Firebase service account JSON as a Streamlit secret named `FIREBASE_SERVICE_ACCOUNT`.

4. **Run & Verify**:
   - GitHub Actions runs every 5 minutes (check Actions tab).
   - Verify data in Firestore (`prices` collection).
   - Visit the Streamlit app URL to see the dashboard.

## Files
- `fetch_prices.py`: Fetches prices and writes to Firestore.
- `app.py`: Streamlit dashboard to display price history and charts.
- `.github/workflows/fetch.yml`: GitHub Actions workflow (runs every 5 minutes).
- `requirements.txt`: Python dependencies.
- `.gitignore`: Excludes sensitive files (e.g., `serviceAccount.json`).

## Troubleshooting
- **No data in Streamlit**: Ensure the GitHub Action has run and Firestore rules allow reads.
- **Permission errors**: Verify the service account JSON matches the Firebase project.
- **Rate limits**: CoinGecko’s free tier allows 5–30 calls/min; the 5-minute schedule is safe.

## License
MIT License