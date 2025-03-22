import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from core.data_feed import fetch_data
from core.analytics import analyze_all
from ui.styles import EARTH_TONES

class TradeChart(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=EARTH_TONES["bg"])
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(5, 7), sharex=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack()

    def update_chart(self, ticker, broker_type="alpaca"):
        df_1m = fetch_data(ticker, broker_type=broker_type, period="1d", interval="1m")
        df_1h = fetch_data(ticker, broker_type=broker_type, period="1d", interval="1h")
        analysis = analyze_all(df_1m)

        self.ax1.clear()
        self.ax1.plot(df_1m.index, df_1m['Close'], color=EARTH_TONES["fg"], label="1m Price")
        self.ax1.plot(df_1m.index, analysis["EMA_9"], color=EARTH_TONES["profit"], label="EMA 9")
        self.ax1.plot(df_1m.index, analysis["BB_upper"], color="gray", linestyle="--")
        self.ax1.plot(df_1m.index, analysis["BB_lower"], color="gray", linestyle="--")
        self.ax1.set_title(f"{ticker} 1m", color=EARTH_TONES["fg"])
        self.ax1.set_facecolor(EARTH_TONES["highlight"])
        self.ax1.legend()

        self.ax2.clear()
        self.ax2.plot(df_1h.index, df_1h['Close'], color=EARTH_TONES["fg"], label="1h Price")
        self.ax2.plot(df_1h.index, analysis["Ichimoku_A"], color="green", label="Ichimoku A")
        self.ax2.plot(df_1h.index, analysis["Ichimoku_B"], color="red", label="Ichimoku B")
        self.ax2.set_title(f"{ticker} 1h", color=EARTH_TONES["fg"])
        self.ax2.set_facecolor(EARTH_TONES["highlight"])
        self.ax2.legend()

        self.ax3.clear()
        self.ax3.plot(df_1m.index, analysis["RSI"], color=EARTH_TONES["fg"], label="RSI")
        self.ax3.axhline(70, color="red", linestyle="--")
        self.ax3.axhline(30, color="green", linestyle="--")
        self.ax3.set_title("RSI", color=EARTH_TONES["fg"])
        self.ax3.set_facecolor(EARTH_TONES["highlight"])
        self.ax3.legend()

        self.fig.patch.set_facecolor(EARTH_TONES["bg"])
        self.canvas.draw()