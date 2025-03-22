# 🌿 Stop Loss Trading Platform: Discipline Meets Serenity 🧘‍♂️ (v3.1)

**Description**

Stop Loss isn't just a trading platform; it's a sanctuary for disciplined traders. Crafted with Python's versatility and a soothing, earth-toned aesthetic, it's designed to enforce strict trading rules, manage multiple brokers, and monitor trades with advanced analytics. Imagine a trading environment that's as calming as a forest clearing, yet as powerful as a seasoned trader's strategy.

**Key Features: Where Serenity Meets Power 🚀 (v3.1 Updates Included!)**

* **Multi-Broker Mastery 🤝:** Seamlessly link and manage trades across multiple platforms (Alpaca, Binance, and extensible).
* **Precision Trade Control 🎯:** Set individual stop-loss percentages and take-profit amounts per trade.
* **Rule-Bound Trading 📜:** Implement 35 customizable trading rules for disciplined execution.
* **Dynamic Watchlists 📈:** Add/remove tickers in real-time for focused monitoring.
* **Real-Time Analytics 📊:** Track cash, P/L, margin, spread, and win/loss ratio instantly.
* **Level 2 Data Insights 🔍:** Simulated bid/ask data (upgradeable to real L2 with IEX).
* **Visual Trade Charts 📈:** Real-time price charts using Matplotlib for clear visualization.
* **Sound Alerts 🔔:** Audible notifications for trade entries and exits.
* **Comprehensive Logging 📝:** Detailed trade history saved to `trades_log.csv`.
* **Earthy UI Design 🎨:** Minimalist, calming interface with beige, olive, and brown tones.
* **Alpaca Integration 🦙:** Paper trading API for live trades (configurable).
* **Binance Support 🪙:** Added Binance API for crypto trading. Fetches crypto data.
    * *Note: Binance spot doesn’t support shorting; futures/margin accounts would need further implementation.*
* **Advanced Charting 📈:** Added 9-period EMA to charts. Charts adapt to broker type (Alpaca for stocks, Binance for crypto).
* **Exportable Analytics Reports 📊:** Exports total trades, profit, wins, losses, and average profit to `reports/analytics_report.csv`.
* **UI Settings Panel ⚙️:** Accessible via a "Settings" button.
    * Allows editing `MAX_TRADES` and `MAX_TRADE_DURATION`.
    * Add new brokers with name, API key, secret, and type (Alpaca or Binance).

**File Structure: A Peek Under the Hood 🛠️**

stop_loss/
├── main.py              # The launchpad 🚀
├── core/
│   ├── trading_logic.py # The trading brain 🧠
│   ├── broker_api.py    # Broker communication 🌐 (Alpaca, Binance)
│   ├── data_feed.py     # Market data insights 📊 (Stocks, Crypto)
│   └── logger.py        # Trade journaling & Analytics 📖
├── ui/
│   ├── app.py           # The command center 🖥️
│   ├── widgets.py       # UI building blocks 🧱
│   ├── styles.py        # Earth-toned canvas 🎨
│   └── charts.py        # Visual analytics 📈 (Stocks, Crypto)
├── config/
│   ├── settings.py      # Broker secrets 🔑
│   └── rules.py         # Trading commandments 📜
├── reports/
│   └── analytics_report.csv # Analytics export
├── assets/
│   └── alert.wav        # Audible alerts 🔔
└── tests/
└── test_trading.py  # Validation tests ✅


**Installation: Embark on Your Trading Journey 🚀**

**Prerequisites:**

* Python 3.8+ 🐍
* Dependencies: `pip install yfinance matplotlib alpaca-trade-api python-binance playsound` 📦
* Alpaca account 🦙 (paper trading recommended).
* Binance account 🪙.
* Alert sound file (`alert.wav`) 🔊.

**How to Run:**

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/the-real-kodoninja/stoploss
    cd stop_loss
    ```

2.  **Install Dependencies:**

    ```bash
    pip install yfinance matplotlib alpaca-trade-api python-binance playsound
    ```

3.  **Set Up Alpaca and Binance Credentials:**

    ```python
    # config/settings.py
    BROKER_CREDENTIALS = {
        "Alpaca1": {"api_key": "YOUR_ALPACA_KEY", "api_secret": "YOUR_ALPACA_SECRET"},
        "Binance1": {"api_key": "YOUR_BINANCE_KEY", "api_secret": "YOUR_BINANCE_SECRET"}
    }
    ```

4.  **Add Alert Sound:**

    * Place `alert.wav` in the `assets/` directory.

5.  **Run the Application:**

    ```bash
    python main.py
    ```

**Connecting to Trading Platforms:**

* **Alpaca & Binance:** Configure credentials in `settings.py`.
* **Extensibility:** Modify `broker_api.py` for other brokers.

**Usage: Navigating Your Trading Sanctuary 🧭**

* **Trade Entry:** Fill the form and click "Buy" or "Short".
* **Watchlists:** Add/remove tickers in real-time.
* **Monitoring:** Track trades, Level 2 data, and charts.
* **Analytics:** View real-time performance metrics.
* **Logging:** Review detailed trade history.
* **Settings:** Use the settings panel to change rules and add brokers.
* **Export Analytics:** Use the export analytics button to create a report.

**Future Enhancements: Expanding the Horizon 🌌**

* More advanced charting indicators.
* Further expansion of supported brokers.
* Real level 2 data implementation.
* And more.

**License: Open Source Trading 📜**

This project is licensed under the MIT License. Modify and distribute freely.

**Important Notes:**

* Test with paper trading before live use.
* Securely manage API keys (e.g., environment variables).