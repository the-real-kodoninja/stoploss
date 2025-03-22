import csv
from datetime import datetime
import pandas as pd
from cloud.sync import upload_to_cloud

class TradeLogger:
    def __init__(self, log_file="trades_log.csv"):
        self.log_file = log_file
        with open(self.log_file, "a", newline="") as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(["Timestamp", "Ticker", "Action", "Shares", "Price", "Broker", "Profit", "Reason"])

    def log_trade(self, ticker, action, shares, price, broker):
        with open(self.log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), ticker, action, shares, price, broker, "", "entry"])
        upload_to_cloud(self.log_file)

    def log_exit(self, ticker, action, shares, price, profit, reason):
        with open(self.log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), ticker, action, shares, price, "", profit, reason])
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