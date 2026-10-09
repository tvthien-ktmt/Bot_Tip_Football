from typing import Tuple, Dict, Optional
import numpy as np
from scipy.stats import poisson


class DixonColesModel:
    """
    Dixon & Coles (1997) model with low-score correlation parameter rho and time-decay xi.
    Adjusts the probability of 0-0, 1-0, 0-1, and 1-1 scores.
    """

    def __init__(self, rho: float = -0.06, home_adv: float = 1.25, xi: float = 0.0019):
        self.rho = rho
        self.home_adv = home_adv
        self.xi = xi  # Exponential time decay per day

    def tau_adjustment(self, x: int, y: int, lambda_h: float, mu_a: float) -> float:
        """Tau correlation multiplier from Dixon & Coles (1997) eq (4.1)."""
        if x == 0 and y == 0:
            return max(0.01, 1.0 - lambda_h * mu_a * self.rho)
        elif x == 0 and y == 1:
            return max(0.01, 1.0 + mu_a * self.rho)
        elif x == 1 and y == 0:
            return max(0.01, 1.0 + lambda_h * self.rho)
        elif x == 1 and y == 1:
            return max(0.01, 1.0 - self.rho)
        else:
            return 1.0

    def compute_expected_goals(
        self,
        home_attack: float,
        home_defence: float,
        away_attack: float,
        away_defence: float,
        league_avg_goals: float = 1.35
    ) -> Tuple[float, float]:
        """Calculates expected goals with attack/defence parameters and home advantage."""
        exp_home = max(0.2, league_avg_goals * home_attack * away_defence * self.home_adv)
        exp_away = max(0.2, league_avg_goals * away_attack * home_defence)
        return float(exp_home), float(exp_away)

    def generate_score_matrix(
        self,
        exp_home: float,
        exp_away: float,
        max_goals: int = 10
    ) -> np.ndarray:
        """
        Generates score matrix with Dixon-Coles rho adjustment on low scores.
        """
        matrix = np.zeros((max_goals + 1, max_goals + 1), dtype=np.float64)

        for x in range(max_goals + 1):
            p_x = poisson.pmf(x, exp_home)
            for y in range(max_goals + 1):
                p_y = poisson.pmf(y, exp_away)
                adj = self.tau_adjustment(x, y, exp_home, exp_away)
                matrix[x, y] = p_x * p_y * adj

        # Normalize matrix to strictly sum to 1.0
        matrix_sum = np.sum(matrix)
        if matrix_sum > 0:
            matrix /= matrix_sum

        return matrix
