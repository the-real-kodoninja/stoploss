import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from core.data_feed import fetch_data, fetch_sentiment

def suggest_trades(watchlist, brokers):
    suggestions = []
    for ticker in watchlist:
        broker_type = "binance" if "USDT" in ticker else "alpaca"
        df = fetch_data(ticker, broker_type=broker_type, period="1mo")
        if len(df) < 15:
            continue
        features = pd.DataFrame({
            "rsi": calculate_rsi(df["Close"]),
            "ema_diff": df["Close"].ewm(span=9).mean() - df["Close"].ewm(span=21).mean(),
            "volume_change": df["Volume"].pct_change().iloc[-1],
            "sentiment": fetch_sentiment(ticker)
        }, index=[0])
        model = RandomForestClassifier().fit([[0, 0, 0, 0]], [1])  # Placeholder; train with real data
        prediction = model.predict(features)[0]
        if prediction == 1:
            suggestions.append({"ticker": ticker, "action": "buy", "confidence": model.predict_proba(features)[0][1]})
    return suggestions