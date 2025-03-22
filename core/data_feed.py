import yfinance as yf
from binance.client import Client
import requests
import pandas as pd
from config.settings import BROKER_CREDENTIALS, NEWSAPI_KEY, X_API_KEY

def fetch_data(ticker, broker_type="alpaca", period="1d", interval="1m"):
    if broker_type == "alpaca":
        stock = yf.Ticker(ticker)
        return stock.history(period=period, interval=interval)
    elif broker_type == "binance":
        client = Client(BROKER_CREDENTIALS["Binance"]["api_key"], BROKER_CREDENTIALS["Binance"]["api_secret"])
        klines = client.get_historical_klines(ticker, interval, f"{period} ago UTC")
        df = pd.DataFrame(klines, columns=["timestamp", "Open", "High", "Low", "Close", "Volume", "Close_time", "Quote_asset_volume", "Number_of_trades", "Taker_buy_base", "Taker_buy_quote", "Ignore"])
        df["Close"] = df["Close"].astype(float)
        return df

def fetch_level2_data(ticker):
    return {"bids": [(150.50, 100), (150.40, 200), (150.30, 150)], "asks": [(150.60, 120), (150.70, 180), (150.80, 90)]}

def fetch_news(ticker):
    url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={NEWSAPI_KEY}"
    response = requests.get(url)
    return response.json().get("articles", [])[:5] if response.status_code == 200 else []

def fetch_sentiment(ticker):
    # Simulated X sentiment analysis; requires real X API integration
    url = f"https://api.x.com/2/tweets/search/recent?query={ticker}&max_results=100"  # Replace with actual endpoint
    headers = {"Authorization": f"Bearer {X_API_KEY}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tweets = response.json().get("data", [])
        sentiment = sum(1 if "bullish" in t.lower() else -1 if "bearish" in t.lower() else 0 for t in (tweet["text"] for tweet in tweets)) / len(tweets) if tweets else 0
        return sentiment
    return 0