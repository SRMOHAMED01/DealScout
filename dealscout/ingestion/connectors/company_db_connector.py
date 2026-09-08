"""
DealScout - Company Database Connector
Palier A.1

Responsabilité :
    Fournir les métadonnées des entreprises à la pipeline d'ingestion DealScout.
    Supporte la génération, le chargement, la recherche par nom et par ID,
    ainsi que le filtrage et le listing.

Source principale :
    Dataset synthétique généré localement via ingestion.generators.company_generator.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from ingestion.config import config
from ingestion.generators.company_generator import (
    generate_companies,
)

logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_DATASET_PATH = config.local_samples_dir / "companies.json"


# ============================================================
# GENERATE SYNTHETIC COMPANIES
# ============================================================

def generate_synthetic_companies(
    n: int = 1000,
    seed: int = 42,
) -> list[dict[str, Any]]:
    """
    Génère un dataset synthétique d'entreprises.

    Cette fonction délègue la génération au module
    company_generator.py.

    Args:
        n: nombre d'entreprises.
        seed: seed de reproductibilité.

    Returns:
        Liste de dictionnaires représentant les entreprises.
    """

    return generate_companies(
        n=n,
        seed=seed,
    )


# ============================================================
# SAVE DATASET
# ============================================================

def save_companies(
    companies: list[dict[str, Any]],
    output_path: str | Path = DEFAULT_DATASET_PATH,
) -> Path:
    """
    Sauvegarde les entreprises dans un fichier JSON.

    Args:
        companies: liste d'entreprises.
        output_path: chemin du fichier de sortie.

    Returns:
        Path du fichier créé.
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

    return output_path


# ============================================================
# LOAD DATASET
# ============================================================

def load_companies(
    dataset_path: str | Path = DEFAULT_DATASET_PATH,
) -> list[dict[str, Any]]:
    """
    Charge le dataset des entreprises depuis JSON.

    Args:
        dataset_path: chemin du dataset.

    Returns:
        Liste d'entreprises.

    Raises:
        FileNotFoundError:
            Si le dataset n'existe pas.
        ValueError:
            Si le JSON n'est pas une liste.
    """

    dataset_path = Path(dataset_path)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset introuvable : {dataset_path}"
        )

    with dataset_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        companies = json.load(file)

    if not isinstance(companies, list):
        raise ValueError(
            "Le dataset doit contenir une liste d'entreprises."
        )

    return companies


# ============================================================
# FETCH COMPANY METADATA
# ============================================================

def fetch_company_metadata(
    company_name: str,
    dataset_path: str | Path = DEFAULT_DATASET_PATH,
) -> dict[str, Any] | None:
    """
    Recherche une entreprise par son nom.

    Pour le moment, la recherche est effectuée dans
    le dataset synthétique local.

    Une API externe pourra être ajoutée plus tard.

    Args:
        company_name: nom de l'entreprise.
        dataset_path: dataset JSON.

    Returns:
        Métadonnées de l'entreprise si trouvée,
        sinon None.
    """

    if not company_name.strip():
        raise ValueError(
            "company_name ne peut pas être vide."
        )

    companies = load_companies(
        dataset_path
    )

    search_name = company_name.strip().lower()

    for company in companies:

        current_name = str(
            company.get("name", "")
        ).strip().lower()

        if current_name == search_name:
            return company

    return None


# ============================================================
# FETCH BY COMPANY ID
# ============================================================

def fetch_company_by_id(
    company_id: str,
    dataset_path: str | Path = DEFAULT_DATASET_PATH,
) -> dict[str, Any] | None:
    """
    Recherche une entreprise par company_id.

    Exemple :

        CMP-000001
    """

    if not company_id.strip():
        raise ValueError(
            "company_id ne peut pas être vide."
        )

    companies = load_companies(
        dataset_path
    )

    company_id = company_id.strip()

    for company in companies:

        if company.get("company_id") == company_id:
            return company

    return None


# ============================================================
# API ALIASES & QUERY HELPERS
# ============================================================

def get_company_by_id(
    company_id: str,
    dataset_path: str | Path = DEFAULT_DATASET_PATH,
) -> dict[str, Any] | None:
    """Alias for fetch_company_by_id."""
    return fetch_company_by_id(company_id=company_id, dataset_path=dataset_path)


def search_company_by_name(
    company_name: str,
    dataset_path: str | Path = DEFAULT_DATASET_PATH,
) -> dict[str, Any] | None:
    """Alias for fetch_company_metadata."""
    return fetch_company_metadata(company_name=company_name, dataset_path=dataset_path)


def list_companies(
    limit: int = 100,
    offset: int = 0,
    dataset_path: str | Path = DEFAULT_DATASET_PATH,
) -> list[dict[str, Any]]:
    """
    Returns a paginated list of companies.
    """
    companies = load_companies(dataset_path)
    return companies[offset : offset + limit]


def filter_companies(
    sector: str | None = None,
    country: str | None = None,
    min_growth: float | None = None,
    min_employees: int | None = None,
    dataset_path: str | Path = DEFAULT_DATASET_PATH,
) -> list[dict[str, Any]]:
    """
    Filters companies by sector, country, growth threshold, or minimum employees.
    """
    companies = load_companies(dataset_path)
    results = []

    for c in companies:
        if sector and c.get("sector", "").lower() != sector.lower():
            continue
        if country and c.get("country", "").lower() != country.lower():
            continue
        if min_growth is not None and c.get("revenue_growth", 0.0) < min_growth:
            continue
        if min_employees is not None and c.get("employees", 0) < min_employees:
            continue
        results.append(c)

    return results


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """
    Test manuel du connector.
    """

    print("=" * 60)
    print("DealScout - Company DB Connector")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Génération
    # --------------------------------------------------------

    companies = generate_synthetic_companies(
        n=1000,
        seed=42,
    )

    print(
        f"Generated companies : {len(companies)}"
    )

    # --------------------------------------------------------
    # 2. Sauvegarde
    # --------------------------------------------------------

    output_path = save_companies(
        companies
    )

    print(
        f"Dataset saved       : {output_path}"
    )

    # --------------------------------------------------------
    # 3. Chargement
    # --------------------------------------------------------

    loaded_companies = load_companies()

    print(
        f"Dataset loaded      : {len(loaded_companies)}"
    )

    # --------------------------------------------------------
    # 4. Recherche par ID
    # --------------------------------------------------------

    company = fetch_company_by_id(
        "CMP-000001"
    )

    print("\nCompany by ID:")
    print(company)

    # --------------------------------------------------------
    # 5. Recherche par nom
    # --------------------------------------------------------

    if company:

        company_name = company["name"]

        result = fetch_company_metadata(
            company_name
        )

        print("\nCompany by name:")
        print(result)

    print("=" * 60)


if __name__ == "__main__":
    main()