import React, { useState } from 'react';
import { BarChart2 } from 'lucide-react';

export default function MarketAnalysisCard({ marketData }) {
  const [activeSubTab, setActiveSubTab] = useState('candlestick');
  const [hoveredCandle, setHoveredCandle] = useState(null);

  const series = marketData?.series || [];
  const latestRsi = marketData?.latest_rsi || 58.7;

  // Chart dimensions & calculations
  const width = 680;
  const height = 220;
  const padding = { top: 20, right: 55, bottom: 25, left: 10 };

  // Calculate scales from series
  const validCloses = series.map(d => d.close).filter(c => c > 0);
  const minPrice = validCloses.length ? Math.min(...series.map(d => Math.min(d.low, d.sma20 || d.low))) * 0.995 : 23000;
  const maxPrice = validCloses.length ? Math.max(...series.map(d => Math.max(d.high, d.sma20 || d.high))) * 1.005 : 25500;

  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;

  const xScale = (index) => padding.left + (index / Math.max(1, series.length - 1)) * innerWidth;
  const yScale = (price) => padding.top + innerHeight - ((price - minPrice) / (maxPrice - minPrice || 1)) * innerHeight;

  // Generate SVG path for a line
  const makeLinePath = (key) => {
    return series
      .map((d, i) => {
        const val = d[key];
        if (!val) return null;
        const x = xScale(i);
        const y = yScale(val);
        return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
      })
      .filter(Boolean)
      .join(' ');
  };

  const sma5Path = makeLinePath('sma5');
  const sma10Path = makeLinePath('sma10');
  const sma20Path = makeLinePath('sma20');

  // Mini Sparklines
  // 1. RSI
  const rsiWidth = 180;
  const rsiHeight = 55;
  const rsiXScale = (i) => (i / Math.max(1, series.length - 1)) * rsiWidth;
  const rsiYScale = (val) => rsiHeight - (Math.min(100, Math.max(0, val)) / 100) * rsiHeight;
  const rsiPath = series.map((d, i) => `${i === 0 ? 'M' : 'L'} ${rsiXScale(i)} ${rsiYScale(d.rsi || 50)}`).join(' ');

  // 2. Bollinger Bands
  const bbWidth = 180;
  const bbHeight = 55;
  const bbUpperPath = series.map((d, i) => `${i === 0 ? 'M' : 'L'} ${rsiXScale(i)} ${yScale(d.bb_upper || d.close) * (bbHeight / height)}`).join(' ');
  const bbMiddlePath = series.map((d, i) => `${i === 0 ? 'M' : 'L'} ${rsiXScale(i)} ${yScale(d.bb_middle || d.close) * (bbHeight / height)}`).join(' ');
  const bbLowerPath = series.map((d, i) => `${i === 0 ? 'M' : 'L'} ${rsiXScale(i)} ${yScale(d.bb_lower || d.close) * (bbHeight / height)}`).join(' ');

  // 3. MACD
  const macdWidth = 180;
  const macdHeight = 55;
  const macdPath = series.map((d, i) => `${i === 0 ? 'M' : 'L'} ${rsiXScale(i)} ${28 - (d.macd || 0) * 0.15}`).join(' ');
  const macdSigPath = series.map((d, i) => `${i === 0 ? 'M' : 'L'} ${rsiXScale(i)} ${28 - (d.macd_signal || 0) * 0.15}`).join(' ');

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden flex flex-col justify-between">
      {/* Dark Navy Header Bar */}
      <div className="bg-[#1e3a8a] text-white px-5 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <BarChart2 className="w-5 h-5 text-blue-300" />
          <h2 className="text-sm font-bold tracking-wide">Market Analysis</h2>
        </div>
      </div>

      <div className="p-4 flex flex-col flex-1">
        {/* Navigation Tabs & Legend */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-slate-100 pb-2 mb-3">
          <div className="flex items-center space-x-6 text-xs font-semibold">
            {['candlestick', 'trend', 'indicators'].map((tab) => {
              const label = tab === 'candlestick' ? 'Candlestick' : tab === 'trend' ? 'Trend Pattern' : 'Indicators';
              const isActive = activeSubTab === tab;
              return (
                <button
                  key={tab}
                  onClick={() => setActiveSubTab(tab)}
                  className={`pb-1.5 transition-colors cursor-pointer capitalize ${
                    isActive
                      ? 'text-[#2563eb] border-b-2 border-[#2563eb] font-bold'
                      : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  {label}
                </button>
              );
            })}
          </div>

          {/* Moving Average Legend */}
          <div className="flex items-center space-x-4 text-[11px] font-medium text-slate-600 mt-2 sm:mt-0">
            <span className="flex items-center space-x-1">
              <span className="w-3.5 h-0.5 bg-[#2563eb] inline-block"></span>
              <span>SMA 5</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-3.5 h-0.5 bg-[#f59e0b] inline-block"></span>
              <span>SMA 10</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-3.5 h-0.5 bg-[#1e3a8a] inline-block"></span>
              <span>SMA 20</span>
            </span>
          </div>
        </div>

        {/* Main Candlestick Chart */}
        <div className="relative w-full h-[220px] select-none">
          <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full overflow-visible">
            {/* Grid Lines */}
            {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => {
              const y = padding.top + innerHeight * pct;
              const price = maxPrice - (maxPrice - minPrice) * pct;
              return (
                <g key={i}>
                  <line x1={padding.left} y1={y} x2={width - padding.right} y2={y} stroke="#f1f5f9" strokeDasharray="3 3" />
                  <text x={width - padding.right + 6} y={y + 3} fill="#94a3b8" fontSize="10" fontFamily="sans-serif">
                    {Math.round(price).toLocaleString()}
                  </text>
                </g>
              );
            })}

            {/* Moving Average Lines */}
            {sma5Path && <path d={sma5Path} fill="none" stroke="#2563eb" strokeWidth="1.6" />}
            {sma10Path && <path d={sma10Path} fill="none" stroke="#f59e0b" strokeWidth="1.6" />}
            {sma20Path && <path d={sma20Path} fill="none" stroke="#1e3a8a" strokeWidth="1.8" />}

            {/* Candlesticks */}
            {series.map((d, i) => {
              const x = xScale(i);
              const isUp = d.close >= d.open;
              const color = isUp ? '#10b981' : '#ef4444';
              const yHigh = yScale(d.high);
              const yLow = yScale(d.low);
              const yOpen = yScale(d.open);
              const yClose = yScale(d.close);
              const candleTop = Math.min(yOpen, yClose);
              const candleHeight = Math.max(2, Math.abs(yClose - yOpen));
              const candleWidth = Math.max(4, Math.min(10, (innerWidth / series.length) * 0.65));

              return (
                <g
                  key={i}
                  onMouseEnter={() => setHoveredCandle(d)}
                  onMouseLeave={() => setHoveredCandle(null)}
                  className="cursor-pointer transition-opacity hover:opacity-80"
                >
                  {/* High-Low Wick */}
                  <line x1={x} y1={yHigh} x2={x} y2={yLow} stroke={color} strokeWidth="1.2" />
                  {/* Real Body */}
                  <rect
                    x={x - candleWidth / 2}
                    y={candleTop}
                    width={candleWidth}
                    height={candleHeight}
                    fill={color}
                    rx="1"
                  />
                </g>
              );
            })}

            {/* X-Axis Date Labels */}
            {series.filter((_, i) => i % Math.ceil(series.length / 5) === 0 || i === series.length - 1).map((d, i, arr) => {
              const origIndex = series.indexOf(d);
              return (
                <text
                  key={i}
                  x={xScale(origIndex)}
                  y={height - 6}
                  fill="#64748b"
                  fontSize="10"
                  textAnchor="middle"
                  fontFamily="sans-serif"
                >
                  {d.date}
                </text>
              );
            })}
          </svg>

          {/* Hover Tooltip */}
          {hoveredCandle && (
            <div className="absolute top-2 left-4 bg-slate-900/90 text-white text-[11px] p-2 rounded-lg shadow-lg pointer-events-none backdrop-blur-xs flex items-center space-x-3 z-10">
              <span className="font-bold text-blue-300">{hoveredCandle.full_date}</span>
              <span>O: {hoveredCandle.open}</span>
              <span>H: {hoveredCandle.high}</span>
              <span>L: {hoveredCandle.low}</span>
              <span className={hoveredCandle.close >= hoveredCandle.open ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
                C: {hoveredCandle.close}
              </span>
            </div>
          )}
        </div>

        {/* 3 Sub-Indicators Row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 mt-1 border-t border-slate-100">
          {/* Sub 1: RSI (14) */}
          <div className="bg-slate-50/70 p-2.5 rounded-xl border border-slate-200/80 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[11px] font-bold text-slate-700">RSI (14)</span>
              <span className="text-xs font-extrabold text-[#7e22ce]">{latestRsi.toFixed(1)}</span>
            </div>
            <div className="h-12 w-full relative">
              <svg viewBox={`0 0 ${rsiWidth} ${rsiHeight}`} className="w-full h-full overflow-visible">
                <line x1="0" y1={rsiHeight * 0.3} x2={rsiWidth} y2={rsiHeight * 0.3} stroke="#ef4444" strokeDasharray="2 2" strokeWidth="0.8" />
                <line x1="0" y1={rsiHeight * 0.7} x2={rsiWidth} y2={rsiHeight * 0.7} stroke="#10b981" strokeDasharray="2 2" strokeWidth="0.8" />
                <path d={rsiPath} fill="none" stroke="#9333ea" strokeWidth="1.5" />
              </svg>
            </div>
          </div>

          {/* Sub 2: Bollinger Bands */}
          <div className="bg-slate-50/70 p-2.5 rounded-xl border border-slate-200/80 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[11px] font-bold text-slate-700">Bollinger Bands</span>
              <div className="flex items-center space-x-1.5 text-[9px] text-slate-500">
                <span className="text-blue-500">• Upper</span>
                <span className="text-cyan-500">• Mid</span>
                <span className="text-amber-500">• Low</span>
              </div>
            </div>
            <div className="h-12 w-full relative">
              <svg viewBox={`0 0 ${bbWidth} ${bbHeight}`} className="w-full h-full overflow-visible">
                <path d={bbUpperPath} fill="none" stroke="#3b82f6" strokeWidth="1.2" />
                <path d={bbMiddlePath} fill="none" stroke="#06b6d4" strokeWidth="1" strokeDasharray="2 2" />
                <path d={bbLowerPath} fill="none" stroke="#f59e0b" strokeWidth="1.2" />
              </svg>
            </div>
          </div>

          {/* Sub 3: MACD */}
          <div className="bg-slate-50/70 p-2.5 rounded-xl border border-slate-200/80 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[11px] font-bold text-slate-700">MACD</span>
              <div className="flex items-center space-x-2 text-[9px] text-slate-500">
                <span className="text-blue-600">— MACD</span>
                <span className="text-amber-500">— Signal</span>
              </div>
            </div>
            <div className="h-12 w-full relative">
              <svg viewBox={`0 0 ${macdWidth} ${macdHeight}`} className="w-full h-full overflow-visible">
                <line x1="0" y1="28" x2={macdWidth} y2="28" stroke="#cbd5e1" strokeWidth="0.8" />
                {/* Histogram Bars */}
                {series.map((d, i) => {
                  const x = rsiXScale(i);
                  const h = Math.min(18, Math.abs(d.macd_hist || 0) * 0.12);
                  const isPos = (d.macd_hist || 0) >= 0;
                  return (
                    <rect
                      key={i}
                      x={x - 1.5}
                      y={isPos ? 28 - h : 28}
                      width="3"
                      height={Math.max(1, h)}
                      fill={isPos ? '#60a5fa' : '#f87171'}
                      opacity="0.8"
                    />
                  );
                })}
                <path d={macdPath} fill="none" stroke="#2563eb" strokeWidth="1.2" />
                <path d={macdSigPath} fill="none" stroke="#f59e0b" strokeWidth="1.2" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
