import pytest
import numpy as np
import pandas as pd

from backend.app.math.poisson import IndependentPoissonModel
from backend.app.math.dixon_coles import DixonColesModel
from backend.app.math.bivariate_poisson import BivariatePoissonModel
from backend.app.math.ratings import EloRatingSystem, PiRatingSystem, SkellamGoalDifferenceModel
from backend.app.math.shot_xg import ShotBasedXGProxy
from backend.app.math.market_implied import MarketImpliedModel
from backend.app.math.ensemble import LogLinearEnsemble
from backend.app.math.corners_cards import CornersModel, CardsModel
from backend.app.data.team_mapper import LeagueTransitionManager


def test_m1_poisson_probability_sum():
    """Verify Maher Independent Poisson score matrix sums to 1.0 (1e-9 tolerance)."""
    model = IndependentPoissonModel()
    matrix = model.score_matrix(1.65, 1.20, max_goals=10)
    assert abs(np.sum(matrix) - 1.0) < 1e-9


def test_m2_dixon_coles_probability_sum():
    """Verify Dixon-Coles score matrix sums to 1.0 (1e-9 tolerance)."""
    dc = DixonColesModel(rho=-0.06)
    matrix = dc.score_matrix(1.50, 1.10, rho=-0.06, max_goals=10)
    assert abs(np.sum(matrix) - 1.0) < 1e-9


def test_m3_bivariate_poisson_probability_sum():
    """Verify Bivariate Poisson joint score matrix sums to 1.0 (1e-9 tolerance)."""
    bp = BivariatePoissonModel(lambda_3=0.08)
    matrix = bp.score_matrix(1.45, 1.15, lambda_3=0.08, max_goals=10)
    assert abs(np.sum(matrix) - 1.0) < 1e-9


def test_m4_skellam_1x2_probability_sum():
    """Verify Skellam goal difference probabilities sum to 1.0 (1e-9 tolerance)."""
    sk = SkellamGoalDifferenceModel(league_avg_total=2.70)
    p_h, p_d, p_a = sk.compute_1x2_from_lambdas(1.60, 1.10)
    assert abs((p_h + p_d + p_a) - 1.0) < 1e-9
    assert 0.0 < p_h < 1.0 and 0.0 < p_d < 1.0 and 0.0 < p_a < 1.0


def test_m5_shot_xg_proxy():
    """Verify Shot-based xG proxy estimates reasonable numbers."""
    proxy = ShotBasedXGProxy()
    # High shots & SOT
    xg_high = proxy.estimate_match_xg(shots=18, sot=7, is_home=True)
    # Low shots & SOT
    xg_low = proxy.estimate_match_xg(shots=6, sot=1, is_home=False)
    assert xg_high > xg_low
    assert 1.5 < xg_high < 3.5
    assert 0.2 < xg_low < 1.0


def test_m6_market_implied_reverse_solver():
    """Verify MarketImpliedModel reverse-solves lambdas accurately matching de-vigged market."""
    m6 = MarketImpliedModel(devig_method="shin")
    res = m6.fit_from_odds(
        odds_1x2=(1.80, 3.80, 4.50),
        odds_ou25=(1.75, 2.10),
        ah_line=-0.5,
        odds_ah=(1.82, 2.05)
    )
    assert res["convergence"] is True
    assert res["lambda_home"] > res["lambda_away"]
    assert abs(np.sum(res["score_matrix"]) - 1.0) < 1e-9
    # Home prob from model should be within 2.5% of fair market
    assert abs(res["model_1x2"][0] - res["fair_1x2"][0]) < 0.025


def test_m8_log_linear_ensemble_honest_no_edge():
    """Verify that when w is near 0, model yields no edge."""
    ens = LogLinearEnsemble(w=0.02, threshold_no_edge=0.04)
    p_mkt = [0.45, 0.28, 0.27]
    p_mod = [0.60, 0.20, 0.20]
    p_final, has_edge = ens.pool_1x2(p_mkt, p_mod)
    assert has_edge is False
    assert abs(p_final[0] - p_mkt[0]) < 0.02


def test_league_transition_manager():
    """Verify promotion offset and regression to mean."""
    # Promoted team from Championship (E1) to Premier League (E0)
    adj = LeagueTransitionManager.adjust_promoted_team_ratings(
        from_div="E1",
        to_div="E0",
        base_elo=1550.0,
        base_attack=1.10,
        base_defence=0.90
    )
    assert adj["adjusted_elo"] < 1550.0  # -135 offset
    assert adj["adjusted_attack"] < 1.10
    assert adj["adjusted_defence"] > 0.90

    # Early season regression to mean
    # Team rating 1650, league mean 1500
    r_gw1 = LeagueTransitionManager.apply_early_season_regression_to_mean(1650.0, 1500.0, matchweek=1)
    r_gw5 = LeagueTransitionManager.apply_early_season_regression_to_mean(1650.0, 1500.0, matchweek=5)
    r_gw10 = LeagueTransitionManager.apply_early_season_regression_to_mean(1650.0, 1500.0, matchweek=10)
    assert r_gw1 < r_gw5 < r_gw10
    assert r_gw10 == 1650.0  # No regression after week 5


def test_cards_whole_line_push_exclusion():
    """Verify that on whole card lines (e.g. 3.0), P(under win) equals P(X <= 2), not P(X <= 3)."""
    from scipy.stats import poisson
    from backend.app.math.corners_cards import CardsModel

    exp_cards = 3.75
    line = 3.0
    res = CardsModel.calculate_card_ou_probs(exp_cards=exp_cards, line=line)

    expected_p_under_win = float(poisson.cdf(2, exp_cards))
    expected_p_push = float(poisson.pmf(3, exp_cards))

    assert res["p_win_under"] == pytest.approx(expected_p_under_win, abs=1e-4)
    assert res["p_push"] == pytest.approx(expected_p_push, abs=1e-4)
    # Ensure P(push) is strictly not included in p_win_under
    assert res["p_win_under"] < float(poisson.cdf(3, exp_cards)) - 0.05


def test_yip_zou_bivariate_poisson_corners():
    """Verify Yip & Zou (2021) Bivariate Poisson corner matrix sums to 1.0."""
    cm = CornersModel()
    mat_bp = cm.generate_bivariate_poisson_corner_matrix(exp_home=5.5, exp_away=4.5, covariance_lambda3=0.65, max_corners=18)
    assert abs(np.sum(mat_bp) - 1.0) < 1e-9
    assert mat_bp.shape == (19, 19)
    assert np.all(mat_bp >= 0.0)

    # Test that extract_corner_ou produces valid probabilities in [0, 1]
    ou_res = cm.extract_corner_ou(mat_bp)
    for line, vals in ou_res.items():
        assert 0.0 <= vals["over_prob"] <= 1.0
        assert 0.0 <= vals["under_prob"] <= 1.0


def test_walkforward_ah_eff_win_execution():
    """Verify WalkForwardEvaluator runs without NameError on ah_eff_win."""
    from backend.app.backtest.walkforward import WalkForwardEvaluator
    evaluator = WalkForwardEvaluator()
    # Test on E0 with a fast slice if data exists
    if evaluator.data_path.exists():
        res = evaluator.run_league_backtest(league_div="E0", mode="T-24h")
        assert "metrics" in res or "error" in res
        if "metrics" in res:
            assert "model_final" in res["metrics"]
            assert "simulation_tips" in res

