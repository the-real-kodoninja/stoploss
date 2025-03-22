import pandas as pd
import numpy as np
from core.data_feed import fetch_data, fetch_level2_data
from core.analytics import analyze_all

class StockScreener:
    def __init__(self, trading_style="penny"):
        self.trading_style = trading_style
        self.filters = {
            "penny": {"price_range": (0.01, 5.00), "volume_min": 500000, "volatility_min": 0.05, "exclude_gray_pink": True},
            "swing": {"price_range": (5.00, 5000), "volume_min": 100000, "volatility_min": 0.02},
            "day": {"price_range": (0.01, 5000), "volume_min": 200000, "volatility_min": 0.03},
            "scalp": {"price_range": (0.01, 5000), "volume_min": 1000000, "volatility_min": 0.10}
        }

    def scan(self, tickers):
        results = []
        style_filters = self.filters.get(self.trading_style, self.filters["penny"])
        for ticker in tickers:
            df = fetch_data(ticker, period="1d", interval="1m")
            if not df.empty and self._passes_basic_filters(ticker, df, style_filters):
                metrics = self._analyze_stock(ticker, df)
                if self._passes_advanced_filters(metrics, style_filters):
                    results.append((ticker, metrics))
        return sorted(results, key=lambda x: x[1]["sss_score"] if self.trading_style == "penny" else x[1]["momentum"], reverse=True)

    def _passes_basic_filters(self, ticker, df, filters):
        price = df["Close"].iloc[-1]
        is_penny = filters["price_range"][0] <= price <= filters["price_range"][1]
        if filters.get("exclude_gray_pink", False):
            return is_penny and not ticker.endswith(".PK") and not ticker.endswith(".GR")
        return is_penny

    def _analyze_stock(self, ticker, df):
        features = analyze_all(df)
        l2 = fetch_level2_data(ticker)
        volatility = (df["High"].max() - df["Low"].min()) / df["Close"].mean()
        sss_score = self._sykes_sliding_scale(features, l2)  # Penny stock focus
        momentum = self._cameron_momentum(df)  # Day/scalp focus
        return {
            "price": df["Close"].iloc[-1],
            "volume": df["Volume"].iloc[-1],
            "volatility": volatility,
            "sss_score": sss_score,
            "momentum": momentum,
            "rsi": features["RSI"].iloc[-1],
            "vwap": features["VWAP"].iloc[-1],
            "macd": features["MACD"].iloc[-1],
            "bollinger_width": (features["BB_upper"] - features["BB_lower"]).iloc[-1] / features["BB_middle"].iloc[-1]
        }

    def _sykes_sliding_scale(self, features, l2):
        pattern = 10 if features["CDLDOJI"].iloc[-1] or features["CDLHAMMER"].iloc[-1] else 5
        risk_reward = min(20, 10 * (features["Close"].iloc[-1] / features["BB_lower"].iloc[-1] - 1))
        liquidity = min(10, (l2["bids"][0][1] + l2["asks"][0][1]) / 1000)
        return (pattern * 0.4 + risk_reward * 0.3 + liquidity * 0.3)

    def _cameron_momentum(self, df):
        return (df["Close"].iloc[-1] / df["Close"].iloc[-5] - 1) * df["Volume"].iloc[-5:].mean()

    def _passes_advanced_filters(self, metrics, filters):
        return (metrics["volume"] >= filters["volume_min"] and 
                metrics["volatility"] >= filters["volatility_min"])