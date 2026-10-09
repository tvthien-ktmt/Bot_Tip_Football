from typing import Dict, Any, List
import numpy as np
from scipy.stats import poisson, nbinom
from backend.app.math.asian_handicap import calculate_ah_probabilities, calculate_ou_probabilities


class CornersModel:
    """
    Corner kick forecasting model using compound Poisson / Negative Binomial distribution.
    Parameters: team corner attack & defence rates, home advantage, and match tempo.
    """

    def __init__(self, home_corner_adv: float = 1.15):
        self.home_corner_adv = home_corner_adv

    def compute_expected_corners(
        self,
        home_corner_atk: float,
        home_corner_def: float,
        away_corner_atk: float,
        away_corner_def: float,
        tempo_factor: float = 1.0
    ) -> Tuple[float, float]:
        """
        Expected corners for home and away teams.
        """
        exp_h = max(1.5, home_corner_atk * (away_corner_def / 5.0) * self.home_corner_adv * tempo_factor)
        exp_a = max(1.5, away_corner_atk * (home_corner_def / 5.0) * tempo_factor)
        return float(exp_h), float(exp_a)

    def generate_corner_matrix(
        self,
        exp_home: float,
        exp_away: float,
        max_corners: int = 18
    ) -> np.ndarray:
        """
        Generates joint probability matrix for corners (0..18 x 0..18).
        """
        h_probs = [poisson.pmf(i, exp_home) for i in range(max_corners + 1)]
        a_probs = [poisson.pmf(j, exp_away) for j in range(max_corners + 1)]

        matrix = np.outer(h_probs, a_probs)
        matrix /= np.sum(matrix)
        return matrix

    def extract_corner_ou(
        self,
        matrix: np.ndarray,
        lines: List[float] = None
    ) -> Dict[float, Dict[str, float]]:
        """Extracts Corner Over/Under probabilities (default lines: 8.5, 9.5, 10.5, 11.5)."""
        if lines is None:
            lines = [8.5, 9.5, 10.5, 11.5]

        results = {}
        for line in lines:
            over_res = calculate_ou_probabilities(matrix, line, is_over=True)
            under_res = calculate_ou_probabilities(matrix, line, is_over=False)
            results[line] = {
                "over_prob": over_res["effective_win_prob"],
                "under_prob": under_res["effective_win_prob"]
            }
        return results

    def extract_corner_ah(
        self,
        matrix: np.ndarray,
        lines: List[float] = None
    ) -> Dict[float, Dict[str, float]]:
        """Extracts Corner Asian Handicap probabilities (e.g. -1.5, -2.0, -2.5)."""
        if lines is None:
            lines = [-2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5]

        results = {}
        for line in lines:
            h_res = calculate_ah_probabilities(matrix, line)
            a_res = calculate_ah_probabilities(matrix.T, -line)
            results[line] = {
                "home_prob": h_res["effective_win_prob"],
                "away_prob": a_res["effective_win_prob"]
            }
        return results


class CardsModel:
    """
    Cards forecasting model factoring referee strictness, derby intensity, and team fouls.
    """

    @staticmethod
    def compute_expected_cards(
        referee_avg_cards: float = 4.2,
        is_derby: bool = False,
        home_yellow_avg: float = 1.8,
        away_yellow_avg: float = 2.1
    ) -> float:
        """Calculates expected total yellow/red cards in the match."""
        base = (home_yellow_avg + away_yellow_avg) * (referee_avg_cards / 4.0)
        if is_derby:
            base *= 1.25
        return float(base)

    @staticmethod
    def calculate_card_ou(expected_cards: float, line: float = 4.5) -> Dict[str, float]:
        """Calculates Over / Under card probabilities."""
        p_under = sum(poisson.pmf(k, expected_cards) for k in range(int(line) + 1))
        p_over = max(0.0, 1.0 - p_under)
        return {
            "over_prob": float(p_over),
            "under_prob": float(p_under)
        }
