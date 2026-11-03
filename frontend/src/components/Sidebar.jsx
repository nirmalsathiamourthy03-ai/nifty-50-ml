import React from 'react';
import {
  LayoutDashboard,
  LineChart,
  Brain,
  CheckSquare,
  Sparkles,
  Settings,
  TrendingUp
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'charts', label: 'Charts', icon: LineChart },
    { id: 'models', label: 'Models', icon: Brain },
    { id: 'evaluation', label: 'Evaluation', icon: CheckSquare },
    { id: 'insights', label: 'Data Insights', icon: Sparkles },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-20 md:w-24 bg-[#15233c] text-white flex flex-col items-center py-4 shrink-0 min-h-screen border-r border-[#1e3458]">
      {/* Brand Icon */}
      <div className="w-12 h-12 bg-gradient-to-tr from-[#1e40af] to-[#3b82f6] rounded-xl flex items-center justify-center mb-6 shadow-md cursor-pointer">
        <TrendingUp className="w-7 h-7 text-white" />
      </div>

      {/* Nav List */}
      <nav className="w-full flex flex-col items-center space-y-3 px-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full py-2.5 px-1 rounded-xl flex flex-col items-center justify-center text-xs transition-all duration-200 cursor-pointer ${
                isActive
                  ? 'bg-[#3b82f6] text-white font-semibold shadow-md'
                  : 'text-[#94a3b8] hover:text-white hover:bg-[#1e2e4a]'
              }`}
            >
              <Icon className="w-5 h-5 mb-1 stroke-[1.8]" />
              <span className="text-[10px] tracking-tight text-center leading-tight">
                {item.label}
              </span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
