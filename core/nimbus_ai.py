import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, Attention, Concatenate
from core.analytics import analyze_all
from core.data_feed import fetch_data, fetch_sentiment, fetch_level2_data, fetch_news
from core.scanner import StockScreener
import numpy as np
import threading
from datetime import datetime
import pytz

class NimbusAI:
    def __init__(self, platform, trading_style="penny", target_profit=0.10):
        self.platform = platform
        self.model = self._build_universal_model()
        self.screener = StockScreener(trading_style)
        self.trading_style = trading_style
        self.target_profit = target_profit  # User-defined (e.g., 10% for penny stocks)
        self.is_running = False
        self.timezone = pytz.timezone("America/New_York")
        self.risk_per_trade = 0.01  # 1% risk default

    def _build_universal_model(self):
        price_input = Input(shape=(100, 60))
        sentiment_input = Input(shape=(1,))
        l2_input = Input(shape=(20,))
        x = LSTM(256, return_sequences=True)(price_input)
        x = Dropout(0.3)(x)
        x = LSTM(128)(x)
        x = Attention()([x, x])
        x = Concatenate()([x, sentiment_input, l2_input])
        x = Dense(64, activation="relu")(x)
        output = Dense(5, activation="softmax")(x)  # Buy, Sell, Hold, Short, Hedge
        model = Model(inputs=[price_input, sentiment_input, l2_input], outputs=output)
        model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
        return model

    def train_model(self, ticker):
        df = fetch_data(ticker, period="1y" if self.trading_style == "swing" else "1d")
        features = analyze_all(df).values[-100:]
        sentiment = np.array([fetch_sentiment(ticker)])
        l2 = np.array([self._flatten_l2(fetch_level2_data(ticker))])
        target = pd.qcut(df["Close"].pct_change().shift(-1).iloc[-100:], 5, labels=[0, 1, 2, 3, 4]).values
        target = tf.keras.utils.to_categorical(target, num_classes=5)
        self.model.fit([features[np.newaxis], sentiment[np.newaxis], l2[np.newaxis]], target[np.newaxis], epochs=10, batch_size=32, verbose=0)
        return self.model.predict([features[-1:], sentiment[-1:], l2[-1:]], verbose=0)[0]

    def _flatten_l2(self, l2_data):
        bids = [b[0] for b in l2_data["bids"][:10]] + [b[1] for b in l2_data["bids"][:10]]
        asks = [a[0] for a in l2_data["asks"][:10]] + [a[1] for a in l2_data["asks"][:10]]
        return bids + asks

    def start_autonomous_trading(self):
        if not self.is_running:
            self.is_running = True
            threading.Thread(target=self.trade_autonomously, daemon=True).start()

    def trade_autonomously(self):
        while self.is_running:
            candidates = self.screener.scan(self.platform.watchlist)
            for ticker, metrics in candidates:
                if ticker in self.platform.active_trades:
                    self._manage_trade(ticker, metrics)
                else:
                    self._enter_trade(ticker, metrics)
            time.sleep(0.1 if self.trading_style in ["day", "scalp"] else 60)

    def _enter_trade(self, ticker, metrics):
        df = fetch_data(ticker)
        price = df["Close"].iloc[-1]
        probs = self.train_model(ticker)
        broker_name = self._select_broker()
        shares = self._calculate_position_size(ticker, price)
        stop_loss = 0.02 if self.trading_style == "penny" else 0.05  # Tighter for penny stocks
        
        if probs[2] > 0.95:  # Buy
            self.platform.enter_trade(ticker, shares, price, "buy", broker_name, stop_loss * 100, self.target_profit * 100, trailing_stop=True)
        elif probs[3] > 0.95 and self.trading_style != "penny":  # Short (not for penny stocks)
            self.platform.enter_trade(ticker, shares, price, "short", broker_name, stop_loss * 100, self.target_profit * 100, trailing_stop=True)

    def _manage_trade(self, ticker, metrics):
        trade = self.platform.active_trades[ticker]
        df = fetch_data(ticker)
        price = df["Close"].iloc[-1]
        profit = (price - trade["entry_price"]) * trade["shares"] if trade["type"] == "long" else (trade["entry_price"] - price) * trade["shares"]
        if profit >= self.target_profit * trade["entry_price"] * trade["shares"] or price <= trade["stop_loss"]:
            broker = self.platform.brokers[trade["broker"]]
            broker.sell(ticker, trade["shares"], price) if trade["type"] == "long" else broker.cover(ticker, trade["shares"], price)
            del self.platform.active_trades[ticker]

    def _calculate_position_size(self, ticker, price):
        cash = sum(b.get_account_info()["cash"] for b in self.platform.brokers.values())
        atr = (fetch_data(ticker)["High"] - fetch_data(ticker)["Low"]).iloc[-14:].mean()
        return int((cash * self.risk_per_trade) / (atr * price))

    def _select_broker(self):
        offshore = [b for b in self.platform.brokers if b.startswith("Offshore")]
        return offshore[0] if offshore and self.trading_style == "penny" else list(self.platform.brokers.keys())[0]