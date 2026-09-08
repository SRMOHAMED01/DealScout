import React, { useEffect, useState } from "react";
import KpiCard from "../components/KpiCard";
import RankingList from "../components/RankingList";
import { getCompanies, getMarketAnalysis } from "../api/companies";

export default function Dashboard() {
  const [companies, setCompanies] = useState([]);
  const [market, setMarket] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setLoading(true);
        const [compData, marketData] = await Promise.all([
          getCompanies({ limit: 25 }),
          getMarketAnalysis(),
        ]);
        setCompanies(compData.items || []);
        setMarket(marketData || []);
      } catch (err) {
        setError("Erreur lors du chargement des données de la plateforme.");
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  const totalAnalyzed = companies.length;
  const priorityTargets = companies.filter((c) => c.recommendation === "Cible prioritaire").length;
  const avgScore = totalAnalyzed
    ? (companies.reduce((acc, c) => acc + (c.m_and_a_score || 0), 0) / totalAnalyzed).toFixed(1)
    : 0;

  return (
    <div className="space-y-8 p-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard M&A Intelligence</h1>
        <p className="text-sm text-gray-500">
          Surveillance et détection d'opportunités d'investissement et d'acquisition.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KpiCard
          title="Entreprises Analysées"
          value={totalAnalyzed}
          subtitle="Pipeline Bronze & Silver"
          color="blue"
        />
        <KpiCard
          title="Cibles Prioritaires"
          value={priorityTargets}
          subtitle="Score M&A >= 85"
          trend={`${priorityTargets > 0 ? "+" + priorityTargets : 0} opportunités`}
          color="green"
        />
        <KpiCard
          title="Score M&A Moyen"
          value={`${avgScore}/100`}
          subtitle="Moyenne du portefeuille"
          color="purple"
        />
        <KpiCard
          title="Secteurs Couverts"
          value={market.length || 6}
          subtitle="FinTech, SaaS, AI, Health..."
          color="amber"
        />
      </div>

      {/* Top Opportunities Ranking */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900">Top Opportunités Détectées</h2>
          <span className="text-xs text-gray-400">Classées par score d'opportunité</span>
        </div>
        {loading ? (
          <p className="text-sm text-gray-500 py-8 text-center">Chargement des opportunités...</p>
        ) : (
          <RankingList targets={companies} />
        )}
      </div>
    </div>
  );
}
