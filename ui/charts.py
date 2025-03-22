import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from core.data_feed import fetch_data
from ui.styles import EARTH_TONES

class TradeChart(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=EARTH_TONES["bg"])
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack()

    def update_chart(self, ticker):
        df = fetch_data(ticker)
        self.ax.clear()
        self.ax.plot(df.index, df['Close'], color=EARTH_TONES["fg"], label="Price")
        self.ax.set_title(f"{ticker} Price", color=EARTH_TONES["fg"])
        self.ax.set_facecolor(EARTH_TONES["highlight"])
        self.ax.legend()
        self.fig.patch.set_facecolor(EARTH_TONES["bg"])
        self.canvas.draw()