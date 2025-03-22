import yfinance as yf
from alpaca_trade_api.rest import REST
from config.settings import BROKER_CREDENTIALS

def fetch_data(ticker, period="1d", interval="1m"):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)
    return df

def fetch_level2_data(ticker):
    api = REST(BROKER_CREDENTIALS["Broker1"]["api_key"], BROKER_CREDENTIALS["Broker1"]["api_secret"], base_url="https://paper-api.alpaca.markets")
    # Simulated Level 2 for now; Alpaca doesn’t provide full L2, use IEX or similar for real L2
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
        lines = list(csv.reader(f))[1:]  # Skip header
        wins = sum(1 for line in lines if line[6] and float(line[6]) > 0)
        losses = sum(1 for line in lines if line[6] and float(line[6]) < 0)
        total = wins + losses
        return wins / total if total > 0 else 0