from alpaca_trade_api.rest import REST
from binance.client import Client
import ib_insync as ib  # Interactive Brokers
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

    def buy(self, ticker, shares, price, order_type="limit", trailing_stop=False, oco=False):
        if self.broker_type == "alpaca":
            kwargs = {"symbol": ticker, "qty": shares, "side": "buy", "time_in_force": "gtc"}
            if order_type == "limit": kwargs.update(type="limit", limit_price=price)
            elif order_type == "market": kwargs["type"] = "market"
            if trailing_stop: kwargs.update(type="trailing_stop", trail_percent="5")
            if oco: kwargs.update(order_class="oco", stop_loss={"stop_price": price * 0.95}, take_profit={"limit_price": price * 1.05})
            self.api.submit_order(**kwargs)
        elif self.broker_type == "binance":
            self.api.order_limit_buy(symbol=ticker, quantity=shares, price=str(price))
        elif self.broker_type == "ib":
            contract = ib.Stock(ticker, "SMART", "USD")
            order = ib.LimitOrder("BUY", shares, price) if order_type == "limit" else ib.MarketOrder("BUY", shares)
            self.api.placeOrder(contract, order)
        self.positions[ticker] = self.positions.get(ticker, 0) + shares
        return True

    def sell(self, ticker, shares, price):
        if ticker in self.positions and self.positions[ticker] >= shares:
            if self.broker_type == "alpaca":
                self.api.submit_order(symbol=ticker, qty=shares, side="sell", type="limit", limit_price=price, time_in_force="gtc")
            elif self.broker_type == "binance":
                self.api.order_limit_sell(symbol=ticker, quantity=shares, price=str(price))
            elif self.broker_type == "ib":
                contract = ib.Stock(ticker, "SMART", "USD")
                order = ib.LimitOrder("SELL", shares, price)
                self.api.placeOrder(contract, order)
            self.positions[ticker] -= shares
            return True
        return False

    def short(self, ticker, shares, price, order_type="limit", trailing_stop=False, oco=False):
        if self.broker_type == "alpaca":
            kwargs = {"symbol": ticker, "qty": shares, "side": "sell", "time_in_force": "gtc"}
            if order_type == "limit": kwargs.update(type="limit", limit_price=price)
            elif order_type == "market": kwargs["type"] = "market"
            if trailing_stop: kwargs.update(type="trailing_stop", trail_percent="5")
            if oco: kwargs.update(order_class="oco", stop_loss={"stop_price": price * 1.05}, take_profit={"limit_price": price * 0.95})
            self.api.submit_order(**kwargs)
        elif self.broker_type == "ib":
            contract = ib.Stock(ticker, "SMART", "USD")
            order = ib.LimitOrder("SELL", shares, price) if order_type == "limit" else ib.MarketOrder("SELL", shares)
            self.api.placeOrder(contract, order)
        self.positions[ticker] = self.positions.get(ticker, 0) - shares
        return True

    def cover(self, ticker, shares, price):
        if ticker in self.positions and self.positions[ticker] < 0:
            if self.broker_type == "alpaca":
                self.api.submit_order(symbol=ticker, qty=shares, side="buy", type="limit", limit_price=price, time_in_force="gtc")
            elif self.broker_type == "ib":
                contract = ib.Stock(ticker, "SMART", "USD")
                order = ib.LimitOrder("BUY", shares, price)
                self.api.placeOrder(contract, order)
            self.positions[ticker] += shares
            return True
        return False

    def buy_option(self, ticker, shares, price, strike, expiry, option_type="call"):
        if self.broker_type == "alpaca":
            contract = self.api.get_option_contract(ticker, strike, expiry, option_type)
            self.api.submit_order(symbol=contract.symbol, qty=shares, side="buy", type="limit", limit_price=price, time_in_force="gtc")
            self.positions[f"{ticker}_OPT"] = shares
            return True
        elif self.broker_type == "ib":
            contract = ib.Option(ticker, expiry, strike, option_type.upper(), "SMART")
            order = ib.LimitOrder("BUY", shares, price)
            self.api.placeOrder(contract, order)
            return True
        return False

    def sell_option(self, ticker, shares, price, strike, expiry):
        if f"{ticker}_OPT" in self.positions:
            if self.broker_type == "alpaca":
                contract = self.api.get_option_contract(ticker, strike, expiry, "call")
                self.api.submit_order(symbol=contract.symbol, qty=shares, side="sell", type="limit", limit_price=price, time_in_force="gtc")
            elif self.broker_type == "ib":
                contract = ib.Option(ticker, expiry, strike, "CALL", "SMART")
                order = ib.LimitOrder("SELL", shares, price)
                self.api.placeOrder(contract, order)
            del self.positions[f"{ticker}_OPT"]
            return True
        return False

    def get_option_value(self, ticker, strike, expiry):
        if self.broker_type == "alpaca":
            contract = self.api.get_option_contract(ticker, strike, expiry, "call")
            quote = self.api.get_latest_quote(contract.symbol)
            return (quote.bidprice + quote.askprice) / 2 * 100
        elif self.broker_type == "ib":
            contract = ib.Option(ticker, expiry, strike, "CALL", "SMART")
            self.api.reqMktData(contract)
            return self.api.ticker(contract).marketPrice() * 100
        return 0

    def get_account_info(self):
        if self.broker_type == "alpaca":
            account = self.api.get_account()
            return {"cash": float(account.cash), "margin": float(account.margin_used) if hasattr(account, "margin_used") else 0}
        elif self.broker_type == "binance":
            account = self.api.get_account()
            return {"cash": float(account["balances"][0]["free"]), "margin": 0}
        elif self.broker_type == "ib":
            return {"cash": self.api.accountSummary()[0].value, "margin": self.api.accountSummary()[1].value}