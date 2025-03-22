import threading
import time
from playsound import playsound
from core.broker_api import Broker
from core.data_feed import fetch_data, fetch_level2_data
from core.logger import TradeLogger
from config.rules import *

class StopLossPlatform:
    def __init__(self):
        self.brokers = {}
        self.watchlist = ["AAPL", "BTCUSDT"]  # Mixed stock/crypto watchlist
        self.active_trades = {}
        self.logger = TradeLogger()
        self.max_trades = MAX_TRADES
        self.max_trade_duration = MAX_TRADE_DURATION

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

    def enter_trade(self, ticker, shares, price, action, broker_name, stop_loss_percent, take_profit):
        if broker_name not in self.brokers:
            print(f"Broker {broker_name} not linked.")
            return
        
        if len(self.active_trades) >= self.max_trades:
            print("Max trades reached.")
            return

        broker = self.brokers[broker_name]
        if action == "buy" and broker.buy(ticker, shares, price):
            self.active_trades[ticker] = {
                "broker": broker_name, "entry_price": price, "shares": shares, "time": time.time(),
                "type": "long", "stop_loss": price * (1 - stop_loss_percent / 100), "take_profit": take_profit
            }
            self.logger.log_trade(ticker, action, shares, price, broker_name)
            threading.Thread(target=self.monitor_trade, args=(ticker,)).start()
            playsound("assets/alert.wav", block=False)
        elif action == "short" and broker.short(ticker, shares, price):
            self.active_trades[ticker] = {
                "broker": broker_name, "entry_price": price, "shares": shares, "time": time.time(),
                "type": "short", "stop_loss": price * (1 + stop_loss_percent / 100), "take_profit": take_profit
            }
            self.logger.log_trade(ticker, action, shares, price, broker_name)
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

        while ticker in self.active_trades:
            df = fetch_data(ticker, broker_type=broker.broker_type)
            current_price = df['Close'].iloc[-1]
            profit = (current_price - entry_price) * shares if trade_type == "long" else (entry_price - current_price) * shares
            
            if trade_type == "long":
                if current_price <= stop_loss:
                    broker.sell(ticker, shares, current_price)
                    self.logger.log_exit(ticker, "sell", shares, current_price, profit, "stop_loss")
                    del self.active_trades[ticker]
                    playsound("assets/alert.wav", block=False)
                elif profit >= take_profit:
                    broker.sell(ticker, shares, current_price)
                    self.logger.log_exit(ticker, "sell", shares, current_price, profit, "take_profit")
                    del self.active_trades[ticker]
                    playsound("assets/alert.wav", block=False)
            else:  # Short
                if current_price >= stop_loss:
                    broker.cover(ticker, shares, current_price)
                    self.logger.log_exit(ticker, "cover", shares, current_price, profit, "stop_loss")
                    del self.active_trades[ticker]
                    playsound("assets/alert.wav", block=False)
                elif profit >= take_profit:
                    broker.cover(ticker, shares, current_price)
                    self.logger.log_exit(ticker, "cover", shares, current_price, profit, "take_profit")
                    del self.active_trades[ticker]
                    playsound("assets/alert.wav", block=False)

            if time.time() - trade["time"] > self.max_trade_duration:
                action = "sell" if trade_type == "long" else "cover"
                func = broker.sell if trade_type == "long" else broker.cover
                func(ticker, shares, current_price)
                self.logger.log_exit(ticker, action, shares, current_price, profit, "time_limit")
                del self.active_trades[ticker]
                playsound("assets/alert.wav", block=False)

            time.sleep(1)