import React from "react";
import { Trophy, Lightbulb, CheckCircle2 } from "lucide-react";

export default function ModelPerformanceSummary({ summaryData }) {
  const rows = summaryData?.rows || [
    {
      model: "Logistic Regression",
      accuracy: "59.3%",
      precision: "56.8%",
      recall: "61.2%",
      f1: "59.0%",
      auc: "0.5562",
      cm_str: "[[ 472, 331],\n [ 354, 392 ]]",
      selection_score: "59.15",
      is_best: false,
    },
    {
      model: "Random Forest",
      accuracy: "59.8%",
      precision: "57.5%",
      recall: "62.1%",
      f1: "59.7%",
      auc: "0.5242",
      cm_str: "[[ 487, 316],\n [ 349, 387 ]]",
      selection_score: "59.73",
      is_best: true,
    },
    {
      model: "Gradient Boosting",
      accuracy: "59.7%",
      precision: "57.0%",
      recall: "61.9%",
      f1: "59.4%",
      auc: "0.5223",
      cm_str: "[[ 480, 323],\n [ 351, 385 ]]",
      selection_score: "59.40",
      is_best: false,
    },
    {
      model: "XGBoost",
      accuracy: "59.8%",
      precision: "57.2%",
      recall: "61.7%",
      f1: "59.4%",
      auc: "0.5192",
      cm_str: "[[ 482, 321],\n [ 355, 381 ]]",
      selection_score: "59.38",
      is_best: false,
    },
    {
      model: "LightGBM",
      accuracy: "59.8%",
      precision: "57.1%",
      recall: "61.5%",
      f1: "59.3%",
      auc: "0.5177",
      cm_str: "[[ 479, 324],\n [ 353, 383 ]]",
      selection_score: "59.27",
      is_best: false,
    },
  ];

  const keyInsights = summaryData?.key_insights || [
    "Random Forest shows the best overall performance (Selection Score: 59.73)",
    "Market is showing a bullish trend with RSI at 58.7",
    "Bollinger Bands indicate moderate volatility",
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden flex flex-col justify-between">
      {/* Header Banner */}
      <div>
        <div className="bg-[#1e3a8a] text-white px-5 py-3 flex items-center gap-2">
          <Trophy className="w-5 h-5 text-amber-300" />
          <h3 className="font-semibold text-base tracking-wide">
            Model Performance Summary
          </h3>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-200 text-slate-600 font-semibold bg-slate-50/70">
                <th className="py-2.5 px-4">Model</th>
                <th className="py-2.5 px-3 text-center">Accuracy ↑</th>
                <th className="py-2.5 px-3 text-center">Precision ↑</th>
                <th className="py-2.5 px-3 text-center">Recall ↑</th>
                <th className="py-2.5 px-3 text-center">F1-Score ↑</th>
                <th className="py-2.5 px-3 text-center">ROC-AUC ↑</th>
                <th className="py-2.5 px-3 text-center">Confusion Matrix</th>
                <th className="py-2.5 px-4 text-center">Selection Score ↑</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rows.map((row, idx) => {
                const isSelected = row.is_best || row.model === "Random Forest";
                return (
                  <tr
                    key={idx}
                    className={`transition-colors ${
                      isSelected
                        ? "bg-[#e0f2fe]/70 font-semibold text-slate-900 border-y border-sky-200"
                        : "hover:bg-slate-50 text-slate-700"
                    }`}
                  >
                    <td className="py-2.5 px-4 font-medium flex items-center gap-2">
                      {row.model}
                    </td>
                    <td className="py-2.5 px-3 text-center">{row.accuracy}</td>
                    <td className="py-2.5 px-3 text-center">{row.precision}</td>
                    <td className="py-2.5 px-3 text-center">{row.recall}</td>
                    <td className="py-2.5 px-3 text-center">{row.f1}</td>
                    <td className="py-2.5 px-3 text-center font-mono">{row.auc}</td>
                    <td className="py-2 px-3 text-center font-mono text-[11px] leading-tight text-slate-600 whitespace-pre">
                      {row.cm_str}
                    </td>
                    <td className="py-2.5 px-4 text-center font-bold text-slate-900">
                      {row.selection_score}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Key Insights Footer Box */}
      <div className="bg-[#f0f5fa] rounded-xl p-3.5 mx-4 my-3 border border-slate-200/80 flex flex-col sm:flex-row sm:items-center gap-4">
        <div className="flex items-center gap-2 text-slate-800 font-bold text-sm shrink-0">
          <Lightbulb className="w-5 h-5 text-blue-600" />
          <span>Key Insights</span>
        </div>
        <div className="flex flex-col gap-1.5 text-xs text-slate-700 flex-1">
          {keyInsights.map((insight, idx) => (
            <div key={idx} className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <span>{insight}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
