"""
Unit tests for Company DB Connector (Palier A.1).
"""

import json
import pytest
from pathlib import Path

from ingestion.connectors.company_db_connector import (
    generate_synthetic_companies,
    save_companies,
    load_companies,
    fetch_company_by_id,
    fetch_company_metadata,
    get_company_by_id,
    search_company_by_name,
    list_companies,
    filter_companies,
)


def test_generation_and_saving(tmp_path: Path):
    test_file = tmp_path / "companies_test.json"
    comps = generate_synthetic_companies(n=15, seed=99)
    saved_path = save_companies(comps, output_path=test_file)

    assert saved_path.exists()
    loaded = load_companies(saved_path)
    assert len(loaded) == 15
    assert loaded[0]["company_id"] == comps[0]["company_id"]


def test_search_by_id_and_name(tmp_path: Path):
    test_file = tmp_path / "test_lookup.json"
    comps = generate_synthetic_companies(n=5, seed=10)
    save_companies(comps, output_path=test_file)

    target_id = comps[0]["company_id"]
    target_name = comps[0]["name"]

    found_by_id = fetch_company_by_id(target_id, dataset_path=test_file)
    assert found_by_id is not None
    assert found_by_id["name"] == target_name

    found_by_name = search_company_by_name(target_name, dataset_path=test_file)
    assert found_by_name is not None
    assert found_by_name["company_id"] == target_id

    # Non-existent
    assert fetch_company_by_id("NON_EXISTENT_ID", dataset_path=test_file) is None
    assert search_company_by_name("Unknown Fake Company", dataset_path=test_file) is None


def test_missing_file_raises_filenotfound(tmp_path: Path):
    missing_file = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError):
        load_companies(missing_file)


def test_invalid_json_raises_value_error(tmp_path: Path):
    bad_file = tmp_path / "corrupt.json"
    bad_file.write_text('{"error": "not a list"}', encoding="utf-8")
    with pytest.raises(ValueError):
        load_companies(bad_file)


def test_list_and_filter(tmp_path: Path):
    test_file = tmp_path / "test_filter.json"
    comps = generate_synthetic_companies(n=20, seed=42)
    save_companies(comps, output_path=test_file)

    paged = list_companies(limit=5, offset=0, dataset_path=test_file)
    assert len(paged) == 5

    sector = comps[0]["sector"]
    filtered = filter_companies(sector=sector, dataset_path=test_file)
    assert all(c["sector"] == sector for c in filtered)
