"""
DealScout - Synthetic Company Generator
Palier A.1

Génère un dataset synthétique réaliste d'entreprises
pour alimenter la pipeline Data Engineering de DealScout.

Pipeline future :

Synthetic Generator
        ↓
Company Connector
        ↓
Kafka
        ↓
Bronze
        ↓
Spark
        ↓
Silver
        ↓
dbt
        ↓
Gold
        ↓
M&A Scoring
        ↓
XGBoost + SHAP
"""

from __future__ import annotations

import json
import random
from datetime import date
from pathlib import Path
from typing import Any

from faker import Faker


# ============================================================
# CONFIGURATION
# ============================================================

CURRENT_YEAR = date.today().year

DEFAULT_COMPANY_COUNT = 1000
DEFAULT_SEED = 42

fake = Faker()


# ============================================================
# SECTEURS
# ============================================================

SECTORS = {
    "FinTech": {
        "growth": (8, 45),
        "margin": (8, 28),
        "innovation": (65, 98),
        "market": (60, 95),
        "revenue_multiplier": 1.25,
    },
    "SaaS": {
        "growth": (10, 50),
        "margin": (5, 30),
        "innovation": (60, 95),
        "market": (65, 95),
        "revenue_multiplier": 1.10,
    },
    "HealthTech": {
        "growth": (5, 35),
        "margin": (4, 25),
        "innovation": (70, 99),
        "market": (60, 92),
        "revenue_multiplier": 1.05,
    },
    "E-commerce": {
        "growth": (5, 40),
        "margin": (2, 18),
        "innovation": (50, 90),
        "market": (65, 95),
        "revenue_multiplier": 1.30,
    },
    "Cybersecurity": {
        "growth": (12, 48),
        "margin": (8, 30),
        "innovation": (75, 99),
        "market": (70, 98),
        "revenue_multiplier": 1.15,
    },
    "AI": {
        "growth": (15, 60),
        "margin": (-5, 25),
        "innovation": (85, 100),
        "market": (75, 99),
        "revenue_multiplier": 0.95,
    },
    "Logistics": {
        "growth": (4, 30),
        "margin": (3, 18),
        "innovation": (45, 85),
        "market": (55, 90),
        "revenue_multiplier": 1.40,
    },
    "EdTech": {
        "growth": (8, 45),
        "margin": (3, 25),
        "innovation": (65, 95),
        "market": (60, 90),
        "revenue_multiplier": 0.85,
    },
    "ClimateTech": {
        "growth": (10, 40),
        "margin": (-2, 22),
        "innovation": (75, 98),
        "market": (65, 95),
        "revenue_multiplier": 0.90,
    },
}


# ============================================================
# LOCALISATIONS
# ============================================================

LOCATIONS = [
    ("Morocco", "Casablanca"),
    ("Morocco", "Rabat"),
    ("Morocco", "Marrakesh"),
    ("France", "Paris"),
    ("France", "Lyon"),
    ("Germany", "Berlin"),
    ("Germany", "Munich"),
    ("United Kingdom", "London"),
    ("Spain", "Madrid"),
    ("Spain", "Barcelona"),
    ("United States", "New York"),
    ("United States", "San Francisco"),
    ("United States", "Boston"),
    ("Canada", "Toronto"),
    ("United Arab Emirates", "Dubai"),
    ("Netherlands", "Amsterdam"),
    ("Singapore", "Singapore"),
    ("Australia", "Sydney"),
]


# ============================================================
# HELPERS
# ============================================================

def clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """
    Limite une valeur entre minimum et maximum.
    """
    return max(minimum, min(value, maximum))


def round_value(
    value: float,
    digits: int = 2,
) -> float:
    """
    Arrondit une valeur numérique.
    """
    return round(value, digits)


# ============================================================
# COMPANY GENERATOR
# ============================================================

def generate_company(
    company_id: int,
) -> dict[str, Any]:
    """
    Génère une entreprise synthétique.

    Les différentes variables sont volontairement corrélées
    pour produire des données réalistes.

    Args:
        company_id: identifiant numérique.

    Returns:
        Dictionnaire représentant une entreprise.
    """

    # --------------------------------------------------------
    # Secteur
    # --------------------------------------------------------

    sector = random.choice(list(SECTORS.keys()))
    sector_config = SECTORS[sector]

    # --------------------------------------------------------
    # Localisation
    # --------------------------------------------------------

    country, city = random.choice(LOCATIONS)

    # --------------------------------------------------------
    # Âge de l'entreprise
    # --------------------------------------------------------

    founded_year = random.randint(
        CURRENT_YEAR - 20,
        CURRENT_YEAR - 2,
    )

    age_years = CURRENT_YEAR - founded_year

    # --------------------------------------------------------
    # Nom
    # --------------------------------------------------------

    company_name = fake.unique.company()

    # --------------------------------------------------------
    # Nombre d'employés
    # --------------------------------------------------------

    if age_years <= 3:
        employees = random.randint(5, 80)

    elif age_years <= 7:
        employees = random.randint(40, 500)

    elif age_years <= 12:
        employees = random.randint(150, 2500)

    else:
        employees = random.randint(500, 10000)

    # --------------------------------------------------------
    # Croissance
    # --------------------------------------------------------

    growth_min, growth_max = sector_config["growth"]

    revenue_growth = random.uniform(
        growth_min,
        growth_max,
    )

    # Les jeunes entreprises ont généralement
    # une croissance plus élevée.

    if age_years <= 4:
        revenue_growth += random.uniform(3, 12)

    elif age_years >= 15:
        revenue_growth -= random.uniform(0, 8)

    revenue_growth = clamp(
        revenue_growth,
        -10,
        70,
    )

    # --------------------------------------------------------
    # Revenue
    # --------------------------------------------------------

    revenue_per_employee = random.uniform(
        70_000,
        300_000,
    )

    revenue = (
        employees
        * revenue_per_employee
        * sector_config["revenue_multiplier"]
    )

    revenue = max(
        revenue,
        100_000,
    )

    # --------------------------------------------------------
    # Profitabilité
    # --------------------------------------------------------

    margin_min, margin_max = sector_config["margin"]

    profit_margin = random.uniform(
        margin_min,
        margin_max,
    )

    # Les entreprises très jeunes
    # sont généralement moins rentables.

    if age_years <= 3:
        profit_margin -= random.uniform(2, 8)

    profit_margin = clamp(
        profit_margin,
        -15,
        35,
    )

    # EBITDA légèrement supérieur ou inférieur
    # à la marge nette.

    ebitda_margin = profit_margin + random.uniform(
        0,
        8,
    )

    ebitda_margin = clamp(
        ebitda_margin,
        -10,
        40,
    )

    # --------------------------------------------------------
    # Funding
    # --------------------------------------------------------

    if age_years <= 2:
        funding_rounds = random.randint(0, 2)

    elif age_years <= 5:
        funding_rounds = random.randint(1, 4)

    elif age_years <= 10:
        funding_rounds = random.randint(2, 7)

    else:
        funding_rounds = random.randint(3, 10)

    base_funding = (
        employees
        * random.uniform(
            10_000,
            80_000,
        )
    )

    funding_total = (
        base_funding
        * max(1, funding_rounds / 3)
    )

    # --------------------------------------------------------
    # Limite financement selon âge
    # --------------------------------------------------------

    if age_years <= 2:
        funding_total = min(
            funding_total,
            5_000_000,
        )

    elif age_years <= 5:
        funding_total = min(
            funding_total,
            30_000_000,
        )

    elif age_years <= 10:
        funding_total = min(
            funding_total,
            150_000_000,
        )

    else:
        funding_total = min(
            funding_total,
            500_000_000,
        )

    # --------------------------------------------------------
    # Dette
    # --------------------------------------------------------

    debt_ratio = random.uniform(
        0.05,
        0.45,
    )

    debt = revenue * debt_ratio

    # --------------------------------------------------------
    # Cash
    # --------------------------------------------------------

    cash = revenue * random.uniform(
        0.05,
        0.35,
    )

    # --------------------------------------------------------
    # Market Cap
    # --------------------------------------------------------

    valuation_multiple = random.uniform(
        1.5,
        8.0,
    )

    # AI, SaaS et Cybersecurity
    # ont généralement des multiples plus élevés.

    if sector in {
        "AI",
        "SaaS",
        "Cybersecurity",
    }:
        valuation_multiple += random.uniform(
            1,
            4,
        )

    market_cap = (
        revenue
        * valuation_multiple
    )

    # --------------------------------------------------------
    # Présence internationale
    # --------------------------------------------------------

    if age_years <= 3:
        international_presence = random.uniform(
            5,
            40,
        )

    elif age_years <= 8:
        international_presence = random.uniform(
            20,
            70,
        )

    else:
        international_presence = random.uniform(
            40,
            100,
        )

    # --------------------------------------------------------
    # Innovation
    # --------------------------------------------------------

    innovation_min, innovation_max = (
        sector_config["innovation"]
    )

    innovation_score = random.uniform(
        innovation_min,
        innovation_max,
    )

    # --------------------------------------------------------
    # Market Opportunity
    # --------------------------------------------------------

    market_min, market_max = (
        sector_config["market"]
    )

    market_score = random.uniform(
        market_min,
        market_max,
    )

    # Une croissance importante augmente
    # légèrement l'opportunité du marché.

    market_score += (
        revenue_growth * 0.10
    )

    market_score = clamp(
        market_score,
        0,
        100,
    )

    # --------------------------------------------------------
    # Résultat
    # --------------------------------------------------------

    return {
        "company_id": f"CMP-{company_id:06d}",
        "name": company_name,
        "sector": sector,
        "country": country,
        "city": city,
        "founded_year": founded_year,
        "age_years": age_years,
        "employees": employees,
        "revenue": round_value(revenue),
        "revenue_growth": round_value(revenue_growth),
        "profit_margin": round_value(profit_margin),
        "ebitda_margin": round_value(ebitda_margin),
        "debt": round_value(debt),
        "cash": round_value(cash),
        "market_cap": round_value(market_cap),
        "funding_total": round_value(funding_total),
        "funding_rounds": funding_rounds,
        "international_presence": round_value(
            international_presence
        ),
        "innovation_score": round_value(
            innovation_score
        ),
        "market_score": round_value(
            market_score
        ),
    }


# ============================================================
# MULTIPLE COMPANIES
# ============================================================

def generate_companies(
    n: int = DEFAULT_COMPANY_COUNT,
    seed: int = DEFAULT_SEED,
) -> list[dict[str, Any]]:
    """
    Génère plusieurs entreprises.

    Args:
        n: nombre d'entreprises.
        seed: seed pour la reproductibilité.

    Returns:
        Liste d'entreprises.
    """

    if n <= 0:
        raise ValueError(
            "n doit être supérieur à 0."
        )

    random.seed(seed)
    Faker.seed(seed)

    # Reset du générateur unique Faker
    fake.unique.clear()

    companies = []

    for company_id in range(1, n + 1):

        company = generate_company(
            company_id=company_id,
        )

        companies.append(company)

    return companies


# ============================================================
# SAVE JSON
# ============================================================

def save_companies_to_json(
    companies: list[dict[str, Any]],
    output_path: str | Path,
) -> None:
    """
    Sauvegarde les entreprises au format JSON.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            companies,
            file,
            indent=2,
            ensure_ascii=False,
        )


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """
    Point d'entrée du générateur.
    """

    output_path = Path(
        "data/samples/companies.json"
    )

    companies = generate_companies(
        n=1000,
        seed=42,
    )

    save_companies_to_json(
        companies,
        output_path,
    )

    print("=" * 60)
    print("DealScout - Synthetic Company Generator")
    print("=" * 60)
    print(f"Companies generated : {len(companies)}")
    print(f"Output              : {output_path}")
    print(f"Seed                : 42")
    print("=" * 60)


if __name__ == "__main__":
    main()