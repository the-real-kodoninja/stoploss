BROKER_CREDENTIALS = {
    "Alpaca1": {"api_key": "", "api_secret": ""},
    "Binance1": {"api_key": "", "api_secret": ""},
    "IB": {"port": 7497, "client_id": 1},
    "Offshore1": {"api_key": "", "api_secret": "", "base_url": ""}
}
NEWSAPI_KEY = ""
X_API_KEY = ""
AWS_ACCESS_KEY = ""
AWS_SECRET_KEY = ""

# User-configurable trading style and targets
TRADING_STYLE = "penny"  # Options: penny, swing, day, scalp
TARGET_PROFIT = 0.10  # 10% default for penny stocks
RISK_PER_TRADE = 0.01  # 1% risk default