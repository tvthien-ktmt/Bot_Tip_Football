import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "KèoLab" in data["service"]


def test_api_leagues():
    response = client.get("/api/leagues")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    codes = [l["code"] for l in data]
    assert "E0" in codes
    assert "SP1" in codes


def test_api_fixtures():
    response = client.get("/api/fixtures")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    first = data[0]
    assert "home_team" in first
    assert "away_team" in first
    assert "league" in first


def test_api_match_analysis():
    fixtures_res = client.get("/api/fixtures")
    assert fixtures_res.status_code == 200
    fixtures = fixtures_res.json()
    match_id = fixtures[0]["id"]

    analysis_res = client.get(f"/api/matches/{match_id}/analysis")
    assert analysis_res.status_code == 200
    data = analysis_res.json()

    assert "score_matrix" in data
    assert "radar_comparison" in data
    assert "model_breakdown" in data
    assert "home_form" in data
    assert "away_form" in data
    assert "odds_comparison" in data
    assert len(data["score_matrix"]["matrix"]) == 7


def test_api_performance():
    res = client.get("/api/performance")
    assert res.status_code == 200
    data = res.json()
    assert data["total_tips"] > 0
    assert "simulated_roi_pct" in data
    assert "brier_score" in data
    assert "by_confidence" in data


def test_api_odds_history():
    fixtures_res = client.get("/api/fixtures")
    fixtures = fixtures_res.json()
    match_id = fixtures[0]["id"]

    res = client.get(f"/api/matches/{match_id}/odds-history")
    assert res.status_code == 200
    history = res.json()
    assert isinstance(history, list)


def test_api_tips():
    res = client.get("/api/tips")
    assert res.status_code == 200
    tips = res.json()
    assert isinstance(tips, list)
    for tip in tips:
        assert tip["ev"] >= 0.03  # Must satisfy EV threshold
        assert tip["edge"] >= 0.025 # Must satisfy edge threshold


def test_api_admin_injury():
    res = client.post("/api/admin/injury", json={
        "team_name": "Arsenal",
        "player_name": "Bukayo Saka",
        "status": "Chấn thương gân kheo",
        "impact": "-4.5% xG"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "Bukayo Saka" in data["message"]

