import threading
import time
from playsound import playsound
from core.broker_api import Broker
from core.data_feed import fetch_data, fetch_level2_data, fetch_news, fetch_sentiment
from core.logger import TradeLogger
from core.portfolio import Portfolio
from core.nimbus_ai import NimbusAI
from config.rules import *

class NimbusTraderPlatform:
    def __init__(self):
        self.brokers = {}
        self.watchlist = ["AAPL", "BTCUSDT"]
        self.active_trades = {}
        self.logger = TradeLogger()
        self.portfolio = Portfolio()
        self.max_trades = MAX_TRADES
        self.max_trade_duration = MAX_TRADE_DURATION
        self.nimbus_ai = NimbusAI(self)

    def add_broker(self, broker_name, credentials, broker_type="alpaca"):
        self.brokers[broker_name] = Broker(broker_name, credentials, broker_type)

    def add_to_watchlist(self, ticker):
        if ticker not in self.watchlist:
            self.watchlist.append(ticker)

    def remove_from_watchlist(self, ticker):
        if ticker in self.watchlist:
            self.watchlist.remove(ticker)

    def update_rule(self, rule_name, value):
        globals()[rule_name] = value

    def enter_trade(self, ticker, shares, price, action, broker_name, stop_loss_percent, take_profit, order_type="limit", trailing_stop=False, oco=False, option=False, strike=None, expiry=None):
        if broker_name not in self.brokers:
            print(f"Broker {broker_name} not linked.")
            return
        
        if len(self.active_trades) >= self.max_trades and not self.nimbus_ai.is_managing():
            print("Max trades reached.")
            return

        broker = self.brokers[broker_name]
        trade_data = {
            "broker": broker_name, "entry_price": price, "shares": shares, "time": time.time(),
            "type": "long" if action == "buy" else "short", "stop_loss": price * (1 - stop_loss_percent / 100 if action == "buy" else 1 + stop_loss_percent / 100),
            "take_profit": take_profit, "order_type": order_type, "trailing_stop": trailing_stop, "oco": oco, "option": option, "strike": strike, "expiry": expiry
        }

        if option:
            success = broker.buy_option(ticker, shares, price, strike, expiry, "call" if action == "buy" else "put")
        else:
            success = broker.buy(ticker, shares, price, order_type, trailing_stop, oco) if action == "buy" else broker.short(ticker, shares, price, order_type, trailing_stop, oco)

        if success:
            self.active_trades[ticker] = trade_data
            self.logger.log_trade(ticker, action, shares, price, broker_name, option=option, strike=strike, expiry=expiry)
            self.portfolio.add_position(ticker, shares, price, option)
            threading.Thread(target=self.monitor_trade, args=(ticker,)).start()
            playsound("assets/alert.wav", block=False)

    def monitor_trade(self, ticker):
        trade = self.active_trades[ticker]
        broker = self.brokers[trade["broker"]]
        entry_price = trade["entry_price"]
        shares = trade["shares"]
        trade_type = trade["type"]
        stop_loss = trade["stop_loss"]
        take_profit = trade["take_profit"]
        trailing_stop = trade["trailing_stop"]
        option = trade["option"]

        highest_price = entry_price if trade_type == "long" else float('inf')
        lowest_price = entry_price if trade_type == "short" else 0

        while ticker in self.active_trades:
            df = fetch_data(ticker, broker_type=broker.broker_type)
            current_price = df['Close'].iloc[-1]
            profit = (current_price - entry_price) * shares if not option else broker.get_option_value(ticker, trade["strike"], trade["expiry"])

            if trailing_stop:
                if trade_type == "long":
                    highest_price = max(highest_price, current_price)
                    stop_loss = highest_price * (1 - trade["stop_loss"] / entry_price)
                else:
                    lowest_price = min(lowest_price, current_price)
                    stop_loss = lowest_price * (1 + trade["stop_loss"] / entry_price)

            if trade_type == "long":
                if current_price <= stop_loss or profit >= take_profit:
                    func = broker.sell_option if option else broker.sell
                    func(ticker, shares, current_price, strike=trade["strike"], expiry=trade["expiry"]) if option else func(ticker, shares, current_price)
                    reason = "stop_loss" if current_price <= stop_loss else "take_profit"
                    self.logger.log_exit(ticker, "sell", shares, current_price, profit, reason)
                    self.portfolio.remove_position(ticker, shares)
                    del self.active_trades[ticker]
                    playsound("assets/alert.wav", block=False)
            else:  # Short
                if current_price >= stop_loss or profit >= take_profit:
                    func = broker.cover_option if option else broker.cover
                    func(ticker, shares, current_price, strike=trade["strike"], expiry=trade["expiry"]) if option else func(ticker, shares, current_price)
                    reason = "stop_loss" if current_price >= stop_loss else "take_profit"
                    self.logger.log_exit(ticker, "cover", shares, current_price, profit, reason)
                    self.portfolio.remove_position(ticker, -shares)
                    del self.active_trades[ticker]
                    playsound("assets/alert.wav", block=False)

            if time.time() - trade["time"] > self.max_trade_duration:
                action = "sell" if trade_type == "long" else "cover"
                func = (broker.sell_option if option else broker.sell) if trade_type == "long" else (broker.cover_option if option else broker.cover)
                func(ticker, shares, current_price, strike=trade["strike"], expiry=trade["expiry"]) if option else func(ticker, shares, current_price)
                self.logger.log_exit(ticker, action, shares, current_price, profit, "time_limit")
                self.portfolio.remove_position(ticker, shares if trade_type == "long" else -shares)
                del self.active_trades[ticker]
                playsound("assets/alert.wav", block=False)

            time.sleep(1)

    def activate_nimbus_ai(self):
        self.nimbus_ai.start_autonomous_trading()