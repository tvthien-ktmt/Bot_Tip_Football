import pytest
import numpy as np
from backend.app.math.poisson import IndependentPoissonModel
from backend.app.math.dixon_coles import DixonColesModel
from backend.app.math.score_matrix import ScoreMatrixProcessor


def test_poisson_score_matrix_consistency():
    model = IndependentPoissonModel(home_adv=1.2)
    exp_h, exp_a = model.compute_expected_goals(1.3, 0.9, 1.1, 1.0)
    matrix = model.generate_score_matrix(exp_h, exp_a)

    assert matrix.shape == (11, 11)
    assert np.sum(matrix) == pytest.approx(1.0, abs=1e-5)

    probs_1x2 = ScoreMatrixProcessor.extract_1x2_probabilities(matrix)
    assert (probs_1x2["home"] + probs_1x2["draw"] + probs_1x2["away"]) == pytest.approx(1.0, abs=1e-5)

    btts = ScoreMatrixProcessor.extract_btts_probabilities(matrix)
    assert (btts["yes"] + btts["no"]) == pytest.approx(1.0, abs=1e-5)

    ou = ScoreMatrixProcessor.extract_ou_markets(matrix, lines=[2.5])
    assert (ou[2.5]["over_prob"] + ou[2.5]["under_prob"]) == pytest.approx(1.0, abs=1e-5)


def test_dixon_coles_rho_effect():
    # Negative rho (e.g. -0.1) should boost 0-0 and 1-1 compared to standard Poisson
    exp_h = 1.3
    exp_a = 1.0

    poisson_model = IndependentPoissonModel()
    p_mat = poisson_model.generate_score_matrix(exp_h, exp_a)

    dc_model = DixonColesModel(rho=-0.10)
    dc_mat = dc_model.generate_score_matrix(exp_h, exp_a)

    # 0-0 and 1-1 should be boosted by negative rho
    assert dc_mat[0, 0] > p_mat[0, 0]
    assert dc_mat[1, 1] > p_mat[1, 1]

    # Total sum must still be 1.0
    assert np.sum(dc_mat) == pytest.approx(1.0, abs=1e-5)


def test_dixon_coles_fit_2n_plus_1():
    """Verify 2n+1 parameter allocation, attack sum=0 constraint, distinct team ratings, and valid rho/tau."""
    import pandas as pd
    teams = ["TeamA", "TeamB", "TeamC", "TeamD", "TeamE", "TeamF"]
    records = []
    # Create round-robin matches (30 matches)
    for i, h in enumerate(teams):
        for j, a in enumerate(teams):
            if h != a:
                records.append({
                    "Date": "01/09/2025",
                    "home_team": h,
                    "away_team": a,
                    "FTHG": (i + 1) % 4,
                    "FTAG": (j + 2) % 3,
                })
    df = pd.DataFrame(records)

    dc = DixonColesModel()
    dc.fit(df)

    # 1. Assert all 6 teams have ratings
    assert len(dc.team_ratings) == 6

    # 2. Assert sum of log(attack) constraint equals 0
    log_attacks = [np.log(v["attack"]) for v in dc.team_ratings.values()]
    assert abs(np.sum(log_attacks)) < 1e-4

    # 3. Assert teams have distinct attack and defence ratings
    attacks = [v["attack"] for v in dc.team_ratings.values()]
    defences = [v["defence"] for v in dc.team_ratings.values()]
    assert len(set([round(a, 3) for a in attacks])) > 1
    assert len(set([round(d, 3) for d in defences])) > 1

    # 4. Assert rho in [-0.15, 0.15]
    assert -0.15 <= dc.rho <= 0.15

    # 5. Assert tau multipliers are strictly non-negative
    for x in range(3):
        for y in range(3):
            tau = dc.tau_adjustment(x, y, 1.4, 1.1)
            assert tau >= 0.0
