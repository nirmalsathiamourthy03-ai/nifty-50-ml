import React, { useState } from 'react';

export default function ModelComparisonCard({ comparisonData }) {
  const [activeSubTab, setActiveSubTab] = useState('metrics');
  const [hoveredBar, setHoveredBar] = useState(null);

  const data = comparisonData || [
    { model: 'Logistic Regression', Accuracy: 47.75, Precision: 50.26, Recall: 67.90, F1_Score: 57.76, ROC_AUC: 49.19 },
    { model: 'Random Forest', Accuracy: 52.25, Precision: 53.64, Recall: 68.13, F1_Score: 60.02, ROC_AUC: 52.30 },
    { model: 'Gradient Boosting', Accuracy: 51.52, Precision: 52.98, Recall: 69.75, F1_Score: 60.22, ROC_AUC: 51.31 },
    { model: 'XGBoost', Accuracy: 50.67, Precision: 52.58, Recall: 63.51, F1_Score: 57.53, ROC_AUC: 51.57 },
    { model: 'LightGBM', Accuracy: 51.52, Precision: 53.07, Recall: 67.90, F1_Score: 59.57, ROC_AUC: 50.77 },
  ];

  const metricsConfig = [
    { key: 'Accuracy', label: 'Accuracy', color: '#2563eb' },
    { key: 'Precision', label: 'Precision', color: '#60a5fa' },
    { key: 'Recall', label: 'Recall', color: '#fed7aa' },
    { key: 'F1_Score', label: 'F1-Score', color: '#f472b6' },
    { key: 'ROC_AUC', label: 'ROC-AUC', color: '#1e3a8a' },
  ];

  const svgWidth = 460;
  const svgHeight = 270;
  const padding = { top: 30, right: 15, bottom: 45, left: 35 };

  const innerW = svgWidth - padding.left - padding.right;
  const innerH = svgHeight - padding.top - padding.bottom;

  const yTicks = [0, 20, 40, 60, 80];
  const maxY = 80;

  const groupWidth = innerW / data.length;
  const barWidth = 6.5;
  const barGap = 1.8;
  const totalClusterWidth = 5 * barWidth + 4 * barGap;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden flex flex-col justify-between">
      {/* Dark Navy Header Bar */}
      <div className="bg-[#1e3a8a] text-white px-5 py-3 flex items-center justify-between">
        <h2 className="text-sm font-bold tracking-wide">Model Comparison</h2>
      </div>

      <div className="p-4 flex flex-col flex-1">
        {/* Navigation Tabs */}
        <div className="flex items-center space-x-6 text-xs font-semibold border-b border-slate-100 pb-2 mb-2">
          {[
            { id: 'metrics', label: 'Performance Metrics' },
            { id: 'cm', label: 'Confusion Matrix' },
            { id: 'fi', label: 'Feature Importance' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id)}
              className={`pb-1.5 transition-colors cursor-pointer ${
                activeSubTab === tab.id
                  ? 'text-[#2563eb] border-b-2 border-[#2563eb] font-bold'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center justify-end gap-x-3 gap-y-1 text-[10px] font-semibold text-slate-600 mb-2">
          {metricsConfig.map((m) => (
            <span key={m.key} className="flex items-center space-x-1">
              <span className="w-2.5 h-2.5 rounded-xs" style={{ backgroundColor: m.color }}></span>
              <span>{m.label}</span>
            </span>
          ))}
        </div>

        {/* Grouped Bar Chart */}
        <div className="relative w-full h-[230px] select-none">
          <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="w-full h-full overflow-visible">
            {/* Grid & Y Axis */}
            {yTicks.map((tick) => {
              const y = padding.top + innerH - (tick / maxY) * innerH;
              return (
                <g key={tick}>
                  <line x1={padding.left} y1={y} x2={svgWidth - padding.right} y2={y} stroke="#f1f5f9" strokeDasharray="3 3" />
                  <text x={padding.left - 6} y={y + 3.5} fill="#94a3b8" fontSize="9.5" textAnchor="end" fontFamily="sans-serif">
                    {tick}%
                  </text>
                </g>
              );
            })}

            {/* Clusters */}
            {data.map((item, groupIdx) => {
              const groupCenterX = padding.left + groupIdx * groupWidth + groupWidth / 2;
              const startX = groupCenterX - totalClusterWidth / 2;

              return (
                <g key={item.model}>
                  {/* Bars */}
                  {metricsConfig.map((m, mIdx) => {
                    const x = startX + mIdx * (barWidth + barGap);
                    const val = Math.min(maxY, item[m.key] || 0);
                    const barH = (val / maxY) * innerH;
                    const y = padding.top + innerH - barH;

                    return (
                      <rect
                        key={m.key}
                        x={x}
                        y={y}
                        width={barWidth}
                        height={Math.max(0, barH)}
                        fill={m.color}
                        rx="1"
                        onMouseEnter={() => setHoveredBar({ model: item.model, metric: m.label, value: item[m.key] })}
                        onMouseLeave={() => setHoveredBar(null)}
                        className="cursor-pointer transition-opacity hover:opacity-80"
                      />
                    );
                  })}

                  {/* X Axis Model Label */}
                  <text
                    x={groupCenterX}
                    y={svgHeight - 14}
                    fill="#475569"
                    fontSize="9.5"
                    fontWeight="500"
                    textAnchor="middle"
                    fontFamily="sans-serif"
                  >
                    {item.model}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Hover Tooltip */}
          {hoveredBar && (
            <div className="absolute top-1 right-2 bg-slate-900/90 text-white text-[11px] px-2.5 py-1.5 rounded-lg shadow-lg pointer-events-none backdrop-blur-xs flex items-center space-x-2 z-10">
              <span className="font-bold text-blue-300">{hoveredBar.model}</span>
              <span>{hoveredBar.metric}: <strong>{hoveredBar.value.toFixed(1)}%</strong></span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
