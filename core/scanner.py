import yfinance as yf
import pandas as pd

def scan_stocks(criteria={"volume": 1000000, "price_min": 5, "price_max": 500, "rsi_threshold": 70}):
    tickers = ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN"]  # Expandable list or fetch from API
    results = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo", interval="1d")
        if not df.empty and len(df) > 14:
            volume = df["Volume"].mean()
            price = df["Close"].iloc[-1]
            rsi = calculate_rsi(df["Close"])
            if (volume >= criteria["volume"] and 
                criteria["price_min"] <= price <= criteria["price_max"] and 
                rsi >= criteria["rsi_threshold"]):
                results.append({"ticker": ticker, "price": price, "volume": volume, "rsi": rsi})
    return pd.DataFrame(results)

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs)).iloc[-1]