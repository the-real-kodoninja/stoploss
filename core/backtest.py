import pandas as pd
from core.data_feed import fetch_data

def backtest_strategy(ticker, broker_type="alpaca", period="1y", stop_loss_percent=5, take_profit=100):
    df = fetch_data(ticker, broker_type=broker_type, period=period, interval="1d")
    trades = []
    position = 0
    entry_price = 0

    for i in range(1, len(df)):
        price = df['Close'].iloc[i]
        if position == 0 and df['Close'].iloc[i-1] < df['Close'].iloc[i]:  # Simple buy signal
            position = 1
            entry_price = price
        elif position == 1:
            if price <= entry_price * (1 - stop_loss_percent / 100):
                trades.append({"entry": entry_price, "exit": price, "profit": price - entry_price})
                position = 0
            elif price - entry_price >= take_profit:
                trades.append({"entry": entry_price, "exit": price, "profit": price - entry_price})
                position = 0

    return pd.DataFrame(trades)