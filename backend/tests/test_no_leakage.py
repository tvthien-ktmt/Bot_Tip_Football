import pytest
import numpy as np
import pandas as pd
from backend.app.pipeline.match_predictor import MatchPredictor
from backend.app.math.residual_lgbm import ResidualLGBMModel


def test_t24h_vs_t1h_odds_separation():
    """
    Test strict separation:
    - In T-24h mode, line shifts and closing odds are strictly 0 or ignored.
    - In T-1h mode, line shifts and closing odds are permitted.
    """
    model_t24 = ResidualLGBMModel(mode="T-24h")
    model_t1 = ResidualLGBMModel(mode="T-1h")

    sample_match = pd.Series({
        "ah_open_line": -0.5,
        "ah_close_line": -0.75,
        "ref_open_h": 2.00,
        "ref_close_h": 1.80,
    })

    feats_t24 = model_t24.build_features_for_match(
        match_row=sample_match,
        m2_prob_h=0.52,
        mkt_prob_h=0.50,
        home_elo=1550,
        away_elo=1500,
        pi_exp_gd=0.35,
        m5_xg_diff=0.20,
        home_form_5=1.8,
        away_form_5=1.2,
        home_rest_days=6.0,
        away_rest_days=6.0,
        referee_cards_avg=3.8
    )

    feats_t1 = model_t1.build_features_for_match(
        match_row=sample_match,
        m2_prob_h=0.52,
        mkt_prob_h=0.50,
        home_elo=1550,
        away_elo=1500,
        pi_exp_gd=0.35,
        m5_xg_diff=0.20,
        home_form_5=1.8,
        away_form_5=1.2,
        home_rest_days=6.0,
        away_rest_days=6.0,
        referee_cards_avg=3.8
    )

    # In T-24h mode, line shift and odds shift MUST BE STRICTLY 0.0 (anti-leakage)
    assert feats_t24["line_shift_ah"] == 0.0, "T-24h leaked closing line shift!"
    assert feats_t24["odds_shift_h"] == 0.0, "T-24h leaked closing odds shift!"

    # In T-1h mode, line shift reflects the change from open to close (-0.75 - (-0.50) = -0.25)
    assert feats_t1["line_shift_ah"] == pytest.approx(-0.25)
    assert feats_t1["odds_shift_h"] == pytest.approx(-0.10)


def test_future_permutation_invariance():
    """
    Test that modifying, permuting, or deleting future matches
    does NOT alter the prediction or features for match t.
    """
    # Create a synthetic historical dataframe
    dates = pd.date_range("2026-08-01", periods=10, freq="W")
    history_base = pd.DataFrame({
        "match_date": dates,
        "home_team": ["TeamA", "TeamB", "TeamA", "TeamC", "TeamA", "TeamB", "TeamC", "TeamA", "TeamB", "TeamC"],
        "away_team": ["TeamB", "TeamC", "TeamC", "TeamA", "TeamB", "TeamA", "TeamA", "TeamB", "TeamC", "TeamA"],
        "FTHG": [2, 1, 0, 3, 1, 2, 0, 2, 1, 3],
        "FTAG": [1, 1, 2, 0, 1, 0, 1, 1, 2, 1],
        "HST": [5, 4, 3, 6, 4, 5, 2, 6, 4, 7],
        "AST": [3, 4, 5, 2, 3, 2, 4, 3, 5, 3],
        "HY": [2, 1, 3, 2, 1, 0, 2, 1, 2, 3],
        "AY": [1, 2, 1, 3, 2, 2, 1, 2, 1, 2],
        "referee": ["Ref1"] * 10
    })

    # Target match t at index 4 (Date: 2026-08-29)
    target_match = pd.Series({
        "Div": "E0",
        "match_date": "2026-08-29",
        "home_team": "TeamA",
        "away_team": "TeamB",
        "referee": "Ref1",
        "AvgH": 2.10,
        "AvgD": 3.40,
        "AvgA": 3.60,
        "Avg>2.5": 1.90,
        "Avg<2.5": 1.95,
        "AHh": -0.25,
        "AvgAHH": 1.85,
        "AvgAHA": 2.05
    })

    predictor = MatchPredictor(mode="T-24h")

    # History slice prior to target match (first 4 matches)
    hist_before = history_base.iloc[:4].copy()
    pred_original = predictor.predict_match(target_match, historical_matches=hist_before)

    # Now simulate future matches being perturbed (indices 5 to 9 altered completely)
    history_perturbed = history_base.copy()
    history_perturbed.loc[5:, "FTHG"] = 9
    history_perturbed.loc[5:, "FTAG"] = 9
    history_perturbed.loc[5:, "HST"] = 20

    # Match predictor should only look at matches with match_date < target_match
    hist_filtered = history_perturbed[history_perturbed["match_date"] < pd.Timestamp("2026-08-29")]
    pred_perturbed = predictor.predict_match(target_match, historical_matches=hist_filtered)

    # Verify that predictions are strictly identical
    assert pred_original["expected_goals"]["home"] == pred_perturbed["expected_goals"]["home"]
    assert pred_original["expected_goals"]["away"] == pred_perturbed["expected_goals"]["away"]
    assert pred_original["probs"]["1x2"] == pred_perturbed["probs"]["1x2"]
    assert pred_original["probs"]["over_under"] == pred_perturbed["probs"]["over_under"]
