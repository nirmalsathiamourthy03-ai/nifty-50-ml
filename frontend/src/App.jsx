import React, { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import TopKpiCards from "./components/TopKpiCards";
import MarketAnalysisCard from "./components/MarketAnalysisCard";
import ModelComparisonCard from "./components/ModelComparisonCard";
import ModelPerformanceSummary from "./components/ModelPerformanceSummary";
import ConfusionMatrixCard from "./components/ConfusionMatrixCard";

export default function App() {
  const [activeTab, setActiveTab] = useState("overview");
  const [selectedCmModel, setSelectedCmModel] = useState("Random Forest");

  const [overviewData, setOverviewData] = useState(null);
  const [marketData, setMarketData] = useState(null);
  const [comparisonData, setComparisonData] = useState(null);
  const [summaryData, setSummaryData] = useState(null);
  const [cmData, setCmData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch initial data
  useEffect(() => {
    async function fetchData() {
      try {
        const [overviewRes, marketRes, compRes, summaryRes, cmRes] =
          await Promise.all([
            fetch("/api/overview").then((r) => (r.ok ? r.json() : null)),
            fetch("/api/market-analysis").then((r) => (r.ok ? r.json() : null)),
            fetch("/api/model-comparison").then((r) => (r.ok ? r.json() : null)),
            fetch("/api/model-summary").then((r) => (r.ok ? r.json() : null)),
            fetch(`/api/confusion-matrix?model=${encodeURIComponent(selectedCmModel)}`).then((r) =>
              r.ok ? r.json() : null
            ),
          ]);

        if (overviewRes) setOverviewData(overviewRes);
        if (marketRes) setMarketData(marketRes);
        if (compRes) setComparisonData(compRes);
        if (summaryRes) setSummaryData(summaryRes);
        if (cmRes) setCmData(cmRes);
      } catch (err) {
        console.error("Failed to fetch initial dashboard data:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  // Handle Confusion Matrix model change
  const handleModelChange = async (modelName) => {
    setSelectedCmModel(modelName);
    try {
      const res = await fetch(
        `/api/confusion-matrix?model=${encodeURIComponent(modelName)}`
      );
      if (res.ok) {
        const data = await res.json();
        setCmData(data);
      }
    } catch (e) {
      console.error("Failed to load confusion matrix for", modelName, e);
    }
  };

  return (
    <div className="min-h-screen bg-[#f1f5f9] flex text-slate-800 antialiased selection:bg-blue-100 selection:text-blue-900">
      {/* Left Navigation Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Dashboard */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Top Header */}
        <Header overviewData={overviewData} />

        {/* Dashboard Workspace */}
        <main className="p-4 sm:p-5 lg:p-6 space-y-4 max-w-[1560px] mx-auto w-full">
          {/* Top 3 KPI Cards */}
          <TopKpiCards overviewData={overviewData} />

          {/* Middle Row: Market Analysis (Candlestick + Sparklines) & Model Comparison (Grouped Bar Chart) */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
            <div className="lg:col-span-7">
              <MarketAnalysisCard marketData={marketData} />
            </div>
            <div className="lg:col-span-5">
              <ModelComparisonCard comparisonData={comparisonData} />
            </div>
          </div>

          {/* Bottom Row: Model Performance Summary Table & Confusion Matrix Comparison */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
            <div className="lg:col-span-7">
              <ModelPerformanceSummary summaryData={summaryData} />
            </div>
            <div className="lg:col-span-5">
              <ConfusionMatrixCard
                cmData={cmData}
                selectedModel={selectedCmModel}
                onModelChange={handleModelChange}
              />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
