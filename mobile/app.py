from flask import Flask, render_template
import pandas as pd
from core.data_feed import fetch_data

app = Flask(__name__)

@app.route('/')
def dashboard():
    trades = pd.read_csv("trades_log.csv").tail(10).to_dict(orient="records")
    watchlist = ["AAPL", "BTCUSDT"]  # Placeholder; sync with platform
    analytics = {"cash": 10000, "profit": 500}  # Placeholder; fetch from brokers
    return render_template("index.html", trades=trades, watchlist=watchlist, analytics=analytics)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)