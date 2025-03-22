import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from core.data_feed import fetch_data
from ui.styles import EARTH_TONES

class TradeChart(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=EARTH_TONES["bg"])
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(5, 5), sharex=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack()

    def update_chart(self, ticker, broker_type="alpaca"):
        df_1m = fetch_data(ticker, broker_type=broker_type, period="1d", interval="1m")
        df_1h = fetch_data(ticker, broker_type=broker_type, period="1d", interval="1h")

        self.ax1.clear()
        self.ax1.plot(df_1m.index, df_1m['Close'], color=EARTH_TONES["fg"], label="1m Price")
        ema9 = df_1m['Close'].ewm(span=9, adjust=False).mean()
        self.ax1.plot(df_1m.index, ema9, color=EARTH_TONES["profit"], label="EMA 9")
        self.ax1.set_title(f"{ticker} 1m", color=EARTH_TONES["fg"])
        self.ax1.set_facecolor(EARTH_TONES["highlight"])
        self.ax1.legend()

        self.ax2.clear()
        self.ax2.plot(df_1h.index, df_1h['Close'], color=EARTH_TONES["fg"], label="1h Price")
        ema21 = df_1h['Close'].ewm(span=21, adjust=False).mean()
        self.ax2.plot(df_1h.index, ema21, color=EARTH_TONES["profit"], label="EMA 21")
        self.ax2.set_title(f"{ticker} 1h", color=EARTH_TONES["fg"])
        self.ax2.set_facecolor(EARTH_TONES["highlight"])
        self.ax2.legend()

        self.fig.patch.set_facecolor(EARTH_TONES["bg"])
        self.canvas.draw()