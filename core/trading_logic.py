import threading
import time
from playsound import playsound
from core.broker_api import Broker
from core.data_feed import fetch_data, fetch_level2_data
from core.logger import TradeLogger
from core.portfolio import Portfolio
from core.nimbus_ai import NimbusAI
from config.rules import *

class StopLossPlatform:
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
        if broker_name not in self.brokers or (len(self.active_trades) >= self.max_trades and not self.nimbus_ai.is_managing()):
            return
        broker = self.brokers[broker_name]
        trade_data = {
            "broker": broker_name, "entry_price": price, "shares": shares, "time": time.time(),
            "type": "long" if action == "buy" else "short", "stop_loss": price * (1 - stop_loss_percent / 100 if action == "buy" else 1 + stop_loss_percent / 100),
            "take_profit": take_profit, "order_type": order_type, "trailing_stop": trailing_stop, "oco": oco, "option": option, "strike": strike, "expiry": expiry
        }
        success = self._execute_trade(broker, ticker, shares, price, action, order_type, trailing_stop, oco, option, strike, expiry)
        if success:
            self.active_trades[ticker] = trade_data
            self.logger.log_trade(ticker, action, shares, price, broker_name, option=option, strike=strike, expiry=expiry)
            self.portfolio.add_position(ticker, shares, price, option)
            threading.Thread(target=self.monitor_trade, args=(ticker,), daemon=True).start()
            playsound("assets/alert.wav", block=False)

    def _execute_trade(self, broker, ticker, shares, price, action, order_type, trailing_stop, oco, option, strike, expiry):
        if option:
            return broker.buy_option(ticker, shares, price, strike, expiry, "call" if action == "buy" else "put")
        return broker.buy(ticker, shares, price, order_type, trailing_stop, oco) if action == "buy" else broker.short(ticker, shares, price, order_type, trailing_stop, oco)

    def monitor_trade(self, ticker):
        trade = self.active_trades[ticker]
        broker = self.brokers[trade["broker"]]
        while ticker in self.active_trades:
            df = fetch_data(ticker, broker_type=broker.broker_type)
            current_price = df['Close'].iloc[-1]
            self._check_trade_conditions(ticker, trade, broker, current_price)
            time.sleep(0.1)  # Optimized refresh rate

    def _check_trade_conditions(self, ticker, trade, broker, current_price):
        profit = self._calculate_profit(ticker, trade, broker, current_price)
        stop_loss = self._update_trailing_stop(trade, current_price)
        if trade["type"] == "long":
            if current_price <= stop_loss or profit >= trade["take_profit"]:
                self._exit_trade(ticker, trade, broker, current_price, "sell", "stop_loss" if current_price <= stop_loss else "take_profit")
        else:
            if current_price >= stop_loss or profit >= trade["take_profit"]:
                self._exit_trade(ticker, trade, broker, current_price, "cover", "stop_loss" if current_price >= stop_loss else "take_profit")
        if time.time() - trade["time"] > self.max_trade_duration:
            self._exit_trade(ticker, trade, broker, current_price, "sell" if trade["type"] == "long" else "cover", "time_limit")

    def _calculate_profit(self, ticker, trade, broker, current_price):
        return (current_price - trade["entry_price"]) * trade["shares"] if not trade["option"] else broker.get_option_value(ticker, trade["strike"], trade["expiry"])

    def _update_trailing_stop(self, trade, current_price):
        if trade["trailing_stop"]:
            if trade["type"] == "long":
                trade["highest_price"] = max(trade.get("highest_price", trade["entry_price"]), current_price)
                return trade["highest_price"] * (1 - trade["stop_loss"] / trade["entry_price"])
            else:
                trade["lowest_price"] = min(trade.get("lowest_price", trade["entry_price"]), current_price)
                return trade["lowest_price"] * (1 + trade["stop_loss"] / trade["entry_price"])
        return trade["stop_loss"]

    def _exit_trade(self, ticker, trade, broker, price, action, reason):
        func = (broker.sell_option if trade["option"] else broker.sell) if action == "sell" else (broker.cover_option if trade["option"] else broker.cover)
        func(ticker, trade["shares"], price, strike=trade["strike"], expiry=trade["expiry"]) if trade["option"] else func(ticker, trade["shares"], price)
        profit = self._calculate_profit(ticker, trade, broker, price)
        self.logger.log_exit(ticker, action, trade["shares"], price, profit, reason)
        self.portfolio.remove_position(ticker, trade["shares"] if trade["type"] == "long" else -trade["shares"])
        del self.active_trades[ticker]
        playsound("assets/alert.wav", block=False)

    def activate_nimbus_ai(self):
        self.nimbus_ai.start_autonomous_trading()