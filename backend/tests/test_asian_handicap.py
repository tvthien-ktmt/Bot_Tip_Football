import pytest
import numpy as np
from backend.app.math.asian_handicap import (
    evaluate_ah_line_outcome,
    calculate_ah_probabilities,
    calculate_ah_ev,
    evaluate_ou_line_outcome,
    calculate_ou_probabilities
)
from backend.app.math.dixon_coles import DixonColesModel


def test_ah_12_hand_tested_cases():
    """
    Test explicitly at least 12 Asian Handicap settlement cases covering:
    Level, Half, Quarter, and Full lines from both favorite and underdog perspectives.
    """
    # Case 1: Line 0 (Level / DNB), Home wins -> WIN
    assert evaluate_ah_line_outcome(goal_diff=1, line=0.0) == "WIN"

    # Case 2: Line 0 (Level / DNB), Draw -> PUSH (Hoàn tiền)
    assert evaluate_ah_line_outcome(goal_diff=0, line=0.0) == "PUSH"

    # Case 3: Line 0 (Level / DNB), Away wins -> LOSS
    assert evaluate_ah_line_outcome(goal_diff=-1, line=0.0) == "LOSS"

    # Case 4: Line -0.25, Draw -> HALF_LOSS (Hòa = thua nửa)
    assert evaluate_ah_line_outcome(goal_diff=0, line=-0.25) == "HALF_LOSS"

    # Case 5: Line -0.25, Home wins by 1 -> WIN (Thắng 1 bàn = thắng đủ)
    assert evaluate_ah_line_outcome(goal_diff=1, line=-0.25) == "WIN"

    # Case 6: Line -0.25, Away wins -> LOSS
    assert evaluate_ah_line_outcome(goal_diff=-1, line=-0.25) == "LOSS"

    # Case 7: Line -0.75, Home wins by 1 -> HALF_WIN (Thắng đúng 1 bàn = thắng nửa)
    assert evaluate_ah_line_outcome(goal_diff=1, line=-0.75) == "HALF_WIN"

    # Case 8: Line -0.75, Home wins by 2+ -> WIN
    assert evaluate_ah_line_outcome(goal_diff=2, line=-0.75) == "WIN"

    # Case 9: Line -0.75, Draw -> LOSS
    assert evaluate_ah_line_outcome(goal_diff=0, line=-0.75) == "LOSS"

    # Case 10: Line +0.25, Draw -> HALF_WIN (Được chấp 0.25 hòa = thắng nửa)
    assert evaluate_ah_line_outcome(goal_diff=0, line=0.25) == "HALF_WIN"

    # Case 11: Line -1.0, Home wins by 1 -> PUSH (Chấp 1 quả thắng 1 quả = hòa tiền)
    assert evaluate_ah_line_outcome(goal_diff=1, line=-1.0) == "PUSH"

    # Case 12: Line -1.25, Home wins by 1 -> HALF_LOSS (Chấp 1.25 thắng 1 quả = thua nửa)
    assert evaluate_ah_line_outcome(goal_diff=1, line=-1.25) == "HALF_LOSS"


def test_ah_probabilities_sum_to_one():
    """Verify sum of AH outcome probabilities equals 1.0 within 1e-9 tolerance across lines."""
    dc = DixonColesModel()
    matrix = dc.score_matrix(lambda_home=1.65, lambda_away=1.15, rho=-0.08, max_goals=10)

    # Check across various lines from -2.5 to +2.5 in quarter steps
    test_lines = [-2.0, -1.75, -1.5, -1.25, -1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
    for line in test_lines:
        res = calculate_ah_probabilities(matrix, line)
        prob_sum = res["p_win"] + res["p_half_win"] + res["p_push"] + res["p_half_loss"] + res["p_loss"]
        assert abs(prob_sum - 1.0) < 1e-9, f"AH Prob sum for line {line} deviated: {prob_sum}"


def test_ou_probabilities_sum_to_one():
    """Verify sum of O/U probabilities equals 1.0 within 1e-9 tolerance across quarter and half lines."""
    dc = DixonColesModel()
    matrix = dc.score_matrix(lambda_home=1.50, lambda_away=1.20, rho=-0.05, max_goals=10)

    test_lines = [1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5]
    for line in test_lines:
        for is_over in [True, False]:
            res = calculate_ou_probabilities(matrix, line, is_over=is_over)
            prob_sum = res["p_win"] + res["p_half_win"] + res["p_push"] + res["p_half_loss"] + res["p_loss"]
            assert abs(prob_sum - 1.0) < 1e-9, f"O/U Prob sum for line {line} is_over={is_over} deviated: {prob_sum}"


def test_ou_quarter_line_evaluations():
    # Over 2.25 (split between Over 2.0 and Over 2.5)
    assert evaluate_ou_line_outcome(total_goals=3, line=2.25, is_over=True) == "WIN"
    assert evaluate_ou_line_outcome(total_goals=2, line=2.25, is_over=True) == "HALF_LOSS"  # Pushes on 2, loses on 2.5
    assert evaluate_ou_line_outcome(total_goals=1, line=2.25, is_over=True) == "LOSS"

    # Under 2.25 (split between Under 2.0 and Under 2.5)
    assert evaluate_ou_line_outcome(total_goals=2, line=2.25, is_over=False) == "HALF_WIN"   # Pushes on 2, wins on 2.5
    assert evaluate_ou_line_outcome(total_goals=1, line=2.25, is_over=False) == "WIN"
    assert evaluate_ou_line_outcome(total_goals=3, line=2.25, is_over=False) == "LOSS"

    # Over 2.75 (split between Over 2.5 and Over 3.0)
    assert evaluate_ou_line_outcome(total_goals=3, line=2.75, is_over=True) == "HALF_WIN"   # Wins on 2.5, pushes on 3.0
    assert evaluate_ou_line_outcome(total_goals=4, line=2.75, is_over=True) == "WIN"
    assert evaluate_ou_line_outcome(total_goals=2, line=2.75, is_over=True) == "LOSS"


def test_ah_ev_calculation():
    # If 100% win at odds 2.0, EV = 1.0 (100% ROI)
    probs_win = {"p_win": 1.0, "p_half_win": 0.0, "p_push": 0.0, "p_half_loss": 0.0, "p_loss": 0.0}
    assert calculate_ah_ev(probs_win, 2.0) == pytest.approx(1.0)

    # If 100% push, EV = 0.0
    probs_push = {"p_win": 0.0, "p_half_win": 0.0, "p_push": 1.0, "p_half_loss": 0.0, "p_loss": 0.0}
    assert calculate_ah_ev(probs_push, 2.0) == pytest.approx(0.0)

    # If 100% half-win at odds 2.0: profit is (2.0 - 1.0)/2 = 0.5 -> EV = +0.5
    probs_hw = {"p_win": 0.0, "p_half_win": 1.0, "p_push": 0.0, "p_half_loss": 0.0, "p_loss": 0.0}
    assert calculate_ah_ev(probs_hw, 2.0) == pytest.approx(0.5)

    # If 100% half-loss: loss is -0.5 -> EV = -0.5
    probs_hl = {"p_win": 0.0, "p_half_win": 0.0, "p_push": 0.0, "p_half_loss": 1.0, "p_loss": 0.0}
    assert calculate_ah_ev(probs_hl, 2.0) == pytest.approx(-0.5)
