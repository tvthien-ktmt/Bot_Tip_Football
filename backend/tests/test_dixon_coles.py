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
