import tkinter as tk
from tkinter import ttk
from ui.styles import EARTH_TONES
from ui.widgets import TradeEntryForm, Level2Display, WatchlistManager, SettingsPanel
from ui.charts import TradeChart
from core.data_feed import calculate_spread, calculate_win_loss_ratio
from config.settings import BROKER_CREDENTIALS

class StopLossApp(tk.Tk):
    def __init__(self, platform):
        super().__init__()
        self.platform = platform
        self.title("Stop Loss Platform")
        self.geometry("1200x900")
        self.configure(bg=EARTH_TONES["bg"])

        for name, creds in BROKER_CREDENTIALS.items():
            self.platform.add_broker(name, creds, "binance" if "Binance" in name else "alpaca")

        tk.Label(self, text="Stop Loss Dashboard", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=("Helvetica", 16, "bold")).pack(pady=10)

        self.trade_form = TradeEntryForm(self, self.enter_trade, list(self.platform.brokers.keys()))
        self.trade_form.pack(pady=10)

        tk.Label(self, text="Watchlist", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        self.watchlist_manager = WatchlistManager(self, self.add_to_watchlist, self.remove_from_watchlist)
        self.watchlist_manager.pack(pady=5)
        self.watchlist_tree = ttk.Treeview(self, columns=("Ticker"), show="headings")
        self.watchlist_tree.heading("Ticker", text="Ticker")
        self.watchlist_tree.pack(fill="x", padx=10)
        self.watchlist_tree.bind("<<TreeviewSelect>>", self.on_watchlist_select)

        tk.Label(self, text="Active Trades", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        self.trades_tree = ttk.Treeview(self, columns=("Ticker", "Shares", "Entry", "Type", "Stop Loss", "Take Profit"), show="headings")
        self.trades_tree.heading("Ticker", text="Ticker")
        self.trades_tree.heading("Shares", text="Shares")
        self.trades_tree.heading("Entry", text="Entry Price")
        self.trades_tree.heading("Type", text="Type")
        self.trades_tree.heading("Stop Loss", text="Stop Loss")
        self.trades_tree.heading("Take Profit", text="Take Profit")
        self.trades_tree.pack(fill="x", padx=10)

        self.analytics_frame = tk.Frame(self, bg=EARTH_TONES["bg"])
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

        self.level2_display = Level2Display(self)
        self.level2_display.pack(pady=10)
        self.trade_chart = TradeChart(self)
        self.trade_chart.pack(pady=10)

        tk.Button(self, text="Settings", bg=EARTH_TONES["button_bg"], fg=EARTH_TONES["button_fg"], command=self.open_settings).pack(pady=5)
        tk.Button(self, text="Export Analytics", bg=EARTH_TONES["button_bg"], fg=EARTH_TONES["button_fg"], command=self.export_analytics).pack(pady=5)

        self.after(1000, self.refresh_ui)

    def enter_trade(self, ticker, shares, price, action, broker, stop_loss_percent, take_profit):
        self.platform.enter_trade(ticker, shares, price, action, broker, stop_loss_percent, take_profit)

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
            spread = calculate_spread(fetch_level2_data(ticker))
        else:
            spread = 0
        win_loss_ratio = calculate_win_loss_ratio() * 100

        self.cash_label.config(text=f"Cash: ${total_cash:.2f}")
        self.profit_label.config(text=f"Profit: ${total_profit:.2f}", fg=EARTH_TONES["profit"] if total_profit >= 0 else EARTH_TONES["loss"])
        self.margin_label.config(text=f"Margin: ${total_margin:.2f}")
        self.spread_label.config(text=f"Spread: ${spread:.2f}")
        self.win_loss_label.config(text=f"W/L Ratio: {win_loss_ratio:.1f}%")

    def open_settings(self):
        SettingsPanel(self, self.platform)

    def export_analytics(self):
        self.platform.logger.export_analytics()

    def refresh_ui(self):
        self.update_watchlist()
        self.update_trades()
        self.update_analytics()
        self.after(1000, self.refresh_ui)