import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import EARTH_TONES
from ui.widgets import TradeEntryForm, Level2Display, WatchlistManager, SettingsPanel
from ui.charts import TradeChart
from core.data_feed import calculate_spread, calculate_win_loss_ratio, fetch_news, fetch_sentiment
from core.backtest import backtest_strategy
from core.scanner import scan_stocks
from config.settings import BROKER_CREDENTIALS, HOTKEYS, SCANNER_CRITERIA

class StopLossApp(tk.Tk):
    def __init__(self, platform):
        super().__init__()
        self.platform = platform
        self.title("Ultimate Stop Loss Platform")
        self.geometry("1600x1200")
        self.configure(bg=EARTH_TONES["bg"])

        for name, creds in BROKER_CREDENTIALS.items():
            self.platform.add_broker(name, creds, "binance" if "Binance" in name else "alpaca")

        # Multi-monitor support: Create detachable windows
        self.main_frame = tk.Frame(self, bg=EARTH_TONES["bg"])
        self.main_frame.pack(fill="both", expand=True)

        tk.Label(self.main_frame, text="Ultimate Stop Loss Dashboard", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=("Helvetica", 16, "bold")).pack(pady=10)

        self.trade_form = TradeEntryForm(self.main_frame, self.enter_trade, list(self.platform.brokers.keys()))
        self.trade_form.pack(pady=10)

        tk.Label(self.main_frame, text="Watchlist", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        self.watchlist_manager = WatchlistManager(self.main_frame, self.add_to_watchlist, self.remove_from_watchlist)
        self.watchlist_manager.pack(pady=5)
        self.watchlist_tree = ttk.Treeview(self.main_frame, columns=("Ticker"), show="headings")
        self.watchlist_tree.heading("Ticker", text="Ticker")
        self.watchlist_tree.pack(fill="x", padx=10)
        self.watchlist_tree.bind("<<TreeviewSelect>>", self.on_watchlist_select)

        tk.Label(self.main_frame, text="Active Trades", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        self.trades_tree = ttk.Treeview(self.main_frame, columns=("Ticker", "Shares", "Entry", "Type", "Stop Loss", "Take Profit"), show="headings")
        self.trades_tree.heading("Ticker", text="Ticker")
        self.trades_tree.heading("Shares", text="Shares")
        self.trades_tree.heading("Entry", text="Entry Price")
        self.trades_tree.heading("Type", text="Type")
        self.trades_tree.heading("Stop Loss", text="Stop Loss")
        self.trades_tree.heading("Take Profit", text="Take Profit")
        self.trades_tree.pack(fill="x", padx=10)

        self.analytics_frame = tk.Frame(self.main_frame, bg=EARTH_TONES["bg"])
        self.analytics_frame.pack(pady=10)
        self.cash_label = tk.Label(self.analytics_frame, text="Cash: $0", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"])
        self.cash_label.pack(side="left", padx=5)
        self.profit_label = tk.Label(self.analytics_frame, text="Profit: $0", bg=EARTH_TONES["bg"], fg=EARTH_TONES["profit"], font=EARTH_TONES["font"])
        self.profit_label.pack(side="left", padx=5)
        self.margin_label = tk.Label(self.analytics_frame, text="Margin: $0", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"])
        self.margin_label.pack(side="left", padx=5)
        self.spread_label = tk.Label(self.analytics_frame, text="Spread: $0", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"])
        self.spread_label.pack(side="left", padx=5)
        self.win_loss_label = tk.Label(self.analytics_frame, text="W/L Ratio: 0%", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"])
        self.win_loss_label.pack(side="left", padx=5)
        self.risk_label = tk.Label(self.analytics_frame, text="Risk: $0", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"])
        self.risk_label.pack(side="left", padx=5)
        self.monte_carlo_label = tk.Label(self.analytics_frame, text="Monte Carlo VaR: $0", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"])
        self.monte_carlo_label.pack(side="left", padx=5)

        self.level2_display = Level2Display(self.main_frame)
        self.level2_display.pack(pady=10)
        self.trade_chart = TradeChart(self.main_frame)
        self.trade_chart.pack(pady=10)

        tk.Label(self.main_frame, text="News", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        self.news_text = tk.Text(self.main_frame, height=5, bg=EARTH_TONES["highlight"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"])
        self.news_text.pack(fill="x", padx=10)

        tk.Label(self.main_frame, text="AI Suggestions", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        self.ai_text = tk.Text(self.main_frame, height=5, bg=EARTH_TONES["highlight"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"])
        self.ai_text.pack(fill="x", padx=10)

        tk.Label(self.main_frame, text="Scanner Results", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        self.scanner_tree = ttk.Treeview(self.main_frame, columns=("Ticker", "Price", "Volume", "RSI"), show="headings")
        self.scanner_tree.heading("Ticker", text="Ticker")
        self.scanner_tree.heading("Price", text="Price")
        self.scanner_tree.heading("Volume", text="Volume")
        self.scanner_tree.heading("RSI", text="RSI")
        self.scanner_tree.pack(fill="x", padx=10)

        tk.Label(self.main_frame, text="Trade Journal", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        self.journal_text = tk.Text(self.main_frame, height=5, bg=EARTH_TONES["highlight"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"])
        self.journal_text.pack(fill="x", padx=10)

        tk.Button(self.main_frame, text="Settings", bg=EARTH_TONES["button_bg"], fg=EARTH_TONES["button_fg"], command=self.open_settings).pack(pady=5)
        tk.Button(self.main_frame, text="Export Analytics", bg=EARTH_TONES["button_bg"], fg=EARTH_TONES["button_fg"], command=self.export_analytics).pack(pady=5)
        tk.Button(self.main_frame, text="Run Backtest", bg=EARTH_TONES["button_bg"], fg=EARTH_TONES["button_fg"], command=self.run_backtest).pack(pady=5)
        tk.Button(self.main_frame, text="Run Scanner", bg=EARTH_TONES["button_bg"], fg=EARTH_TONES["button_fg"], command=self.run_scanner).pack(pady=5)
        tk.Button(self.main_frame, text="Detach Window", bg=EARTH_TONES["button_bg"], fg=EARTH_TONES["button_fg"], command=self.detach_window).pack(pady=5)

        self.bind(HOTKEYS["buy"], lambda e: self.hotkey_buy())
        self.bind(HOTKEYS["sell"], lambda e: self.hotkey_sell())

        self.after(1000, self.refresh_ui)

    def enter_trade(self, ticker, shares, price, action, broker, stop_loss_percent, take_profit, order_type, trailing_stop, oco, option, strike, expiry):
        self.platform.enter_trade(ticker, shares, price, action, broker, stop_loss_percent, take_profit, order_type, trailing_stop, oco, option, strike, expiry)

    def hotkey_buy(self):
        self.trade_form.submit_buy()

    def hotkey_sell(self):
        if self.trades_tree.selection():
            ticker = self.trades_tree.item(self.trades_tree.selection(), "values")[0]
            trade = self.platform.active_trades[ticker]
            broker = self.platform.brokers[trade["broker"]]
            broker.sell(ticker, trade["shares"], fetch_data(ticker, broker.broker_type)['Close'].iloc[-1])

    def add_to_watchlist(self, ticker):
        self.platform.add_to_watchlist(ticker)
        self.update_watchlist()

    def remove_from_watchlist(self):
        selected = self.watchlist_tree.selection()
        if selected:
            ticker = self.watchlist_tree.item(selected, "values")[0]
            self.platform.remove_from_watchlist(ticker)
            self.update_watchlist()

    def on_watchlist_select(self, event):
        selected = self.watchlist_tree.selection()
        if selected:
            ticker = self.watchlist_tree.item(selected, "values")[0]
            broker_type = "binance" if "USDT" in ticker else "alpaca"
            self.level2_display.update(ticker)
            self.trade_chart.update_chart(ticker, broker_type)
            self.update_news(ticker)
            self.update_journal(ticker)

    def update_watchlist(self):
        for item in self.watchlist_tree.get_children():
            self.watchlist_tree.delete(item)
        for ticker in self.platform.watchlist:
            self.watchlist_tree.insert("", "end", values=(ticker,))

    def update_trades(self):
        for item in self.trades_tree.get_children():
            self.trades_tree.delete(item)
        for ticker, trade in self.platform.active_trades.items():
            self.trades_tree.insert("", "end", values=(ticker, trade["shares"], trade["entry_price"], trade["type"],
                                                       trade["stop_loss"], trade["take_profit"]))

    def update_analytics(self):
        total_cash = sum(broker.get_account_info()["cash"] for broker in self.platform.brokers.values())
        total_margin = sum(broker.get_account_info()["margin"] for broker in self.platform.brokers.values())
        with open("trades_log.csv", "r") as f:
            lines = list(csv.reader(f))[1:]
            total_profit = sum(float(line[6]) for line in lines if line[6])
        if self.watchlist_tree.selection():
            ticker = self.watchlist_tree.item(self.watchlist_tree.selection(), "values")[0]
            broker_type = "binance" if "USDT" in ticker else "alpaca"
            spread = calculate_spread(fetch_level2_data(ticker))
            risk = self.platform.portfolio.calculate_risk(ticker, broker_type)
            monte_carlo_var = self.platform.portfolio.monte_carlo_risk(ticker, broker_type)
        else:
            spread = risk = monte_carlo_var = 0
        win_loss_ratio = calculate_win_loss_ratio() * 100

        self.cash_label.config(text=f"Cash: ${total_cash:.2f}")
        self.profit_label.config(text=f"Profit: ${total_profit:.2f}", fg=EARTH_TONES["profit"] if total_profit >= 0 else EARTH_TONES["loss"])
        self.margin_label.config(text=f"Margin: ${total_margin:.2f}")
        self.spread_label.config(text=f"Spread: ${spread:.2f}")
        self.win_loss_label.config(text=f"W/L Ratio: {win_loss_ratio:.1f}%")
        self.risk_label.config(text=f"Risk: ${risk:.2f}")
        self.monte_carlo_label.config(text=f"Monte Carlo VaR: ${monte_carlo_var:.2f}")

        ai_suggestions = self.platform.get_ai_suggestions()
        self.ai_text.delete(1.0, tk.END)
        for suggestion in ai_suggestions:
            self.ai_text.insert(tk.END, f"{suggestion['ticker']}: {suggestion['action']} (Confidence: {suggestion['confidence']:.2f})\n")

    def update_news(self, ticker):
        news = fetch_news(ticker)
        sentiment = fetch_sentiment(ticker)
        self.news_text.delete(1.0, tk.END)
        self.news_text.insert(tk.END, f"Sentiment: {sentiment:.2f}\n")
        for article in news:
            self.news_text.insert(tk.END, f"{article['title']} - {article['source']['name']}\n")

    def update_journal(self, ticker):
        df = pd.read_csv("trades_log.csv")
        df = df[df["Ticker"] == ticker]
        self.journal_text.delete(1.0, tk.END)
        for _, row in df.iterrows():
            self.journal_text.insert(tk.END, f"{row['Timestamp']} - {row['Action']} @ {row['Price']} - Profit: {row['Profit']} - {row['Notes']}\n")

    def open_settings(self):
        SettingsPanel(self, self.platform)

    def export_analytics(self):
        self.platform.logger.export_analytics()

    def run_backtest(self):
        if self.watchlist_tree.selection():
            ticker = self.watchlist_tree.item(self.watchlist_tree.selection(), "values")[0]
            broker_type = "binance" if "USDT" in ticker else "alpaca"
            trades, stats = backtest_strategy(ticker, broker_type)
            trades.to_csv(f"reports/backtest_{ticker}.csv")
            messagebox.showinfo("Backtest", f"Mean Profit: ${stats['mean_profit']:.2f}, 5th Percentile: ${stats['5th_percentile']:.2f}")

    def run_scanner(self):
        results = scan_stocks(SCANNER_CRITERIA)
        for item in self.scanner_tree.get_children():
            self.scanner_tree.delete(item)
        for _, row in results.iterrows():
            self.scanner_tree.insert("", "end", values=(row["ticker"], row["price"], row["volume"], row["rsi"]))

    def detach_window(self):
        new_window = tk.Toplevel(self, bg=EARTH_TONES["bg"])
        new_window.geometry("800x600")
        self.main_frame.pack_forget()
        self.main_frame.pack(in_=new_window, fill="both", expand=True)

    def refresh_ui(self):
        self.update_watchlist()
        self.update_trades()
        self.update_analytics()
        self.after(1000, self.refresh_ui)