"""
scoring_service.py — Data loading, search, and score aggregation for FastAPI (Palier F).

Charge les données depuis l'entrepôt Gold (Postgres) via SQLAlchemy, avec
une bascule automatique sur le stockage Parquet local / génération de secours
si Postgres n'est pas disponible (CI, dev hors Docker).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any
import pandas as pd
from sqlalchemy import select

from app.core.database import SessionLocal, engine, Base
from app.core.config import settings
from app.models.company import Company
from app.models.investment_target import InvestmentTarget
from ingestion.config import config
from ingestion.connectors.company_db_connector import generate_synthetic_companies
from scoring_engine.rules_scoring import compute_scores

logger = logging.getLogger(__name__)


class CompanyScoringService:
    """
    Central service caching and serving Company 360 data, M&A scores, and search filtering.
    """

    def __init__(self) -> None:
        self._df: pd.DataFrame = pd.DataFrame()
        self.refresh_data()

    def _load_from_postgres(self) -> pd.DataFrame | None:
        """Charge company_360 depuis Postgres via SQLAlchemy (si dispo)."""
        try:
            Base.metadata.create_all(bind=engine)
            with SessionLocal() as session:
                stmt = select(Company)
                rows = session.execute(stmt).scalars().all()
            if not rows:
                logger.warning("Postgres company_360 vide, bascule sur le fallback")
                return None
            df = pd.DataFrame([{c.name: getattr(r, c.name) for c in Company.__table__.columns} for r in rows])
            logger.info("Chargé %d enregistrements depuis Postgres company_360", len(df))
            return df
        except Exception as exc:  # pragma: no cover - Postgres indisponible en dev/CI
            logger.warning("Postgres indisponible (%s), bascule sur Parquet/local", exc)
            return None

    def refresh_data(self) -> None:
        """Charge les données depuis Postgres, puis Parquet, puis génère un fallback."""
        df = self._load_from_postgres()
        if df is not None and not df.empty:
            self._df = compute_scores(df)
            return

        gold_path = Path("data") / "gold" / "investment_targets" / "investment_targets.parquet"
        if gold_path.exists():
            try:
                self._df = pd.read_parquet(gold_path)
                logger.info("Chargé %d enregistrements depuis Gold Parquet", len(self._df))
                return
            except Exception as e:
                logger.warning("Échec lecture Gold Parquet (%s), génération de secours", e)

        # Fallback: génère depuis le generator + calcule les scores
        raw = generate_synthetic_companies(n=100, seed=42)
        base_df = pd.DataFrame(raw)
        base_df["growth"] = base_df["revenue_growth"]
        base_df["funding"] = base_df["funding_total"]
        base_df["financial_health"] = 65.0
        base_df["news_sentiment"] = 0.25
        base_df["mentions_count"] = 3
        base_df["latest_headline"] = "Strategic expansion announced"

        self._df = compute_scores(base_df)
        logger.info("Généré et scoré %d entreprises de secours en mémoire", len(self._df))

    def persist_to_postgres(self) -> int:
        """Écrit les cibles scorées dans Postgres investment_targets (idempotent)."""
        if self._df.empty:
            return 0
        try:
            Base.metadata.create_all(bind=engine)
            with SessionLocal() as session:
                session.query(InvestmentTarget).delete()
                for _, row in self._df.iterrows():
                    exp = row.get("explanation")
                    if isinstance(exp, str):
                        try:
                            exp_json = exp
                        except Exception:
                            exp_json = "{}"
                    elif isinstance(exp, dict):
                        import json as _json
                        exp_json = _json.dumps(exp, ensure_ascii=False)
                    else:
                        exp_json = "{}"

                    components = exp.get("components", {}) if isinstance(exp, dict) else {}
                    strengths = exp.get("strengths", []) if isinstance(exp, dict) else []
                    risks = exp.get("risks", []) if isinstance(exp, dict) else []

                    session.merge(
                        InvestmentTarget(
                            company_id=str(row["company_id"]),
                            name=str(row["name"]),
                            sector=str(row.get("sector", "")),
                            country=str(row.get("country", "")),
                            revenue=float(row.get("revenue", 0.0)),
                            growth=float(row.get("growth", 0.0)),
                            profit_margin=float(row.get("profit_margin", 0.0)),
                            financial_health=float(row.get("financial_health", 50.0)),
                            market_score=float(row.get("market_score", 50.0)),
                            innovation_score=float(row.get("innovation_score", 50.0)),
                            international_presence=float(row.get("international_presence", 50.0)),
                            news_sentiment=float(row.get("news_sentiment", 0.0)),
                            m_and_a_score=float(row.get("m_and_a_score", 0.0)),
                            ranking=int(row.get("ranking", 0)),
                            risk_level=str(row.get("risk_level", "Medium")),
                            recommendation=str(row.get("recommendation", "Faible priorite")),
                            acquisition_probability=round(float(row.get("m_and_a_score", 50.0)) * 0.95, 1),
                            components_json=json.dumps(components, ensure_ascii=False),
                            strengths_json=json.dumps(strengths, ensure_ascii=False),
                            risks_json=json.dumps(risks, ensure_ascii=False),
                        )
                    )
                session.commit()
                logger.info("Persisté %d cibles dans Postgres investment_targets", len(self._df))
                return len(self._df)
        except Exception as exc:  # pragma: no cover - Postgres indisponible en dev/CI
            logger.warning("Impossible de persister dans Postgres (%s)", exc)
            return 0

    def get_all(self, limit: int = 50, offset: int = 0) -> tuple[list[dict[str, Any]], int]:
        total = len(self._df)
        subset = self._df.iloc[offset : offset + limit]
        return subset.to_dict(orient="records"), total

    def get_by_id(self, company_id: str) -> dict[str, Any] | None:
        matches = self._df[self._df["company_id"] == company_id]
        if matches.empty:
            return None
        return matches.iloc[0].to_dict()

    def get_score_by_id(self, company_id: str) -> dict[str, Any] | None:
        rec = self.get_by_id(company_id)
        if not rec:
            return None

        exp = rec.get("explanation")
        if isinstance(exp, str):
            try:
                exp = json.loads(exp)
            except Exception:
                exp = {}
        elif not isinstance(exp, dict):
            exp = {}

        components = exp.get("components", {
            "growth": 0.0, "revenue": 0.0, "profitability": 0.0,
            "market": 0.0, "innovation": 0.0, "international": 0.0
        })

        return {
            "company_id": rec["company_id"],
            "name": rec["name"],
            "m_and_a_score": float(rec.get("m_and_a_score", 0.0)),
            "ranking": int(rec.get("ranking", 1)),
            "recommendation": str(rec.get("recommendation", "À surveiller")),
            "risk_level": str(rec.get("risk_level", "Medium")),
            "acquisition_probability": round(float(rec.get("m_and_a_score", 50.0)) * 0.95, 1),
            "components": components,
            "strengths": exp.get("strengths", []),
            "risks": exp.get("risks", []),
        }

    def search(
        self,
        sector: str | None = None,
        country: str | None = None,
        min_growth: float | None = None,
        min_revenue: float | None = None,
        min_score: float | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        filtered = self._df.copy()

        if sector:
            filtered = filtered[filtered["sector"].str.lower() == sector.lower()]
        if country:
            filtered = filtered[filtered["country"].str.lower() == country.lower()]
        if min_growth is not None:
            filtered = filtered[filtered["growth"] >= min_growth]
        if min_revenue is not None:
            filtered = filtered[filtered["revenue"] >= min_revenue]
        if min_score is not None:
            filtered = filtered[filtered["m_and_a_score"] >= min_score]

        filtered = filtered.sort_values(by="m_and_a_score", ascending=False)
        total = len(filtered)
        paged = filtered.iloc[offset : offset + limit]
        return paged.to_dict(orient="records"), total

    def market_analysis(self) -> list[dict[str, Any]]:
        if self._df.empty:
            return []

        grouped = self._df.groupby("sector").agg(
            number_of_companies=("company_id", "count"),
            average_growth=("growth", "mean"),
            average_financial_health=("financial_health", "mean"),
            investment_volume=("funding", "sum"),
            average_sentiment=("news_sentiment", "mean"),
        ).reset_index()

        grouped["average_growth"] = grouped["average_growth"].round(2)
        grouped["average_financial_health"] = grouped["average_financial_health"].round(2)
        grouped["investment_volume"] = grouped["investment_volume"].round(2)
        grouped["average_sentiment"] = grouped["average_sentiment"].round(3)

        return grouped.sort_values(by="average_growth", ascending=False).to_dict(orient="records")


service = CompanyScoringService()
