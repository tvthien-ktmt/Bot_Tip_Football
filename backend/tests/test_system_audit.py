import httpx
import pytest

def test_full_system_audit():
    # 1. Test Backend API
    with httpx.Client(base_url="http://localhost:8000/api", timeout=15.0) as api:
        # Health check
        h = api.get("/health")
        assert h.status_code == 200, f"Health failed: {h.status_code}"

        # Leagues check
        leagues = api.get("/leagues").json()
        league_codes = [l["code"] for l in leagues]
        print("Backend Active Leagues:", league_codes)
        for expected in ["E0", "E1", "SP1", "I1", "D1"]:
            assert expected in league_codes, f"Missing league: {expected}"

        # Check each league has scheduled fixtures
        for code in ["E0", "E1", "SP1", "I1", "D1"]:
            resp = api.get(f"/fixtures?league={code}&limit=10")
            assert resp.status_code == 200, f"Fixtures failed for {code}: {resp.status_code}"
            fixtures = resp.json()
            assert len(fixtures) > 0, f"No fixtures for {code}"

        # Check Championship Birmingham
        e1_fixtures = api.get("/fixtures?league=E1&limit=50").json()
        birm_matches = [f for f in e1_fixtures if f["home_team"]["name"] == "Birmingham" or f["away_team"]["name"] == "Birmingham"]
        buli_matches = [f for f in e1_fixtures if f["home_team"]["name"] == "Bundesliga" or f["away_team"]["name"] == "Bundesliga"]
        assert len(birm_matches) > 0, "No Birmingham matches found in Championship!"
        assert len(buli_matches) == 0, "Found Bundesliga as team name in Championship!"

        # Check Match Center Analysis for sample match
        sample_m_id = e1_fixtures[0]["id"]
        analysis = api.get(f"/matches/{sample_m_id}/analysis")
        assert analysis.status_code == 200, f"Analysis failed: {analysis.status_code}"
        ana_data = analysis.json()
        assert "score_matrix" in ana_data
        assert "matrix" in ana_data["score_matrix"]
        assert "radar_comparison" in ana_data

    # 2. Test Frontend SSR & Static Pages
    with httpx.Client(base_url="http://localhost:3000", timeout=15.0) as fe:
        r_home = fe.get("/")
        assert r_home.status_code == 200, f"Frontend home failed: {r_home.status_code}"
        assert "Championship" in r_home.text, "Championship tab missing in frontend HTML"
        assert "Premier League" in r_home.text, "Premier League missing in frontend HTML"

        r_match = fe.get(f"/match/{sample_m_id}")
        assert r_match.status_code == 200, f"Frontend match page failed: {r_match.status_code}"
