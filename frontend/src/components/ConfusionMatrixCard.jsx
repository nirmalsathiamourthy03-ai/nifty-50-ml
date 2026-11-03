import React, { useState } from "react";
import { Scale, ChevronDown, Target, TrendingUp, BarChart2 } from "lucide-react";

export default function ConfusionMatrixCard({
  cmData,
  onModelChange,
  selectedModel = "Random Forest",
}) {
  const models = [
    "Random Forest",
    "Gradient Boosting",
    "XGBoost",
    "LightGBM",
    "Logistic Regression",
  ];

  const gap = cmData?.gap_movement || {
    actual_gap_up: { pred_gap_down: 334, pred_gap_up: 298 },
    actual_gap_down: { pred_gap_down: 229, pred_gap_up: 445 },
  };

  const day = cmData?.full_day_movement || {
    actual_up: { pred_down: 316, pred_up: 334 },
    actual_down: { pred_down: 287, pred_up: 386 },
  };

  const bestModelName = cmData?.best_model || "Random Forest";
  const selectionScore = cmData?.selection_score || "59.73";
  const modelConfidence = cmData?.model_confidence || "59.8";

  // Color intensity helper for 2x2 cells
  const getCellBg = (val, max = 500) => {
    if (val > 400) return "bg-[#3b82f6] text-white font-bold";
    if (val > 320) return "bg-[#93c5fd] text-slate-900 font-semibold";
    if (val > 280) return "bg-[#bfdbfe] text-slate-900 font-semibold";
    return "bg-[#dbeafe] text-slate-800 font-semibold";
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden flex flex-col justify-between">
      {/* Header Banner */}
      <div>
        <div className="bg-[#1e3a8a] text-white px-5 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Scale className="w-5 h-5 text-sky-300" />
            <h3 className="font-semibold text-base tracking-wide">
              Confusion Matrix Comparison
            </h3>
          </div>

          {/* Model Selector Dropdown */}
          <div className="relative">
            <select
              value={selectedModel}
              onChange={(e) => onModelChange && onModelChange(e.target.value)}
              className="bg-[#172554] text-white text-xs font-medium py-1.5 px-3 pr-7 rounded-lg border border-blue-400/40 focus:outline-none focus:ring-1 focus:ring-sky-400 cursor-pointer appearance-none"
            >
              {models.map((m) => (
                <option key={m} value={m} className="bg-slate-900 text-white">
                  {m}
                </option>
              ))}
            </select>
            <ChevronDown className="w-3.5 h-3.5 text-sky-200 absolute right-2 top-2.5 pointer-events-none" />
          </div>
        </div>

        {/* 2 Side-by-Side Confusion Matrices */}
        <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Left: Gap Movement */}
          <div className="border border-slate-200/80 rounded-xl p-3 bg-slate-50/40">
            <h4 className="text-center font-bold text-xs text-slate-800 mb-2.5">
              Gap Movement
            </h4>
            <div className="flex flex-col items-center">
              {/* Matrix Table */}
              <div className="flex items-center gap-2">
                {/* Row Headers */}
                <div className="flex flex-col justify-around text-[10px] font-semibold text-slate-500 text-right h-24 py-1">
                  <div>Actual<br /><span className="text-slate-700">GAP UP</span></div>
                  <div>Actual<br /><span className="text-slate-700">GAP DOWN</span></div>
                </div>

                {/* 2x2 Grid */}
                <div className="grid grid-cols-2 gap-1 w-44 h-24">
                  <div
                    className={`flex items-center justify-center rounded text-sm ${getCellBg(
                      gap.actual_gap_up.pred_gap_down
                    )}`}
                  >
                    {gap.actual_gap_up.pred_gap_down}
                  </div>
                  <div
                    className={`flex items-center justify-center rounded text-sm ${getCellBg(
                      gap.actual_gap_up.pred_gap_up
                    )}`}
                  >
                    {gap.actual_gap_up.pred_gap_up}
                  </div>
                  <div
                    className={`flex items-center justify-center rounded text-sm ${getCellBg(
                      gap.actual_gap_down.pred_gap_down
                    )}`}
                  >
                    {gap.actual_gap_down.pred_gap_down}
                  </div>
                  <div
                    className={`flex items-center justify-center rounded text-sm ${getCellBg(
                      gap.actual_gap_down.pred_gap_up
                    )}`}
                  >
                    {gap.actual_gap_down.pred_gap_up}
                  </div>
                </div>
              </div>

              {/* Column Footers */}
              <div className="grid grid-cols-2 gap-1 w-44 ml-14 mt-1.5 text-center text-[10px] font-medium text-slate-500">
                <div>Predicted<br /><span className="font-semibold text-slate-700">GAP DOWN</span></div>
                <div>Predicted<br /><span className="font-semibold text-slate-700">GAP UP</span></div>
              </div>
            </div>
          </div>

          {/* Right: Full-Day Movement */}
          <div className="border border-slate-200/80 rounded-xl p-3 bg-slate-50/40">
            <h4 className="text-center font-bold text-xs text-slate-800 mb-2.5">
              Full-Day Movement
            </h4>
            <div className="flex flex-col items-center">
              {/* Matrix Table */}
              <div className="flex items-center gap-2">
                {/* Row Headers */}
                <div className="flex flex-col justify-around text-[10px] font-semibold text-slate-500 text-right h-24 py-1">
                  <div>Actual<br /><span className="text-slate-700">UP</span></div>
                  <div>Actual<br /><span className="text-slate-700">DOWN</span></div>
                </div>

                {/* 2x2 Grid */}
                <div className="grid grid-cols-2 gap-1 w-44 h-24">
                  <div
                    className={`flex items-center justify-center rounded text-sm ${getCellBg(
                      day.actual_up.pred_down
                    )}`}
                  >
                    {day.actual_up.pred_down}
                  </div>
                  <div
                    className={`flex items-center justify-center rounded text-sm ${getCellBg(
                      day.actual_up.pred_up
                    )}`}
                  >
                    {day.actual_up.pred_up}
                  </div>
                  <div
                    className={`flex items-center justify-center rounded text-sm ${getCellBg(
                      day.actual_down.pred_down
                    )}`}
                  >
                    {day.actual_down.pred_down}
                  </div>
                  <div
                    className={`flex items-center justify-center rounded text-sm ${getCellBg(
                      day.actual_down.pred_up
                    )}`}
                  >
                    {day.actual_down.pred_up}
                  </div>
                </div>
              </div>

              {/* Column Footers */}
              <div className="grid grid-cols-2 gap-1 w-44 ml-12 mt-1.5 text-center text-[10px] font-medium text-slate-500">
                <div>Predicted<br /><span className="font-semibold text-slate-700">DOWN</span></div>
                <div>Predicted<br /><span className="font-semibold text-slate-700">UP</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Mini Cards */}
      <div className="p-4 pt-0 grid grid-cols-1 sm:grid-cols-2 gap-3">
        {/* Best Model Mini Card */}
        <div className="bg-[#fdf2f4] border border-pink-100 rounded-xl p-3 flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-pink-100 flex items-center justify-center text-pink-600 shrink-0">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <div className="text-[11px] font-semibold text-slate-600 uppercase tracking-wider">
              Best Model
            </div>
            <div className="text-base font-bold text-slate-900 leading-tight">
              {bestModelName}
            </div>
            <div className="text-[11px] text-slate-500">
              (Selection Score: {selectionScore})
            </div>
          </div>
        </div>

        {/* Model Confidence Mini Card */}
        <div className="bg-[#eff6ff] border border-blue-100 rounded-xl p-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 shrink-0">
              <BarChart2 className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[11px] font-semibold text-slate-600 uppercase tracking-wider">
                Model Confidence
              </div>
              <div className="text-2xl font-bold text-slate-900 leading-none mt-1">
                ~ {modelConfidence}%
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
