import math
from typing import Dict, List, Tuple
import numpy as np
from scipy.stats import poisson


class IndependentPoissonModel:
    """
    Maher (1982) Independent Poisson model for football match scores.
    P(X=x, Y=y) = Poisson(x; lambda_home) * Poisson(y; mu_away)
    """

    def __init__(self, home_adv: float = 1.25):
        self.home_adv = home_adv

    def compute_expected_goals(
        self,
        home_attack: float,
        home_defence: float,
        away_attack: float,
        away_defence: float,
        league_avg_goals: float = 1.35
    ) -> Tuple[float, float]:
        """
        Calculates expected goals lambda (home) and mu (away).
        lambda = league_avg * home_attack * away_defence * home_adv
        mu = league_avg * away_attack * home_defence
        """
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
        Generates (max_goals+1, max_goals+1) probability matrix.
        matrix[x, y] = P(Home = x, Away = y)
        """
        home_probs = [poisson.pmf(i, exp_home) for i in range(max_goals + 1)]
        away_probs = [poisson.pmf(j, exp_away) for j in range(max_goals + 1)]

        # Outer product
        matrix = np.outer(home_probs, away_probs)
        matrix /= np.sum(matrix)
        return matrix
