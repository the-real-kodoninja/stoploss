import React, { useEffect, useState } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const Trade = ({ ticker, onBack }) => {
  const [tradeData, setTradeData] = useState({ df: [], l2: { bids: [], asks: [] }, news: [] });

  useEffect(() => {
    axios.get(`/trade/${ticker}`).then((response) => {
      const data = response.data;
      data.df = JSON.parse(data.df); // Parse JSON string from Flask
      setTradeData(data);
    });
  }, [ticker]);

  const chartData = {
    labels: tradeData.df.map((_, i) => i),
    datasets: [
      {
        label: "Price",
        data: tradeData.df.map((d) => d.Close),
        borderColor: "#4A704A",
        backgroundColor: "#D9C2A7",
        fill: false
      }
    ]
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-darkOlive">{ticker} Details</h1>
      <p className="text-lg">Current Price: <span className="font-semibold">${tradeData.df.length ? tradeData.df[tradeData.df.length - 1].Close.toFixed(2) : "0.00"}</span></p>

      <section>
        <h2 className="text-xl text-olive">Level 2 Data</h2>
        <div className="bg-lightBrown p-4 rounded-lg shadow overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-olive">
                <th className="p-2">Bids</th>
                <th className="p-2">Asks</th>
              </tr>
            </thead>
            <tbody>
              {tradeData.l2.bids.map((bid, i) => (
                <tr key={i} className="border-b border-olive">
                  <td className="p-2">{bid[0]} ({bid[1]})</td>
                  <td className="p-2">{tradeData.l2.asks[i]?.[0]} ({tradeData.l2.asks[i]?.[1] || "-"})</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-xl text-olive">News</h2>
        <ul className="bg-lightBrown p-4 rounded-lg shadow space-y-2">
          {tradeData.news.map((article, index) => (
            <li key={index} className="text-sm">{article.title} - {article.source.name}</li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="text-xl text-olive">Price Chart</h2>
        <div className="bg-lightBrown p-4 rounded-lg shadow">
          <Line data={chartData} options={{ responsive: true, scales: { y: { beginAtZero: false } } }} />
        </div>
      </section>

      <button
        onClick={onBack}
        className="bg-olive text-beige px-4 py-2 rounded hover:bg-darkOlive transition"
      >
        Back
      </button>
    </div>
  );
};

export default Trade;