import React from 'react';
import { BarChart3, Calendar } from 'lucide-react';

export default function Header({ overviewData }) {
  const lastUpdated = overviewData?.last_updated_formatted || 'Nov 03, 2026 • 04:30 PM IST';

  return (
    <header className="bg-[#192b49] text-white px-6 py-4 flex flex-col md:flex-row md:items-center md:justify-between border-b border-[#21375d] shadow-sm">
      {/* Title & Subtitle */}
      <div className="flex items-center space-x-3.5 mb-2 md:mb-0">
        <div className="p-2 bg-[#2563eb]/20 rounded-lg text-[#60a5fa] border border-[#3b82f6]/30">
          <BarChart3 className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-xl md:text-2xl font-bold tracking-tight text-white flex items-center space-x-2">
            <span>NIFTY 50 ML Dashboard</span>
          </h1>
          <p className="text-xs text-[#94a3b8] font-medium tracking-wide">
            Next Trading Day Movement Prediction
          </p>
        </div>
      </div>

      {/* Timestamp & Live Badge */}
      <div className="flex items-center space-x-3 self-end md:self-auto">
        <div className="flex items-center text-xs text-[#94a3b8] bg-[#14223b] px-3 py-1.5 rounded-lg border border-[#20365c]">
          <Calendar className="w-3.5 h-3.5 mr-1.5 text-[#60a5fa]" />
          <span>Last Updated: <strong className="text-slate-200 font-semibold">{lastUpdated}</strong></span>
        </div>

        <span className="bg-[#2563eb] text-white text-[11px] font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow-sm flex items-center space-x-1">
          <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse inline-block mr-1"></span>
          Live
        </span>
      </div>
    </header>
  );
}
