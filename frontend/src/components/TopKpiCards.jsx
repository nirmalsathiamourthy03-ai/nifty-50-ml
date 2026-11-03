import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

export default function TopKpiCards({ overviewData }) {
  const lastCloseFormatted = overviewData?.last_close_formatted || '₹23,810.85';
  const changeFormatted = overviewData?.change_formatted || '+0.56%';
  const isPositive = overviewData?.is_positive !== false;

  const target1 = overviewData?.target_1_gap || {
    label: 'GAP UP',
    probability: 71.6,
    is_up: true
  };

  const target2 = overviewData?.target_2_day || {
    label: 'UP',
    probability: 63.3,
    is_up: true
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-5">
      {/* Card 1: Previous Day Closing Price */}
      <div className="bg-[#fff9f2] rounded-2xl p-5 border border-[#fed7aa] shadow-xs flex flex-col justify-between">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
            Previous Day Closing Price
          </span>
          <div className="p-1.5 bg-[#dbeafe] rounded-full text-[#2563eb]">
            <TrendingUp className="w-4 h-4 stroke-[2.5]" />
          </div>
        </div>

        <div className="flex items-baseline space-x-3 mt-1">
          <span className="text-3xl font-extrabold tracking-tight text-[#0f172a]">
            {lastCloseFormatted}
          </span>
          <span className="inline-flex items-center text-xs font-bold px-2 py-0.5 rounded-md bg-[#dcfce7] text-[#16a34a]">
            ▲ {changeFormatted}
          </span>
        </div>
      </div>

      {/* Card 2: Prediction Target 1 (Gap Movement) */}
      <div className="bg-[#f0f7ff] rounded-2xl p-5 border border-[#bfdbfe] shadow-xs flex flex-col justify-between">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
            Prediction Target 1 (Gap Movement)
          </span>
          <div className="p-1.5 bg-[#dbeafe] rounded-full text-[#2563eb]">
            <TrendingUp className="w-4 h-4 stroke-[2.5]" />
          </div>
        </div>

        <div className="flex items-center space-x-4 mt-1">
          <span className="px-5 py-1.5 rounded-full bg-[#1e3a8a] text-white text-sm font-bold tracking-wider shadow-xs uppercase">
            {target1.label}
          </span>
          <span className="text-3xl font-extrabold tracking-tight text-[#0f172a]">
            {target1.probability.toFixed(1)}%
          </span>
        </div>
      </div>

      {/* Card 3: Prediction Target 2 (Full-Day Movement) */}
      <div className="bg-[#fff1f2] rounded-2xl p-5 border border-[#fbcfe8] shadow-xs flex flex-col justify-between">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
            Prediction Target 2 (Full-Day Movement)
          </span>
          <div className="p-1.5 bg-[#dbeafe] rounded-full text-[#2563eb]">
            <TrendingUp className="w-4 h-4 stroke-[2.5]" />
          </div>
        </div>

        <div className="flex items-center space-x-4 mt-1">
          <span className="px-6 py-1.5 rounded-full bg-[#1e3a8a] text-white text-sm font-bold tracking-wider shadow-xs uppercase">
            {target2.label}
          </span>
          <span className="text-3xl font-extrabold tracking-tight text-[#0f172a]">
            {target2.probability.toFixed(1)}%
          </span>
        </div>
      </div>
    </div>
  );
}
