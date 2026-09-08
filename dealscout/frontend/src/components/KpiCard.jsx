import React from "react";

export default function KpiCard({ title, value, subtitle, trend, color = "blue" }) {
  const colorClasses = {
    blue: "text-blue-600 bg-blue-50 border-blue-200",
    green: "text-emerald-600 bg-emerald-50 border-emerald-200",
    purple: "text-purple-600 bg-purple-50 border-purple-200",
    amber: "text-amber-600 bg-amber-50 border-amber-200",
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
      <p className="text-sm font-medium text-gray-500 uppercase tracking-wider">{title}</p>
      <div className="mt-2 flex items-baseline justify-between">
        <p className="text-3xl font-extrabold text-gray-900">{value}</p>
        {trend && (
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${colorClasses[color] || colorClasses.blue}`}>
            {trend}
          </span>
        )}
      </div>
      {subtitle && <p className="mt-1 text-xs text-gray-400">{subtitle}</p>}
    </div>
  );
}
