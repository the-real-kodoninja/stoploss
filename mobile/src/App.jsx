import React, { useState } from "react";
import Dashboard from "./Dashboard";
import Trade from "./Trade";

const App = () => {
  const [view, setView] = useState("dashboard");
  const [selectedTicker, setSelectedTicker] = useState(null);

  const handleTradeView = (ticker) => {
    setSelectedTicker(ticker);
    setView("trade");
  };

  return (
    <div className="min-h-screen bg-beige p-4">
      {view === "dashboard" ? (
        <Dashboard onTradeClick={handleTradeView} />
      ) : (
        <Trade ticker={selectedTicker} onBack={() => setView("dashboard")} />
      )}
    </div>
  );
};

export default App;