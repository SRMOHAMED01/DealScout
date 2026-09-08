"""
Integration and functional tests for FastAPI backend (Palier F).
"""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_companies():
    response = client.get("/companies?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) == 10
    assert "company_id" in data["items"][0]


def test_get_company_by_id():
    list_resp = client.get("/companies?limit=1")
    first_id = list_resp.json()["items"][0]["company_id"]

    response = client.get(f"/companies/{first_id}")
    assert response.status_code == 200
    comp = response.json()
    assert comp["company_id"] == first_id

    # 404 test
    not_found = client.get("/companies/NON_EXISTENT_ID")
    assert not_found.status_code == 404


def test_get_company_score():
    list_resp = client.get("/companies?limit=1")
    first_id = list_resp.json()["items"][0]["company_id"]

    response = client.get(f"/companies/{first_id}/score")
    assert response.status_code == 200
    score_data = response.json()
    assert "m_and_a_score" in score_data
    assert "components" in score_data
    assert "strengths" in score_data
    assert "risks" in score_data
    assert 0.0 <= score_data["m_and_a_score"] <= 100.0


def test_search_targets():
    response = client.get("/search?min_score=30&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    for item in data["items"]:
        assert item["m_and_a_score"] >= 30


def test_market_analysis():
    response = client.get("/market-analysis")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "sector" in data[0]
    assert "average_growth" in data[0]
