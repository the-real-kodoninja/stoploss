import csv
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from cloud.sync import upload_to_cloud

class TradeLogger:
    def __init__(self, log_file="trades_log.csv"):
        self.log_file = log_file
        with open(self.log_file, "a", newline="") as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(["Timestamp", "Ticker", "Action", "Shares", "Price", "Broker", "Profit", "Reason", "Option", "Strike", "Expiry", "Notes"])

    def log_trade(self, ticker, action, shares, price, broker, option=False, strike=None, expiry=None, notes=""):
        with open(self.log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), ticker, action, shares, price, broker, "", "entry", option, strike, expiry, notes])
        upload_to_cloud(self.log_file)

    def log_exit(self, ticker, action, shares, price, profit, reason, notes=""):
        with open(self.log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), ticker, action, shares, price, "", profit, reason, "", "", "", notes])
        upload_to_cloud(self.log_file)

    def export_analytics(self, export_file="reports/analytics_report.csv"):
        df = pd.read_csv(self.log_file)
        summary = {
            "Total Trades": len(df[df["Reason"] != "entry"]),
            "Total Profit": df["Profit"].sum(),
            "Wins": len(df[df["Profit"] > 0]),
            "Losses": len(df[df["Profit"] < 0]),
            "Average Profit": df["Profit"].mean()
        }
        pd.DataFrame([summary]).to_csv(export_file, index=False)
        upload_to_cloud(export_file)

    def visualize_journal(self):
        df = pd.read_csv(self.log_file)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        plt.figure(figsize=(10, 6))
        plt.plot(df[df["Profit"].notna()]["Timestamp"], df[df["Profit"].notna()]["Profit"].cumsum(), color="#4A704A")
        plt.title("Cumulative Profit Over Time")
        plt.xlabel("Time")
        plt.ylabel("Profit")
        plt.savefig("reports/journal_profit.png")
        upload_to_cloud("reports/journal_profit.png")