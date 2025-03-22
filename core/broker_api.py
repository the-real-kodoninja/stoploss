from alpaca_trade_api.rest import REST  # Real Alpaca API integration
from config.settings import BROKER_CREDENTIALS

class Broker:
    def __init__(self, name, credentials):
        self.name = name
        self.api = REST(credentials["api_key"], credentials["api_secret"], base_url="https://paper-api.alpaca.markets")  # Paper trading
        self.positions = {}

    def buy(self, ticker, shares, price):
        try:
            self.api.submit_order(symbol=ticker, qty=shares, side="buy", type="limit", limit_price=price, time_in_force="gtc")
            self.positions[ticker] = self.positions.get(ticker, 0) + shares
            return True
        except Exception as e:
            print(f"Buy failed: {e}")
            return False

    def sell(self, ticker, shares, price):
        if ticker in self.positions and self.positions[ticker] >= shares:
            try:
                self.api.submit_order(symbol=ticker, qty=shares, side="sell", type="limit", limit_price=price, time_in_force="gtc")
                self.positions[ticker] -= shares
                return True
            except Exception as e:
                print(f"Sell failed: {e}")
                return False
        return False

    def short(self, ticker, shares, price):
        try:
            self.api.submit_order(symbol=ticker, qty=shares, side="sell", type="limit", limit_price=price, time_in_force="gtc")
            self.positions[ticker] = self.positions.get(ticker, 0) - shares
            return True
        except Exception as e:
            print(f"Short failed: {e}")
            return False

    def cover(self, ticker, shares, price):
        if ticker in self.positions and self.positions[ticker] < 0:
            try:
                self.api.submit_order(symbol=ticker, qty=shares, side="buy", type="limit", limit_price=price, time_in_force="gtc")
                self.positions[ticker] += shares
                return True
            except Exception as e:
                print(f"Cover failed: {e}")
                return False
        return False

    def get_account_info(self):
        account = self.api.get_account()
        return {
            "cash": float(account.cash),
            "margin": float(account.margin_used) if hasattr(account, "margin_used") else 0,
            "positions": {pos.symbol: float(pos.qty) for pos in self.api.list_positions()}
        }