from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import pandas as pd
from core.data_feed import fetch_data, fetch_level2_data, fetch_news
from core.trading_logic import StopLossPlatform
import threading

app = Flask(__name__, static_folder="static", template_folder="static")
socketio = SocketIO(app)
platform = StopLossPlatform()

def update_clients():
    while True:
        trades = pd.read_csv("trades_log.csv").tail(10).to_dict(orient="records")
        analytics = {
            "cash": sum(b.get_account_info()["cash"] for b in platform.brokers.values()),
            "profit": pd.read_csv("trades_log.csv")["Profit"].sum(),
            "active_trades": len(platform.active_trades)
        }
        watchlist_data = {ticker: fetch_data(ticker)["Close"].iloc[-1] for ticker in platform.watchlist}
        socketio.emit("update", {"trades": trades, "analytics": analytics, "watchlist": watchlist_data})
        socketio.sleep(1)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/trade/<ticker>')
def trade_details(ticker):
    df = fetch_data(ticker).tail(50).to_json(orient="records")
    l2 = fetch_level2_data(ticker)
    news = fetch_news(ticker)
    return jsonify({"df": df, "l2": l2, "news": news, "ticker": ticker})

@socketio.on("connect")
def handle_connect():
    if not hasattr(update_clients, "thread"):
        update_clients.thread = threading.Thread(target=update_clients, daemon=True)
        update_clients.thread.start()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)