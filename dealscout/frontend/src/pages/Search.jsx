import React, { useState } from "react";
import RankingList from "../components/RankingList";
import { searchCompanies } from "../api/companies";

export default function Search() {
  const [filters, setFilters] = useState({
    sector: "",
    country: "",
    min_growth: "",
    min_revenue: "",
    min_score: "",
  });
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSearched(true);
    try {
      const cleanParams = {};
      if (filters.sector) cleanParams.sector = filters.sector;
      if (filters.country) cleanParams.country = filters.country;
      if (filters.min_growth) cleanParams.min_growth = parseFloat(filters.min_growth);
      if (filters.min_revenue) cleanParams.min_revenue = parseFloat(filters.min_revenue);
      if (filters.min_score) cleanParams.min_score = parseFloat(filters.min_score);

      const res = await searchCompanies(cleanParams);
      setResults(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      console.error("Search error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Recherche Multi-Critères de Cibles</h1>
        <p className="text-sm text-gray-500">
          Filtrage avancé selon les critères de thèse d'investissement (secteur, géographie, croissance, taille).
        </p>
      </div>

      {/* Filter Form */}
      <form onSubmit={handleSearch} className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase">Secteur</label>
            <input
              type="text"
              name="sector"
              value={filters.sector}
              onChange={handleInputChange}
              placeholder="ex: FinTech, SaaS, AI"
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase">Pays / Géographie</label>
            <input
              type="text"
              name="country"
              value={filters.country}
              onChange={handleInputChange}
              placeholder="ex: Morocco, United States, France"
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase">Croissance Min. (%)</label>
            <input
              type="number"
              name="min_growth"
              value={filters.min_growth}
              onChange={handleInputChange}
              placeholder="ex: 20"
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase">Chiffre d'Affaires Min. ($)</label>
            <input
              type="number"
              name="min_revenue"
              value={filters.min_revenue}
              onChange={handleInputChange}
              placeholder="ex: 5000000"
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase">Score M&A Min. (0-100)</label>
            <input
              type="number"
              name="min_score"
              value={filters.min_score}
              onChange={handleInputChange}
              placeholder="ex: 60"
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md text-sm transition-colors shadow-sm"
            >
              {loading ? "Recherche en cours..." : "Rechercher les cibles"}
            </button>
          </div>
        </div>
      </form>

      {/* Results Section */}
      {searched && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-gray-900">
              Résultats de recherche ({total} entreprise{total > 1 ? "s" : ""})
            </h2>
            <span className="text-xs text-gray-400">Triées par score M&A décroissant</span>
          </div>
          {results.length > 0 ? (
            <RankingList targets={results} />
          ) : (
            <p className="text-sm text-gray-500 py-8 text-center">
              Aucune entreprise ne correspond aux critères sélectionnés.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
