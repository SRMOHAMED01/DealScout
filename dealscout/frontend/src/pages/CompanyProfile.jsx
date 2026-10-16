import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import ShapChart from "../components/ShapChart";
import {
  getCompanyProfile,
  getCompanyScore,
  getCompanyMLScore,
} from "../api/companies";

export default function CompanyProfile() {
  const { id } = useParams();
  const [profile, setProfile] = useState(null);
  const [scoreData, setScoreData] = useState(null);
  const [mlScore, setMLScore] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [prof, sc, ml] = await Promise.all([
          getCompanyProfile(id),
          getCompanyScore(id),
          getCompanyMLScore(id).catch(() => null),
        ]);
        setProfile(prof);
        setScoreData(sc);
        setMLScore(ml);
      } catch (err) {
        setError(`Impossible de charger la fiche entreprise pour l'identifiant ${id}`);
      } finally {
        setLoading(false);
      }
    }
    if (id) loadData();
  }, [id]);

  if (loading) {
    return <div className="p-8 text-center text-gray-500">Chargement de la fiche entreprise...</div>;
  }

  if (error || !profile) {
    return (
      <div className="p-8 max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
          {error || "Entreprise introuvable."}
        </div>
        <Link to="/" className="mt-4 inline-block text-sm text-blue-600 font-semibold">
          &larr; Retour au Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <Link to="/" className="text-xs text-blue-600 font-medium hover:underline">
            &larr; Retour au Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 mt-1">{profile.name}</h1>
          <p className="text-sm text-gray-500">
            {profile.sector} &bull; {profile.city}, {profile.country} &bull; ID: {profile.company_id}
          </p>
        </div>
        <div className="text-right">
          <span className="text-xs uppercase tracking-wider text-gray-400 font-bold block">Score M&amp;A</span>
          <span className="text-3xl font-extrabold text-blue-600">
            {scoreData?.m_and_a_score ? scoreData.m_and_a_score.toFixed(1) : "N/A"}/100
          </span>
          {mlScore && (
            <div className="mt-2">
              <span className="text-xs uppercase tracking-wider text-gray-400 font-bold block">Probabilité Acquisition (ML)</span>
              <span className="text-2xl font-bold text-purple-600">
                {mlScore.acquisition_probability.toFixed(1)}%
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <p className="text-xs text-gray-500">Chiffre d'Affaires</p>
          <p className="text-xl font-bold text-gray-900 mt-1">
            ${(profile.revenue / 1_000_000).toFixed(1)}M
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <p className="text-xs text-gray-500">Croissance Annuelle</p>
          <p className="text-xl font-bold text-emerald-600 mt-1">
            +{profile.growth?.toFixed(1) || profile.revenue_growth?.toFixed(1)}%
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <p className="text-xs text-gray-500">Effectif</p>
          <p className="text-xl font-bold text-gray-900 mt-1">{profile.employees} employés</p>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <p className="text-xs text-gray-500">Recommandation</p>
          <p className="text-lg font-bold text-gray-900 mt-1">{scoreData?.recommendation || "N/A"}</p>
        </div>
      </div>

      {/* Grid: Chart & Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ShapChart components={scoreData?.components} />

        <div className="bg-white p-6 rounded-xl border border-gray-200 space-y-4">
          <h3 className="text-base font-semibold text-gray-900">Analyse Métier & Signaux</h3>

          <div>
            <p className="text-xs font-semibold uppercase text-emerald-700">Points Forts Détectés</p>
            <ul className="mt-2 space-y-1">
              {scoreData?.strengths?.map((s, idx) => (
                <li key={idx} className="text-sm text-gray-700 flex items-center">
                  <span className="text-emerald-500 mr-2">&#10003;</span> {s}
                </li>
              ))}
              {(!scoreData?.strengths || scoreData.strengths.length === 0) && (
                <li className="text-xs text-gray-400">Aucun point fort critique répertorié.</li>
              )}
            </ul>
          </div>

          <div className="pt-2">
            <p className="text-xs font-semibold uppercase text-rose-700">Risques & Points de Vigilance</p>
            <ul className="mt-2 space-y-1">
              {scoreData?.risks?.map((r, idx) => (
                <li key={idx} className="text-sm text-gray-700 flex items-center">
                  <span className="text-rose-500 mr-2">&#9888;</span> {r}
                </li>
              ))}
              {(!scoreData?.risks || scoreData.risks.length === 0) && (
                <li className="text-xs text-gray-400">Aucun risque majeur identifié.</li>
              )}
            </ul>
          </div>

          <div className="pt-3 border-t border-gray-100">
            <p className="text-xs text-gray-500">Dernière actualité médiatique</p>
            <p className="text-sm font-medium text-gray-800 mt-0.5">
              "{profile.latest_headline || "Pas d'actualité récente"}"
            </p>
            <p className="text-xs text-gray-400 mt-1">
              Sentiment marché : {profile.news_sentiment > 0 ? "Favorable" : "Neutre/Réservé"} ({profile.news_sentiment})
            </p>
          </div>
        </div>

        {mlScore && mlScore.shap_explanation && (
          <div className="bg-white p-6 rounded-xl border border-gray-200 space-y-4">
            <h3 className="text-base font-semibold text-gray-900">Explication ML (SHAP)</h3>
            <p className="text-xs text-gray-500">
              Facteurs qui font varier la probabilité d'acquisition pour cette entreprise.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-xs font-semibold uppercase text-emerald-700 mb-2">Facteurs Positifs</p>
                <ul className="space-y-1">
                  {mlScore.shap_explanation.positive_drivers?.map((d, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-center justify-between">
                      <span>{d.feature} ({d.value})</span>
                      <span className="text-emerald-600 font-medium">+{d.impact}</span>
                    </li>
                  ))}
                  {(mlScore.shap_explanation.positive_drivers?.length || 0) === 0 && (
                    <li className="text-xs text-gray-400">Aucun facteur positif détecté.</li>
                  )}
                </ul>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase text-rose-700 mb-2">Facteurs Négatifs</p>
                <ul className="space-y-1">
                  {mlScore.shap_explanation.negative_drivers?.map((d, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-center justify-between">
                      <span>{d.feature} ({d.value})</span>
                      <span className="text-rose-600 font-medium">{d.impact}</span>
                    </li>
                  ))}
                  {(mlScore.shap_explanation.negative_drivers?.length || 0) === 0 && (
                    <li className="text-xs text-gray-400">Aucun facteur négatif détecté.</li>
                  )}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
