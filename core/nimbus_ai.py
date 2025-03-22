import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, Attention, Concatenate
from tensorflow.keras.optimizers import Adam
import numpy as np
import pandas as pd
from core.analytics import analyze_all
from core.data_feed import fetch_data, fetch_sentiment, fetch_level2_data
import threading
from datetime import datetime, time
import pytz

class NimbusAI:
    def __init__(self, platform):
        self.platform = platform
        self.model = self._build_mega_model()
        self.is_running = False
        self.memory = []  # For reinforcement learning
        self.epsilon = 0.1  # Exploration rate
        self.market_hours = {
            "US": (time(9, 30), time(16, 0)),  # NYSE hours
            "Crypto": (time(0, 0), time(23, 59))  # 24/7
        }
        self.timezone = pytz.timezone("America/New_York")

    def _build_mega_model(self):
        # Multi-input model: Price data, sentiment, L2 data
        price_input = Input(shape=(100, 50))  # 100 timesteps, 50 features
        sentiment_input = Input(shape=(1,))
        l2_input = Input(shape=(10,))  # 5 bids + 5 asks

        # LSTM for price data
        x = LSTM(256, return_sequences=True)(price_input)
        x = Dropout(0.3)(x)
        x = LSTM(128)(x)
        x = Dropout(0.3)(x)

        # Attention mechanism
        attn = Attention()([x, x])
        x = Concatenate()([x, attn])

        # Combine with sentiment and L2 data
        x = Concatenate()([x, sentiment_input, l2_input])
        x = Dense(64, activation="relu")(x)
        x = Dropout(0.2)(x)
        output = Dense(3, activation="softmax")(x)  # Buy, Sell, Hold

        model = Model(inputs=[price_input, sentiment_input, l2_input], outputs=output)
        model.compile(optimizer=Adam(learning_rate=0.0001), loss="categorical_crossentropy", metrics=["accuracy"])
        return model

    def _is_market_open(self, ticker):
        now = datetime.now(self.timezone)
        market = "Crypto" if "USDT" in ticker else "US"
        start, end = self.market_hours[market]
        return start <= now.time() <= end or market == "Crypto"

    def train_model(self, ticker):
        df = fetch_data(ticker, period="2y")
        features = analyze_all(df).values[-200:]  # Last 200 days for swing trading
        sentiment = np.array([fetch_sentiment(ticker)] * len(features))
        l2 = np.array([self._flatten_l2(fetch_level2_data(ticker)) for _ in range(len(features))])
        target = pd.qcut(df["Close"].pct_change().shift(-1).iloc[-200:], 3, labels=[0, 1, 2]).values  # Sell, Hold, Buy
        
        features = np.array([features[i-100:i] for i in range(100, len(features))])
        target = tf.keras.utils.to_categorical(target[100:], num_classes=3)
        
        self.model.fit([features, sentiment[100:], l2[100:]], target, epochs=20, batch_size=16, verbose=0)
        return self.model.predict([features[-1:], sentiment[-1:], l2[-1:]], verbose=0)[0]

    def _flatten_l2(self, l2_data):
        bids = [b[0] for b in l2_data["bids"][:5]] + [b[1] for b in l2_data["bids"][:5]]
        asks = [a[0] for a in l2_data["asks"][:5]] + [a[1] for a in l2_data["asks"][:5]]
        return bids[:5] + asks[:5]

    def start_autonomous_trading(self):
        if not self.is_running:
            self.is_running = True
            threading.Thread(target=self.trade_autonomously, daemon=True).start()

    def stop_autonomous_trading(self):
        self.is_running = False

    def trade_autonomously(self):
        while self.is_running:
            for ticker in self.platform.watchlist:
                if not self._is_market_open(ticker):
                    continue
                if ticker in self.platform.active_trades:
                    self._manage_existing_trade(ticker)
                else:
                    self._evaluate_new_trade(ticker)
            time.sleep(5)  # High-frequency checking

    def _manage_existing_trade(self, ticker):
        trade = self.platform.active_trades[ticker]
        df = fetch_data(ticker)
        current_price = df["Close"].iloc[-1]
        probs = self._predict(ticker)
        profit = (current_price - trade["entry_price"]) * trade["shares"] if trade["type"] == "long" else (trade["entry_price"] - current_price) * trade["shares"]
        
        if trade["type"] == "long" and (probs[0] > 0.9 or profit > trade["take_profit"] * 1.5):  # Sell or overprofit
            broker = self.platform.brokers[trade["broker"]]
            broker.sell(ticker, trade["shares"], current_price)
            del self.platform.active_trades[ticker]
        elif trade["type"] == "short" and (probs[2] > 0.9 or profit > trade["take_profit"] * 1.5):  # Cover or overprofit
            broker = self.platform.brokers[trade["broker"]]
            broker.cover(ticker, trade["shares"], current_price)
            del self.platform.active_trades[ticker]

    def _evaluate_new_trade(self, ticker):
        df = fetch_data(ticker)
        current_price = df["Close"].iloc[-1]
        probs = self._predict(ticker)
        sentiment = fetch_sentiment(ticker)
        broker_name = list(self.platform.brokers.keys())[0]
        shares = self._calculate_position_size(ticker, current_price)

        if probs[2] > 0.95 and sentiment > 0.3:  # Buy with high confidence
            self.platform.enter_trade(ticker, shares, current_price, "buy", broker_name, 5, 100, trailing_stop=True)
        elif probs[0] > 0.95 and sentiment < -0.3:  # Sell/Short with high confidence
            self.platform.enter_trade(ticker, shares, current_price, "short", broker_name, 5, 100, trailing_stop=True)

    def _predict(self, ticker):
        df = fetch_data(ticker)
        features = analyze_all(df).values[-100:]
        sentiment = np.array([fetch_sentiment(ticker)])
        l2 = np.array([self._flatten_l2(fetch_level2_data(ticker))])
        return self.model.predict([features[np.newaxis], sentiment[np.newaxis], l2[np.newaxis]], verbose=0)[0]

    def _calculate_position_size(self, ticker, price):
        cash = sum(b.get_account_info()["cash"] for b in self.platform.brokers.values())
        risk_per_trade = cash * 0.01
        df = fetch_data(ticker)
        atr = (df["High"] - df["Low"]).iloc[-14:].mean()
        return int(risk_per_trade / (atr * price))