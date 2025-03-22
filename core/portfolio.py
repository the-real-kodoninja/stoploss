import pandas as pd
from core.data_feed import fetch_data

class Portfolio:
    def __init__(self):
        self.positions = {}  # {ticker: {"shares": qty, "avg_price": price}}

    def add_position(self, ticker, shares, price):
        if ticker in self.positions:
            current = self.positions[ticker]
            new_shares = current["shares"] + shares
            new_avg_price = (current["avg_price"] * current["shares"] + price * shares) / new_shares
            self.positions[ticker] = {"shares": new_shares, "avg_price": new_avg_price}
        else:
            self.positions[ticker] = {"shares": shares, "avg_price": price}

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
        volatility = df['Close'].pct_change().std() * 252 ** 0.5  # Annualized volatility
        return value * volatility  # Value at Risk approximation