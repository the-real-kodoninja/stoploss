import React, { useEffect, useState } from "react";
import io from "socket.io-client";

const Dashboard = ({ onTradeClick }) => {
  const [data, setData] = useState({ trades: [], analytics: {}, watchlist: {} });
  const socket = io("http://localhost:5000");

  useEffect(() => {
    socket.on("update", (newData) => setData(newData));
    return () => socket.disconnect();
  }, [socket]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-darkOlive">Stop Loss Mobile Dashboard</h1>

      <section>
        <h2 className="text-xl text-olive">Analytics</h2>
        <div className="bg-lightBrown p-4 rounded-lg shadow">
          <p>Cash: <span className="font-semibold">${data.analytics.cash?.toFixed(2) || "0.00"}</span></p>
          <p>Profit: <span className="font-semibold">${data.analytics.profit?.toFixed(2) || "0.00"}</span></p>
          <p>Active Trades: <span className="font-semibold">{data.analytics.active_trades || 0}</span></p>
        </div>
      </section>

      <section>
        <h2 className="text-xl text-olive">Watchlist</h2>
        <div className="bg-lightBrown p-4 rounded-lg shadow overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-olive">
                <th className="p-2">Ticker</th>
                <th className="p-2">Price</th>
                <th className="p-2">Action</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(data.watchlist).map(([ticker, price]) => (
                <tr key={ticker} className="border-b border-olive">
                  <td className="p-2">{ticker}</td>
                  <td className="p-2">${price.toFixed(2)}</td>
                  <td className="p-2">
                    <button
                      onClick={() => onTradeClick(ticker)}
                      className="bg-olive text-beige px-2 py-1 rounded hover:bg-darkOlive transition"
                    >
                      Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-xl text-olive">Recent Trades</h2>
        <div className="bg-lightBrown p-4 rounded-lg shadow overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-olive">
                <th className="p-2">Timestamp</th>
                <th className="p-2">Ticker</th>
                <th className="p-2">Action</th>
                <th className="p-2">Price</th>
                <th className="p-2">Profit</th>
              </tr>
            </thead>
            <tbody>
              {data.trades.map((trade, index) => (
                <tr key={index} className="border-b border-olive">
                  <td className="p-2">{trade.Timestamp}</td>
                  <td className="p-2">{trade.Ticker}</td>
                  <td className="p-2">{trade.Action}</td>
                  <td className="p-2">{trade.Price}</td>
                  <td className="p-2">{trade.Profit || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <div className="flex space-x-4">
        <button className="bg-olive text-beige px-4 py-2 rounded hover:bg-darkOlive transition">
          Refresh
        </button>
        <button
          onClick={() => alert("Nimbus.AI is running autonomously")}
          className="bg-olive text-beige px-4 py-2 rounded hover:bg-darkOlive transition"
        >
          Nimbus.AI Status
        </button>
      </div>
    </div>
  );
};

export default Dashboard;