import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

export default function ShapChart({ components = {} }) {
  const data = [
    { name: "Croissance (30%)", value: components.growth || 0, color: "#3B82F6" },
    { name: "Chiffre d'Affaires (20%)", value: components.revenue || 0, color: "#10B981" },
    { name: "Rentabilité (20%)", value: components.profitability || 0, color: "#8B5CF6" },
    { name: "Opportunité Marché (15%)", value: components.market || 0, color: "#F59E0B" },
    { name: "Innovation (10%)", value: components.innovation || 0, color: "#EC4899" },
    { name: "Présence Int. (5%)", value: components.international || 0, color: "#6366F1" },
  ];

  return (
    <div className="bg-white p-6 rounded-xl border border-gray-200">
      <h3 className="text-base font-semibold text-gray-900 mb-2">
        Décomposition et Poids du Score M&A
      </h3>
      <p className="text-xs text-gray-500 mb-4">
        Contribution normalisée et pondérée de chaque composante métier au score final.
      </p>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
            <XAxis type="number" domain={[0, 30]} />
            <YAxis type="category" dataKey="name" width={140} tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(val) => [`${val.toFixed(2)} pts`, "Contribution"]}
              contentStyle={{ borderRadius: "8px", border: "1px solid #E5E7EB" }}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
