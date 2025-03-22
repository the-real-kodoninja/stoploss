from alpaca_trade_api.rest import REST
from binance.client import Client
import ib_insync as ib
from config.settings import BROKER_CREDENTIALS

class Broker:
    def __init__(self, name, credentials, broker_type="alpaca"):
        self.name = name
        self.broker_type = broker_type
        self.positions = {}
        if broker_type == "alpaca":
            self.api = REST(credentials["api_key"], credentials["api_secret"], base_url="https://paper-api.alpaca.markets")
        elif broker_type == "binance":
            self.api = Client(credentials["api_key"], credentials["api_secret"])
        elif broker_type == "ib":
            self.api = ib.IB()
            self.api.connect("127.0.0.1", credentials["port"], clientId=credentials["client_id"])
        elif broker_type == "offshore":  # e.g., TradeZero, CMEG
            self.api = REST(credentials["api_key"], credentials["api_secret"], base_url=credentials["base_url"])

    def buy(self, ticker, shares, price, order_type="limit", trailing_stop=False):
        if self.broker_type == "offshore":
            self.api.submit_order(symbol=ticker, qty=shares, side="buy", type=order_type, limit_price=price, time_in_force="day")
        # Other broker implementations...
        self.positions[ticker] = self.positions.get(ticker, 0) + shares
        return True

    def sell(self, ticker, shares, price):
        if ticker in self.positions and self.positions[ticker] >= shares:
            if self.broker_type == "offshore":
                self.api.submit_order(symbol=ticker, qty=shares, side="sell", type="limit", limit_price=price, time_in_force="day")
            # Other broker implementations...
            self.positions[ticker] -= shares
            return True
        return False

    def get_account_info(self):
        if self.broker_type == "offshore":
            account = self.api.get_account()
            return {"cash": float(account.cash), "margin": 0}  # No margin calls
        # Other broker implementations...