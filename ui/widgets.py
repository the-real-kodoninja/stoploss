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

        tk.Button(self, text="Buy", bg=EARTH_TONES["button_bg"], fg=EARTH_TONES["button_fg"], command=self.submit_buy).grid(row=6, column=0)
        tk.Button(self, text="Short", bg=EARTH_TONES["button_bg"], fg=EARTH_TONES["button_fg"], command=self.submit_short).grid(row=6, column=1)

    def submit_buy(self):
        self.submit_callback(self.ticker_entry.get(), int(self.shares_entry.get()), float(self.price_entry.get()), "buy",
                             self.broker_var.get(), float(self.stop_loss_entry.get()), float(self.take_profit_entry.get()))

    def submit_short(self):
        self.submit_callback(self.ticker_entry.get(), int(self.shares_entry.get()), float(self.price_entry.get()), "short",
                             self.broker_var.get(), float(self.stop_loss_entry.get()), float(self.take_profit_entry.get()))

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