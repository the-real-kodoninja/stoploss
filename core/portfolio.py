import pandas as pd
import numpy as np
from core.data_feed import fetch_data

class Portfolio:
    def __init__(self):
        self.positions = {}  # {ticker: {"shares": qty, "avg_price": price, "option": bool}}

    def add_position(self, ticker, shares, price, option=False):
        if ticker in self.positions:
            current = self.positions[ticker]
            new_shares = current["shares"] + shares
            new_avg_price = (current["avg_price"] * current["shares"] + price * shares) / new_shares
            self.positions[ticker] = {"shares": new_shares, "avg_price": new_avg_price, "option": option}
        else:
            self.positions[ticker] = {"shares": shares, "avg_price": price, "option": option}

    def remove_position(self, ticker, shares):
        if ticker in self.positions:
            current = self.positions[ticker]
            current["shares"] -= shares
            if current["shares"] <= 0:
                del self.positions[ticker]

    def calculate_risk(self, ticker, broker_type="alpaca"):
        if ticker not in self.positions:
            return 0
        df = fetch_data(ticker, broker_type=broker_type)
        current_price = df['Close'].iloc[-1]
        position = self.positions[ticker]
        value = position["shares"] * current_price
        volatility = df['Close'].pct_change().std() * 252 ** 0.5
        return value * volatility

    def monte_carlo_risk(self, ticker, broker_type="alpaca", simulations=1000):
        df = fetch_data(ticker, broker_type=broker_type, period="1y")
        returns = df['Close'].pct_change().dropna()
        position = self.positions.get(ticker, {"shares": 0, "avg_price": 0})
        value = position["shares"] * df['Close'].iloc[-1]
        sim_returns = np.random.choice(returns, size=(simulations, 252))
        sim_values = value * (1 + sim_returns).cumprod(axis=1)
        return np.percentile(sim_values[:, -1] - value, 5)  # 5% VaR