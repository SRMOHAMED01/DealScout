"""
Unit tests for Company Generator (Palier A.1).
"""

from ingestion.generators.company_generator import generate_companies, generate_company


def test_generate_companies_count():
    companies = generate_companies(n=25, seed=42)
    assert len(companies) == 25


def test_generate_companies_unique_ids():
    companies = generate_companies(n=100, seed=42)
    ids = [c["company_id"] for c in companies]
    assert len(ids) == len(set(ids)), "Company IDs must all be unique"


def test_generate_companies_mandatory_fields():
    company = generate_company(company_id=1)
    mandatory_fields = [
        "company_id", "name", "sector", "country", "city",
        "founded_year", "age_years", "employees", "revenue",
        "revenue_growth", "profit_margin", "ebitda_margin", "debt",
        "cash", "market_cap", "funding_total", "funding_rounds",
        "international_presence", "innovation_score", "market_score"
    ]
    for field in mandatory_fields:
        assert field in company, f"Missing field {field} in company dictionary"


def test_generate_companies_numeric_coherence():
    companies = generate_companies(n=30, seed=42)
    for c in companies:
        assert c["employees"] > 0
        assert c["revenue"] >= 0
        assert c["debt"] >= 0
        assert c["cash"] >= 0
        assert c["market_cap"] >= 0
        assert 0.0 <= c["international_presence"] <= 100.0
        assert 0.0 <= c["innovation_score"] <= 100.0
        assert 0.0 <= c["market_score"] <= 100.0


def test_generate_companies_seed_reproducibility():
    run_1 = generate_companies(n=10, seed=123)
    run_2 = generate_companies(n=10, seed=123)
    assert run_1 == run_2, "Same seed must produce identical company records"
