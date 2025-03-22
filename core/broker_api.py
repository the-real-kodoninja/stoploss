from alpaca_trade_api.rest import REST
from binance.client import Client  # Binance API
from config.settings import BROKER_CREDENTIALS

class Broker:
    def __init__(self, name, credentials, broker_type="alpaca"):
        self.name = name
        self.broker_type = broker_type
        if broker_type == "alpaca":
            self.api = REST(credentials["api_key"], credentials["api_secret"], base_url="https://paper-api.alpaca.markets")
        elif broker_type == "binance":
            self.api = Client(credentials["api_key"], credentials["api_secret"])
        self.positions = {}

    def buy(self, ticker, shares, price):
        try:
            if self.broker_type == "alpaca":
                self.api.submit_order(symbol=ticker, qty=shares, side="buy", type="limit", limit_price=price, time_in_force="gtc")
            elif self.broker_type == "binance":
                self.api.order_limit_buy(symbol=ticker, quantity=shares, price=str(price))
            self.positions[ticker] = self.positions.get(ticker, 0) + shares
            return True
        except Exception as e:
            print(f"Buy failed: {e}")
            return False

    def sell(self, ticker, shares, price):
        if ticker in self.positions and self.positions[ticker] >= shares:
            try:
                if self.broker_type == "alpaca":
                    self.api.submit_order(symbol=ticker, qty=shares, side="sell", type="limit", limit_price=price, time_in_force="gtc")
                elif self.broker_type == "binance":
                    self.api.order_limit_sell(symbol=ticker, quantity=shares, price=str(price))
                self.positions[ticker] -= shares
                return True
            except Exception as e:
                print(f"Sell failed: {e}")
                return False
        return False

    def short(self, ticker, shares, price):
        try:
            if self.broker_type == "alpaca":
                self.api.submit_order(symbol=ticker, qty=shares, side="sell", type="limit", limit_price=price, time_in_force="gtc")
            elif self.broker_type == "binance":  # Binance doesn’t support shorting directly; use futures/margin
                print("Shorting not supported on Binance spot. Use futures/margin accounts.")
                return False
            self.positions[ticker] = self.positions.get(ticker, 0) - shares
            return True
        except Exception as e:
            print(f"Short failed: {e}")
            return False

    def cover(self, ticker, shares, price):
        if ticker in self.positions and self.positions[ticker] < 0:
            try:
                if self.broker_type == "alpaca":
                    self.api.submit_order(symbol=ticker, qty=shares, side="buy", type="limit", limit_price=price, time_in_force="gtc")
                elif self.broker_type == "binance":
                    print("Covering not supported on Binance spot.")
                    return False
                self.positions[ticker] += shares
                return True
            except Exception as e:
                print(f"Cover failed: {e}")
                return False
        return False

    def get_account_info(self):
        if self.broker_type == "alpaca":
            account = self.api.get_account()
            return {
                "cash": float(account.cash),
                "margin": float(account.margin_used) if hasattr(account, "margin_used") else 0,
                "positions": {pos.symbol: float(pos.qty) for pos in self.api.list_positions()}
            }
        elif self.broker_type == "binance":
            account = self.api.get_account()
            return {
                "cash": float(account["balances"][0]["free"]),  # Assumes USDT as base
                "margin": 0,  # Binance spot doesn’t use margin; update for futures
                "positions": {asset["asset"]: float(asset["free"]) for asset in account["balances"] if float(asset["free"]) > 0}
            }