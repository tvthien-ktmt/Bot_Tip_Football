from typing import Dict, Tuple
import numpy as np


def evaluate_ah_line_outcome(goal_diff: int, line: float) -> str:
    """
    Evaluate the outcome of an Asian Handicap bet for the home team given goal_diff = home - away
    and line (e.g. -0.25, -0.5, -0.75, 0, +0.25, +0.5).
    
    Outcomes returned:
    - 'WIN': Full win (payout = stake * odds)
    - 'HALF_WIN': Half win (payout = stake * 0.5 * odds + stake * 0.5)
    - 'PUSH': Stake refunded (payout = stake)
    - 'HALF_LOSS': Half loss (payout = stake * 0.5)
    - 'LOSS': Full loss (payout = 0)
    """
    diff_plus_line = goal_diff + line

    # Check for quarter lines
    frac = abs(line - int(line))
    if np.isclose(frac, 0.25) or np.isclose(frac, 0.75):
        # Quarter line is split between (line - 0.25) and (line + 0.25)
        l1 = line - 0.25
        l2 = line + 0.25
        out1 = evaluate_ah_line_outcome(goal_diff, l1)
        out2 = evaluate_ah_line_outcome(goal_diff, l2)

        if out1 == "WIN" and out2 == "WIN":
            return "WIN"
        elif out1 == "LOSS" and out2 == "LOSS":
            return "LOSS"
        elif (out1 == "WIN" and out2 == "PUSH") or (out1 == "PUSH" and out2 == "WIN"):
            return "HALF_WIN"
        elif (out1 == "LOSS" and out2 == "PUSH") or (out1 == "PUSH" and out2 == "LOSS"):
            return "HALF_LOSS"
        elif out1 == "PUSH" and out2 == "PUSH":
            return "PUSH"
        else:
            return "PUSH"

    # Full and half lines
    if diff_plus_line > 0.001:
        return "WIN"
    elif np.isclose(diff_plus_line, 0.0):
        return "PUSH"
    else:
        return "LOSS"


def calculate_ah_probabilities(
    score_matrix: np.ndarray,
    line: float
) -> Dict[str, float]:
    """
    Calculate exact probabilities for an Asian Handicap market from a score matrix P(home=i, away=j).
    Returns:
    {
        'p_win': float,
        'p_half_win': float,
        'p_push': float,
        'p_half_loss': float,
        'p_loss': float,
        'effective_win_prob': float  # p_win + 0.5*p_half_win
    }
    """
    p_win = 0.0
    p_half_win = 0.0
    p_push = 0.0
    p_half_loss = 0.0
    p_loss = 0.0

    max_goals = score_matrix.shape[0]
    for h in range(max_goals):
        for a in range(max_goals):
            prob = score_matrix[h, a]
            if prob <= 0:
                continue
            goal_diff = h - a
            outcome = evaluate_ah_line_outcome(goal_diff, line)
            if outcome == "WIN":
                p_win += prob
            elif outcome == "HALF_WIN":
                p_half_win += prob
            elif outcome == "PUSH":
                p_push += prob
            elif outcome == "HALF_LOSS":
                p_half_loss += prob
            elif outcome == "LOSS":
                p_loss += prob

    total = p_win + p_half_win + p_push + p_half_loss + p_loss
    if total > 0:
        p_win /= total
        p_half_win /= total
        p_push /= total
        p_half_loss /= total
        p_loss /= total

    # Effective win probability for comparison with de-vigged market odds.
    # Push = refund (neutral), so it is NOT included in effective probability.
    # Ref: Pinnacle / academic convention: eff = P(W) + 0.5 * P(HW)
    eff_prob = p_win + 0.5 * p_half_win

    return {
        "p_win": float(p_win),
        "p_half_win": float(p_half_win),
        "p_push": float(p_push),
        "p_half_loss": float(p_half_loss),
        "p_loss": float(p_loss),
        "effective_win_prob": float(eff_prob)
    }


def calculate_ah_ev(
    probs: Dict[str, float],
    decimal_odds: float
) -> float:
    """
    Compute precise Expected Value (EV) per unit stake:
    EV = P(W)*(O-1) + P(HW)*(O-1)/2 + P(Push)*0 - P(HL)*0.5 - P(L)*1.0
    """
    ev = (
        probs["p_win"] * (decimal_odds - 1.0)
        + probs["p_half_win"] * (decimal_odds - 1.0) * 0.5
        + probs["p_push"] * 0.0
        - probs["p_half_loss"] * 0.5
        - probs["p_loss"] * 1.0
    )
    return float(ev)


def evaluate_ou_line_outcome(total_goals: int, line: float, is_over: bool = True) -> str:
    """
    Evaluate outcome of Over/Under bet for total_goals and line (including quarter lines: 2.25, 2.75).
    """
    frac = abs(line - int(line))
    if np.isclose(frac, 0.25) or np.isclose(frac, 0.75):
        l1 = line - 0.25
        l2 = line + 0.25
        out1 = evaluate_ou_line_outcome(total_goals, l1, is_over)
        out2 = evaluate_ou_line_outcome(total_goals, l2, is_over)
        if out1 == "WIN" and out2 == "WIN":
            return "WIN"
        elif out1 == "LOSS" and out2 == "LOSS":
            return "LOSS"
        elif (out1 == "WIN" and out2 == "PUSH") or (out1 == "PUSH" and out2 == "WIN"):
            return "HALF_WIN"
        elif (out1 == "LOSS" and out2 == "PUSH") or (out1 == "PUSH" and out2 == "LOSS"):
            return "HALF_LOSS"
        else:
            return "PUSH"

    diff = total_goals - line
    if is_over:
        if diff > 0.001:
            return "WIN"
        elif np.isclose(diff, 0.0):
            return "PUSH"
        else:
            return "LOSS"
    else:  # Under
        if diff < -0.001:
            return "WIN"
        elif np.isclose(diff, 0.0):
            return "PUSH"
        else:
            return "LOSS"


def calculate_ou_probabilities(
    score_matrix: np.ndarray,
    line: float,
    is_over: bool = True
) -> Dict[str, float]:
    """Calculate exact probabilities for Over/Under goals line from score matrix."""
    p_win = 0.0
    p_half_win = 0.0
    p_push = 0.0
    p_half_loss = 0.0
    p_loss = 0.0

    max_goals = score_matrix.shape[0]
    for h in range(max_goals):
        for a in range(max_goals):
            prob = score_matrix[h, a]
            if prob <= 0:
                continue
            total_goals = h + a
            outcome = evaluate_ou_line_outcome(total_goals, line, is_over)
            if outcome == "WIN":
                p_win += prob
            elif outcome == "HALF_WIN":
                p_half_win += prob
            elif outcome == "PUSH":
                p_push += prob
            elif outcome == "HALF_LOSS":
                p_half_loss += prob
            elif outcome == "LOSS":
                p_loss += prob

    total = p_win + p_half_win + p_push + p_half_loss + p_loss
    if total > 0:
        p_win /= total
        p_half_win /= total
        p_push /= total
        p_half_loss /= total
        p_loss /= total

    # Push = refund (neutral), excluded from effective probability.
    eff_prob = p_win + 0.5 * p_half_win

    return {
        "p_win": float(p_win),
        "p_half_win": float(p_half_win),
        "p_push": float(p_push),
        "p_half_loss": float(p_half_loss),
        "p_loss": float(p_loss),
        "effective_win_prob": float(eff_prob)
    }
