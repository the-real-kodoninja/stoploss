import pandas as pd
import numpy as np
from core.data_feed import fetch_data
from multiprocessing import Pool

def backtest_strategy(ticker, broker_type="alpaca", period="1y", stop_loss_percent=5, take_profit=100, simulations=1000):
    df = fetch_data(ticker, broker_type=broker_type, period=period, interval="1d")
    trades = []
    position = 0
    entry_price = 0

    for i in range(1, len(df)):
        price = df['Close'].iloc[i]
        if position == 0 and df['Close'].iloc[i-1] < df['Close'].iloc[i]:
            position = 1
            entry_price = price
        elif position == 1:
            if price <= entry_price * (1 - stop_loss_percent / 100) or price - entry_price >= take_profit:
                trades.append({"entry": entry_price, "exit": price, "profit": price - entry_price})
                position = 0

    with Pool() as pool:
        sim_profits = pool.map(lambda x: _simulate_run(trades, df['Close'].pct_change().dropna()), range(simulations))
    
    return pd.DataFrame(trades), {"mean_profit": np.mean(sim_profits), "5th_percentile": np.percentile(sim_profits, 5)}

def _simulate_run(trades, returns):
    sim_trades = pd.DataFrame(trades)
    sim_returns = np.random.choice(returns, size=len(trades))
    sim_trades["profit"] *= (1 + sim_returns)
    return sim_trades["profit"].sum()