import React from "react";
import { Link } from "react-router-dom";

export default function RankingList({ targets = [] }) {
  const getBadgeClass = (rec) => {
    if (rec === "Cible prioritaire") return "bg-emerald-100 text-emerald-800 border-emerald-300";
    if (rec === "À surveiller") return "bg-amber-100 text-amber-800 border-amber-300";
    return "bg-gray-100 text-gray-700 border-gray-300";
  };

  const getScoreColor = (score) => {
    if (score >= 80) return "text-emerald-600 font-bold";
    if (score >= 60) return "text-amber-600 font-semibold";
    return "text-gray-600";
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 text-left text-sm">
        <thead className="bg-gray-50 text-xs font-semibold uppercase text-gray-500">
          <tr>
            <th className="px-4 py-3">Rang</th>
            <th className="px-4 py-3">Entreprise</th>
            <th className="px-4 py-3">Secteur</th>
            <th className="px-4 py-3">Pays</th>
            <th className="px-4 py-3">Croissance</th>
            <th className="px-4 py-3">Score M&A</th>
            <th className="px-4 py-3">Recommandation</th>
            <th className="px-4 py-3 text-right">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {targets.map((item, index) => (
            <tr key={item.company_id || index} className="hover:bg-gray-50 transition-colors">
              <td className="px-4 py-3 font-semibold text-gray-700">#{item.ranking || index + 1}</td>
              <td className="px-4 py-3 font-medium text-gray-900">
                <Link to={`/companies/${item.company_id}`} className="hover:text-blue-600">
                  {item.name}
                </Link>
              </td>
              <td className="px-4 py-3 text-gray-600">{item.sector}</td>
              <td className="px-4 py-3 text-gray-600">{item.country}</td>
              <td className="px-4 py-3 text-gray-900 font-medium">
                {item.growth ? `+${item.growth.toFixed(1)}%` : "N/A"}
              </td>
              <td className={`px-4 py-3 ${getScoreColor(item.m_and_a_score)}`}>
                {item.m_and_a_score ? item.m_and_a_score.toFixed(1) : "N/A"}/100
              </td>
              <td className="px-4 py-3">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getBadgeClass(item.recommendation)}`}>
                  {item.recommendation || "N/A"}
                </span>
              </td>
              <td className="px-4 py-3 text-right">
                <Link
                  to={`/companies/${item.company_id}`}
                  className="text-xs font-semibold text-blue-600 hover:text-blue-800"
                >
                  Voir fiche &rarr;
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
