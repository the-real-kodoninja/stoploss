from core.analytics import analyze_all
from core.data_feed import fetch_data, fetch_sentiment
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import threading

class NimbusAI:
    def __init__(self, platform):
        self.platform = platform
        self.model = RandomForestClassifier(n_estimators=1000)  # Advanced model
        self.is_running = False

    def train_model(self, ticker):
        df = fetch_data(ticker, period="1y")
        features = analyze_all(df)  # Every known analysis
        target = (df["Close"].shift(-1) > df["Close"]).astype(int)  # Predict up/down
        train_size = int(0.8 * len(df))
        self.model.fit(features.iloc[:train_size], target.iloc[:train_size])
        return self.model.predict_proba(features.iloc[train_size:])[:, 1]

    def is_managing(self):
        return self.is_running

    def start_autonomous_trading(self):
        if not self.is_running:
            self.is_running = True
            threading.Thread(target=self.trade_autonomously).start()

    def stop_autonomous_trading(self):
        self.is_running = False

    def trade_autonomously(self):
        while self.is_running:
            for ticker in self.platform.watchlist:
                if ticker in self.platform.active_trades:
                    continue
                df = fetch_data(ticker)
                probs = self.train_model(ticker)
                latest_prob = probs[-1] if len(probs) > 0 else 0.5
                current_price = df["Close"].iloc[-1]
                sentiment = fetch_sentiment(ticker)
                analysis = analyze_all(df.iloc[-100:])

                if latest_prob > 0.9 and sentiment > 0.2:  # High confidence buy
                    broker_name = list(self.platform.brokers.keys())[0]
                    shares = self.calculate_position_size(ticker, current_price)
                    self.platform.enter_trade(ticker, shares, current_price, "buy", broker_name, 5, 100)
                elif latest_prob < 0.1 and sentiment < -0.2:  # High confidence short
                    broker_name = list(self.platform.brokers.keys())[0]
                    shares = self.calculate_position_size(ticker, current_price)
                    self.platform.enter_trade(ticker, shares, current_price, "short", broker_name, 5, 100)
            time.sleep(60)  # Check every minute

    def calculate_position_size(self, ticker, price):
        cash = sum(b.get_account_info()["cash"] for b in self.platform.brokers.values())
        risk_per_trade = cash * 0.01  # 1% risk
        df = fetch_data(ticker)
        atr = df["High"].iloc[-14:] - df["Low"].iloc[-14:]
        stop_loss_distance = atr.mean()
        return int(risk_per_trade / (stop_loss_distance * price))