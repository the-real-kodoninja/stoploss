import tkinter as tk
from tkinter import ttk
from ui.styles import EARTH_TONES

class TradeEntryForm(tk.Frame):
    def __init__(self, parent, submit_callback, brokers):
        super().__init__(parent, bg=EARTH_TONES["bg"])
        self.submit_callback = submit_callback

        tk.Label(self, text="Ticker:", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).grid(row=0, column=0)
        self.ticker_entry = tk.Entry(self, bg=EARTH_TONES["highlight"])
        self.ticker_entry.grid(row=0, column=1)

        tk.Label(self, text="Shares:", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).grid(row=1, column=0)
        self.shares_entry = tk.Entry(self, bg=EARTH_TONES["highlight"])
        self.shares_entry.grid(row=1, column=1)

        tk.Label(self, text="Price:", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).grid(row=2, column=0)
        self.price_entry = tk.Entry(self, bg=EARTH_TONES["highlight"])
        self.price_entry.grid(row=2, column=1)

        tk.Label(self, text="Stop Loss %:", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).grid(row=3, column=0)
        self.stop_loss_entry = tk.Entry(self, bg=EARTH_TONES["highlight"])
        self.stop_loss_entry.grid(row=3, column=1)

        tk.Label(self, text="Take Profit:", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).grid(row=4, column=0)
        self.take_profit_entry = tk.Entry(self, bg=EARTH_TONES["highlight"])
        self.take_profit_entry.grid(row=4, column=1)

        tk.Label(self, text="Broker:", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).grid(row=5, column=0)
        self.broker_var = tk.StringVar(self)
        self.broker_menu = ttk.OptionMenu(self, self.broker_var, brokers[0] if brokers else "", *brokers)
        self.broker_menu.grid(row=5, column=1)

        tk.Label(self, text="Order Type:", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).grid(row=6, column=0)
        self.order_type_var = tk.StringVar(value="limit")
        ttk.OptionMenu(self, self.order_type_var, "limit", "market").grid(row=6, column=1)

        self.trailing_stop_var = tk.BooleanVar()
        tk.Checkbutton(self, text="Trailing Stop", variable=self.trailing_stop_var, bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"]).grid(row=7, column=0)
        self.oco_var = tk.BooleanVar()
        tk.Checkbutton(self, text="OCO", variable=self.oco_var, bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"]).grid(row=7, column=1)

        self.option_var = tk.BooleanVar()
        tk.Checkbutton(self, text="Option", variable=self.option_var, bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"]).grid(row=8, column=0)
        tk.Label(self, text="Strike:", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).grid(row=9, column=0)
        self.strike_entry = tk.Entry(self, bg=EARTH_TONES["highlight"])
        self.strike_entry.grid(row=9, column=1)
        tk.Label(self, text="Expiry (YYYY-MM-DD):", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).grid(row=10, column=0)
        self.expiry_entry = tk.Entry(self, bg=EARTH_TONES["highlight"])
        self.expiry_entry.grid(row=10, column=1)

        tk.Button(self, text="Buy", bg=EARTH_TONES["button_bg"], fg=EARTH_TONES["button_fg"], command=self.submit_buy).grid(row=11, column=0)
        tk.Button(self, text="Short", bg=EARTH_TONES["button_bg"], fg=EARTH_TONES["button_fg"], command=self.submit_short).grid(row=11, column=1)

    def submit_buy(self):
        self.submit_callback(self.ticker_entry.get(), int(self.shares_entry.get()), float(self.price_entry.get()), "buy",
                             self.broker_var.get(), float(self.stop_loss_entry.get()), float(self.take_profit_entry.get()),
                             self.order_type_var.get(), self.trailing_stop_var.get(), self.oco_var.get(),
                             self.option_var.get(), float(self.strike_entry.get() or 0), self.expiry_entry.get() or None)

    def submit_short(self):
        self.submit_callback(self.ticker_entry.get(), int(self.shares_entry.get()), float(self.price_entry.get()), "short",
                             self.broker_var.get(), float(self.stop_loss_entry.get()), float(self.take_profit_entry.get()),
                             self.order_type_var.get(), self.trailing_stop_var.get(), self.oco_var.get(),
                             self.option_var.get(), float(self.strike_entry.get() or 0), self.expiry_entry.get() or None)

class Level2Display(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=EARTH_TONES["bg"])
        self.bids_label = tk.Label(self, text="Bids: ", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"])
        self.bids_label.pack()
        self.asks_label = tk.Label(self, text="Asks: ", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"])
        self.asks_label.pack()

    def update(self, ticker):
        level2 = fetch_level2_data(ticker)
        self.bids_label.config(text=f"Bids: {level2['bids'][:3]}")
        self.asks_label.config(text=f"Asks: {level2['asks'][:3]}")

class WatchlistManager(tk.Frame):
    def __init__(self, parent, add_callback, remove_callback):
        super().__init__(parent, bg=EARTH_TONES["bg"])
        tk.Label(self, text="Add Ticker:", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack(side="left")
        self.ticker_entry = tk.Entry(self, bg=EARTH_TONES["highlight"])
        self.ticker_entry.pack(side="left", padx=5)
        tk.Button(self, text="Add", bg=EARTH_TONES["button_bg"], fg=EARTH_TONES["button_fg"], command=lambda: add_callback(self.ticker_entry.get())).pack(side="left")
        tk.Button(self, text="Remove Selected", bg=EARTH_TONES["button_bg"], fg=EARTH_TONES["button_fg"], command=remove_callback).pack(side="left", padx=5)

class SettingsPanel(tk.Toplevel):
    def __init__(self, parent, platform):
        super().__init__(parent)
        self.platform = platform
        self.title("Settings")
        self.geometry("400x800")
        self.configure(bg=EARTH_TONES["bg"])

        tk.Label(self, text="Trading Rules", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack(pady=5)
        self.max_trades_var = tk.StringVar(value=str(MAX_TRADES))
        tk.Label(self, text="Max Trades:", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        tk.Entry(self, textvariable=self.max_trades_var, bg=EARTH_TONES["highlight"]).pack()

        self.max_duration_var = tk.StringVar(value=str(MAX_TRADE_DURATION))
        tk.Label(self, text="Max Trade Duration (s):", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        tk.Entry(self, textvariable=self.max_duration_var, bg=EARTH_TONES["highlight"]).pack()

        tk.Label(self, text="Broker Management", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack(pady=5)
        tk.Label(self, text="Broker Name:", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        self.broker_name_entry = tk.Entry(self, bg=EARTH_TONES["highlight"])
        self.broker_name_entry.pack()

        tk.Label(self, text="API Key:", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        self.api_key_entry = tk.Entry(self, bg=EARTH_TONES["highlight"])
        self.api_key_entry.pack()

        tk.Label(self, text="API Secret:", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        self.api_secret_entry = tk.Entry(self, bg=EARTH_TONES["highlight"])
        self.api_secret_entry.pack()

        self.broker_type_var = tk.StringVar(value="alpaca")
        tk.OptionMenu(self, self.broker_type_var, "alpaca", "binance").pack()

        tk.Label(self, text="Hotkeys", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack(pady=5)
        tk.Label(self, text="Buy Hotkey (e.g., <Control-b>):", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        self.buy_hotkey_entry = tk.Entry(self, bg=EARTH_TONES["highlight"])
        self.buy_hotkey_entry.pack()

        tk.Label(self, text="Sell Hotkey (e.g., <Control-s>):", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        self.sell_hotkey_entry = tk.Entry(self, bg=EARTH_TONES["highlight"])
        self.sell_hotkey_entry.pack()

        tk.Label(self, text="Scanner Criteria", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack(pady=5)
        tk.Label(self, text="Min Volume:", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        self.volume_entry = tk.Entry(self, bg=EARTH_TONES["highlight"])
        self.volume_entry.pack()
        tk.Label(self, text="Min Price:", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        self.price_min_entry = tk.Entry(self, bg=EARTH_TONES["highlight"])
        self.price_min_entry.pack()
        tk.Label(self, text="Max Price:", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        self.price_max_entry = tk.Entry(self, bg=EARTH_TONES["highlight"])
        self.price_max_entry.pack()
        tk.Label(self, text="RSI Threshold:", bg=EARTH_TONES["bg"], fg=EARTH_TONES["fg"], font=EARTH_TONES["font"]).pack()
        self.rsi_entry = tk.Entry(self, bg=EARTH_TONES["highlight"])
        self.rsi_entry.pack()

        tk.Button(self, text="Add Broker", bg=EARTH_TONES["button_bg"], fg=EARTH_TONES["button_fg"], command=self.add_broker).pack(pady=5)
        tk.Button(self, text="Save Settings", bg=EARTH_TONES["button_bg"], fg=EARTH_TONES["button_fg"], command=self.save_settings).pack(pady=5)

    def add_broker(self):
        name = self.broker_name_entry.get()
        credentials = {"api_key": self.api_key_entry.get(), "api_secret": self.api_secret_entry.get()}
        self.platform.add_broker(name, credentials, self.broker_type_var.get())

    def save_settings(self):
        self.platform.update_rule("MAX_TRADES", int(self.max_trades_var.get()))
        self.platform.update_rule("MAX_TRADE_DURATION", int(self.max_duration_var.get()))
        hotkeys = {"buy": self.buy_hotkey_entry.get(), "sell": self.sell_hotkey_entry.get()}
        scanner_criteria = {
            "volume": int(self.volume_entry.get() or 1000000),
            "price_min": float(self.price_min_entry.get() or 5),
            "price_max": float(self.price_max_entry.get() or 500),
            "rsi_threshold": float(self.rsi_entry.get() or 70)
        }
        with open("config/settings.py", "a") as f:
            f.write(f"\nHOTKEYS = {hotkeys}\nSCANNER_CRITERIA = {scanner_criteria}")
        self.destroy()