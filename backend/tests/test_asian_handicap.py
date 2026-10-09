import pytest
import numpy as np
from backend.app.math.asian_handicap import (
    evaluate_ah_line_outcome,
    calculate_ah_probabilities,
    calculate_ah_ev,
    evaluate_ou_line_outcome,
    calculate_ou_probabilities
)


def test_ah_line_evaluations():
    # Line 0 (Level ball / Draw No Bet)
    assert evaluate_ah_line_outcome(goal_diff=1, line=0.0) == "WIN"
    assert evaluate_ah_line_outcome(goal_diff=0, line=0.0) == "PUSH"
    assert evaluate_ah_line_outcome(goal_diff=-1, line=0.0) == "LOSS"

    # Line -0.5
    assert evaluate_ah_line_outcome(goal_diff=1, line=-0.5) == "WIN"
    assert evaluate_ah_line_outcome(goal_diff=0, line=-0.5) == "LOSS"

    # Quarter Line -0.25 (split between 0 and -0.5)
    assert evaluate_ah_line_outcome(goal_diff=1, line=-0.25) == "WIN"
    assert evaluate_ah_line_outcome(goal_diff=0, line=-0.25) == "HALF_LOSS"  # 0 pushes on 0, loses on -0.5 -> Half Loss
    assert evaluate_ah_line_outcome(goal_diff=-1, line=-0.25) == "LOSS"

    # Quarter Line -0.75 (split between -0.5 and -1.0)
    assert evaluate_ah_line_outcome(goal_diff=2, line=-0.75) == "WIN"
    assert evaluate_ah_line_outcome(goal_diff=1, line=-0.75) == "HALF_WIN"   # 1 wins on -0.5, pushes on -1.0 -> Half Win
    assert evaluate_ah_line_outcome(goal_diff=0, line=-0.75) == "LOSS"

    # Positive Quarter Line +0.25 (split between 0 and +0.5)
    assert evaluate_ah_line_outcome(goal_diff=0, line=0.25) == "HALF_WIN"   # 0 pushes on 0, wins on +0.5 -> Half Win
    assert evaluate_ah_line_outcome(goal_diff=1, line=0.25) == "WIN"
    assert evaluate_ah_line_outcome(goal_diff=-1, line=0.25) == "LOSS"

    # Positive Quarter Line +0.75 (split between +0.5 and +1.0)
    assert evaluate_ah_line_outcome(goal_diff=-1, line=0.75) == "HALF_LOSS" # -1 loses on +0.5, pushes on +1.0 -> Half Loss
    assert evaluate_ah_line_outcome(goal_diff=0, line=0.75) == "WIN"


def test_ou_quarter_line_evaluations():
    # Over 2.25 (split between Over 2.0 and Over 2.5)
    assert evaluate_ou_line_outcome(total_goals=3, line=2.25, is_over=True) == "WIN"
    assert evaluate_ou_line_outcome(total_goals=2, line=2.25, is_over=True) == "HALF_LOSS" # Pushes on 2, loses on 2.5
    assert evaluate_ou_line_outcome(total_goals=1, line=2.25, is_over=True) == "LOSS"

    # Under 2.25 (split between Under 2.0 and Under 2.5)
    assert evaluate_ou_line_outcome(total_goals=2, line=2.25, is_over=False) == "HALF_WIN"  # Pushes on 2, wins on 2.5
    assert evaluate_ou_line_outcome(total_goals=1, line=2.25, is_over=False) == "WIN"
    assert evaluate_ou_line_outcome(total_goals=3, line=2.25, is_over=False) == "LOSS"

    # Over 2.75 (split between Over 2.5 and Over 3.0)
    assert evaluate_ou_line_outcome(total_goals=3, line=2.75, is_over=True) == "HALF_WIN"  # Wins on 2.5, pushes on 3.0
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
