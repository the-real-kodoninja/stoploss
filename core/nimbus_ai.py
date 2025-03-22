from core.analytics import analyze_all
from core.data_feed import fetch_data, fetch_sentiment
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import numpy as np
import threading

class NimbusAI:
    def __init__(self, platform):
        self.platform = platform
        self.model = self._build_deep_model()
        self.is_running = False

    def _build_deep_model(self):
        model = Sequential([
            LSTM(128, return_sequences=True, input_shape=(100, 50)),  # 100 timesteps, 50 features
            Dropout(0.2),
            LSTM(64),
            Dropout(0.2),
            Dense(32, activation="relu"),
            Dense(1, activation="sigmoid")
        ])
        model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
        return model

    def train_model(self, ticker):
        df = fetch_data(ticker, period="1y")
        features = analyze_all(df).values
        target = (df["Close"].shift(-1) > df["Close"]).astype(int).values
        train_size = int(0.8 * len(features))
        features = np.array([features[i-100:i] for i in range(100, len(features))])
        target = target[100:]
        self.model.fit(features[:train_size], target[:train_size], epochs=10, batch_size=32, verbose=0)
        return self.model.predict(features[train_size:], verbose=0)

    def is_managing(self):
        return self.is_running

    def start_autonomous_trading(self):
        if not self.is_running:
            self.is_running = True
            threading.Thread(target=self.trade_autonomously, daemon=True).start()

    def stop_autonomous_trading(self):
        self.is_running = False

    def trade_autonomously(self):
        while self.is_running:
            for ticker in self.platform.watchlist:
                if ticker in self.platform.active_trades:
                    continue
                df = fetch_data(ticker)
                probs = self.train_model(ticker)
                latest_prob = probs[-1][0] if len(probs) > 0 else 0.5
                current_price = df["Close"].iloc[-1]
                sentiment = fetch_sentiment(ticker)
                if latest_prob > 0.9 and sentiment > 0.2:
                    broker_name = list(self.platform.brokers.keys())[0]
                    shares = self.calculate_position_size(ticker, current_price)
                    self.platform.enter_trade(ticker, shares, current_price, "buy", broker_name, 5, 100)
                elif latest_prob < 0.1 and sentiment < -0.2:
                    broker_name = list(self.platform.brokers.keys())[0]
                    shares = self.calculate_position_size(ticker, current_price)
                    self.platform.enter_trade(ticker, shares, current_price, "short", broker_name, 5, 100)
            time.sleep(60)

    def calculate_position_size(self, ticker, price):
        cash = sum(b.get_account_info()["cash"] for b in self.platform.brokers.values())
        risk_per_trade = cash * 0.01
        df = fetch_data(ticker)
        atr = (df["High"] - df["Low"]).iloc[-14:].mean()
        return int(risk_per_trade / (atr * price))