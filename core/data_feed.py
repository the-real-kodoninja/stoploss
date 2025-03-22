import yfinance as yf
from binance.client import Client
import ib_insync as ib
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
    elif broker_type == "ib":
        ib_api = ib.IB()
        ib_api.connect("127.0.0.1", BROKER_CREDENTIALS["IB"]["port"], clientId=BROKER_CREDENTIALS["IB"]["client_id"])
        contract = ib.Stock(ticker, "SMART", "USD")
        bars = ib_api.reqHistoricalData(contract, endDateTime="", durationStr=period, barSizeSetting=interval, whatToShow="TRADES", useRTH=True)
        return pd.DataFrame(bars, columns=["timestamp", "Open", "High", "Low", "Close", "Volume"])

def fetch_level2_data(ticker, broker_type="alpaca"):
    if broker_type == "alpaca":
        api = REST(BROKER_CREDENTIALS["Alpaca1"]["api_key"], BROKER_CREDENTIALS["Alpaca1"]["api_secret"], base_url="https://paper-api.alpaca.markets")
        quote = api.get_latest_quote(ticker)
        return {"bids": [(quote.bidprice, quote.bidsize)], "asks": [(quote.askprice, quote.asksize)]}
    elif broker_type == "ib":
        ib_api = ib.IB()
        ib_api.connect("127.0.0.1", BROKER_CREDENTIALS["IB"]["port"], clientId=BROKER_CREDENTIALS["IB"]["client_id"])
        contract = ib.Stock(ticker, "SMART", "USD")
        ib_api.reqMktDepth(contract)
        depth = ib_api.ticker(contract).domBids, ib_api.ticker(contract).domAsks
        return {"bids": [(b.price, b.size) for b in depth[0][:5]], "asks": [(a.price, a.size) for a in depth[1][:5]]}
    return {"bids": [(150.50, 100)], "asks": [(150.60, 120)]}

def fetch_news(ticker):
    url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={NEWSAPI_KEY}"
    response = requests.get(url)
    return response.json().get("articles", [])[:5] if response.status_code == 200 else []

def fetch_sentiment(ticker):
    url = f"https://api.x.com/2/tweets/search/recent?query={ticker}&max_results=100"
    headers = {"Authorization": f"Bearer {X_API_KEY}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tweets = response.json().get("data", [])
        return sum(1 if "bullish" in t.lower() else -1 if "bearish" in t.lower() else 0 for t in (tweet["text"] for tweet in tweets)) / len(tweets) if tweets else 0
    return 0