from typing import List, Dict, Optional
import numpy as np
from scipy.optimize import brentq


def devig_multiplicative(odds: List[float]) -> List[float]:
    """
    Standard proportional / multiplicative normalization.
    p_i = (1 / odds_i) / sum(1 / odds_k)
    """
    raw_implied = [1.0 / o if o > 1.0 else 0.0 for o in odds]
    total_margin = sum(raw_implied)
    if total_margin <= 0:
        return [1.0 / len(odds)] * len(odds)
    return [p / total_margin for p in raw_implied]


def devig_power(odds: List[float]) -> List[float]:
    """
    Power method: find k such that sum((1 / odds_i)^k) = 1.0.
    """
    raw_implied = np.array([1.0 / o for o in odds if o > 1.0])
    if len(raw_implied) != len(odds) or len(raw_implied) == 0:
        return devig_multiplicative(odds)

    def obj(k):
        return np.sum(np.power(raw_implied, k)) - 1.0

    try:
        # k is typically between 1.0 and 5.0
        k_opt = brentq(obj, 0.5, 10.0)
        fair = np.power(raw_implied, k_opt)
        return list(fair / np.sum(fair))
    except Exception:
        return devig_multiplicative(odds)


def devig_shin(odds: List[float]) -> List[float]:
    """
    Shin (1993) model: accounts for insider / informed betting proportion z.
    Solves for z in [0, 0.4] such that sum(pi_i) = 1.
    pi_i = (sqrt(z^2 + 4*(1-z)*(q_i^2 / S)) - z) / (2*(1-z)) where q_i = 1/odds_i, S = sum(q_i)
    """
    q = np.array([1.0 / o for o in odds if o > 1.0])
    if len(q) != len(odds) or len(q) == 0:
        return devig_multiplicative(odds)

    S = np.sum(q)
    if S <= 1.0:
        return list(q / S)

    def shin_probs(z):
        if np.isclose(z, 1.0):
            return q / S
        term = np.sqrt(z**2 + 4.0 * (1.0 - z) * (q**2) / S)
        return (term - z) / (2.0 * (1.0 - z))

    def objective(z):
        probs = shin_probs(z)
        return np.sum(probs) - 1.0

    try:
        z_opt = brentq(objective, 0.0, 0.4)
        fair_probs = shin_probs(z_opt)
        fair_probs = fair_probs / np.sum(fair_probs)
        return [float(p) for p in fair_probs]
    except Exception:
        # Fallback to multiplicative
        return devig_multiplicative(odds)


def get_fair_probabilities(odds: List[float], method: str = "shin") -> List[float]:
    """Helper to choose devigging algorithm: 'shin', 'power', or 'multiplicative'."""
    if method == "shin":
        return devig_shin(odds)
    elif method == "power":
        return devig_power(odds)
    else:
        return devig_multiplicative(odds)
