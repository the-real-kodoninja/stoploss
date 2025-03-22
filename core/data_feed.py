import yfinance as yf
from binance.client import Client
from config.settings import BROKER_CREDENTIALS

def fetch_data(ticker, broker_type="alpaca", period="1d", interval="1m"):
    if broker_type == "alpaca":
        stock = yf.Ticker(ticker)
        return stock.history(period=period, interval=interval)
    elif broker_type == "binance":
        client = Client(BROKER_CREDENTIALS["Binance"]["api_key"], BROKER_CREDENTIALS["Binance"]["api_secret"])
        klines = client.get_historical_klines(ticker, Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
        df = pd.DataFrame(klines, columns=["timestamp", "Open", "High", "Low", "Close", "Volume", "Close_time", "Quote_asset_volume", "Number_of_trades", "Taker_buy_base", "Taker_buy_quote", "Ignore"])
        df["Close"] = df["Close"].astype(float)
        return df

def fetch_level2_data(ticker):
    # Simulated; replace with real L2 API (e.g., IEX Cloud) for stocks or Binance depth for crypto
    return {
        "bids": [(150.50, 100), (150.40, 200), (150.30, 150)],
        "asks": [(150.60, 120), (150.70, 180), (150.80, 90)]
    }

def calculate_spread(level2_data):
    best_bid = level2_data["bids"][0][0]
    best_ask = level2_data["asks"][0][0]
    return best_ask - best_bid

def calculate_win_loss_ratio(log_file="trades_log.csv"):
    with open(log_file, "r") as f:
        lines = list(csv.reader(f))[1:]
        wins = sum(1 for line in lines if line[6] and float(line[6]) > 0)
        losses = sum(1 for line in lines if line[6] and float(line[6]) < 0)
        total = wins + losses
        return wins / total if total > 0 else 0