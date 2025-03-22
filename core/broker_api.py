from alpaca_trade_api.rest import REST
from binance.client import Client
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

    def buy(self, ticker, shares, price, order_type="limit", trailing_stop=False, oco=False):
        try:
            if self.broker_type == "alpaca":
                kwargs = {"symbol": ticker, "qty": shares, "side": "buy", "time_in_force": "gtc"}
                if order_type == "limit":
                    kwargs["type"] = "limit"
                    kwargs["limit_price"] = price
                elif order_type == "market":
                    kwargs["type"] = "market"
                if trailing_stop:
                    kwargs["type"] = "trailing_stop"
                    kwargs["trail_percent"] = "5"
                if oco:
                    kwargs["order_class"] = "oco"
                    kwargs["stop_loss"] = {"stop_price": price * 0.95}
                    kwargs["take_profit"] = {"limit_price": price * 1.05}
                self.api.submit_order(**kwargs)
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

    def short(self, ticker, shares, price, order_type="limit", trailing_stop=False, oco=False):
        try:
            if self.broker_type == "alpaca":
                kwargs = {"symbol": ticker, "qty": shares, "side": "sell", "time_in_force": "gtc"}
                if order_type == "limit":
                    kwargs["type"] = "limit"
                    kwargs["limit_price"] = price
                elif order_type == "market":
                    kwargs["type"] = "market"
                if trailing_stop:
                    kwargs["type"] = "trailing_stop"
                    kwargs["trail_percent"] = "5"
                if oco:
                    kwargs["order_class"] = "oco"
                    kwargs["stop_loss"] = {"stop_price": price * 1.05}
                    kwargs["take_profit"] = {"limit_price": price * 0.95}
                self.api.submit_order(**kwargs)
            elif self.broker_type == "binance":
                print("Shorting not supported on Binance spot.")
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

    def buy_option(self, ticker, shares, price, strike, expiry, option_type="call"):
        try:
            if self.broker_type == "alpaca":
                contract = self.api.get_option_contract(ticker, strike, expiry, option_type)
                self.api.submit_order(symbol=contract.symbol, qty=shares, side="buy", type="limit", limit_price=price, time_in_force="gtc")
                self.positions[f"{ticker}_OPT"] = shares
                return True
            print("Options not supported on Binance.")
            return False
        except Exception as e:
            print(f"Option buy failed: {e}")
            return False

    def sell_option(self, ticker, shares, price, strike, expiry):
        if f"{ticker}_OPT" in self.positions:
            try:
                if self.broker_type == "alpaca":
                    contract = self.api.get_option_contract(ticker, strike, expiry, "call")
                    self.api.submit_order(symbol=contract.symbol, qty=shares, side="sell", type="limit", limit_price=price, time_in_force="gtc")
                    del self.positions[f"{ticker}_OPT"]
                    return True
                return False
            except Exception as e:
                print(f"Option sell failed: {e}")
                return False
        return False

    def cover_option(self, ticker, shares, price, strike, expiry):
        return self.buy_option(ticker, shares, price, strike, expiry, "put")  # Simplified for now

    def get_option_value(self, ticker, strike, expiry):
        if self.broker_type == "alpaca":
            contract = self.api.get_option_contract(ticker, strike, expiry, "call")
            quote = self.api.get_latest_quote(contract.symbol)
            return (quote.bidprice + quote.askprice) / 2 * 100  # Per contract value
        return 0

    def get_account_info(self):
        if self.broker_type == "alpaca":
            account = self.api.get_account()
            return {"cash": float(account.cash), "margin": float(account.margin_used) if hasattr(account, "margin_used") else 0,
                    "positions": {pos.symbol: float(pos.qty) for pos in self.api.list_positions()}}
        elif self.broker_type == "binance":
            account = self.api.get_account()
            return {"cash": float(account["balances"][0]["free"]), "margin": 0,
                    "positions": {asset["asset"]: float(asset["free"]) for asset in account["balances"] if float(asset["free"]) > 0}}