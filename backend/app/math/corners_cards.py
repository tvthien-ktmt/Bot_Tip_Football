from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from scipy.stats import poisson, nbinom
from backend.app.math.asian_handicap import (
    calculate_ah_probabilities,
    calculate_ou_probabilities,
    evaluate_ou_line_outcome
)


class CornersModel:
    """
    Corner kick forecasting model using overdispersed Negative Binomial / compound Poisson.
    Golden benchmark (PL 2025/26): mean 10.00, std 3.27, variance 10.69 (> mean 10.00 -> overdispersed).
    Flags 'experimental': True and 'lean' guidance when no market odds are present.
    Enables user-entered line and odds to calculate fair value and EV.
    """

    def __init__(self, home_corner_adv: float = 1.15, dispersion_factor: float = 1.07):
        self.home_corner_adv = home_corner_adv
        self.dispersion_factor = dispersion_factor

    def compute_expected_corners(
        self,
        home_corner_atk: float,
        home_corner_def: float,
        away_corner_atk: float,
        away_corner_def: float,
        tempo_factor: float = 1.0
    ) -> Tuple[float, float]:
        """Expected corners for home and away teams."""
        exp_h = max(1.5, home_corner_atk * (away_corner_def / 5.0) * self.home_corner_adv * tempo_factor)
        exp_a = max(1.5, away_corner_atk * (home_corner_def / 5.0) * tempo_factor)
        return float(exp_h), float(exp_a)

    def _nbinom_pmf_series(self, mean: float, var_ratio: float, max_val: int = 20) -> np.ndarray:
        """
        Generate Negative Binomial PMF matching given mean and variance = mean * var_ratio.
        """
        if var_ratio <= 1.001:
            return np.array([poisson.pmf(i, mean) for i in range(max_val + 1)])

        variance = mean * var_ratio
        p = mean / variance
        r = (mean ** 2) / (variance - mean)
        pmf = np.array([nbinom.pmf(k, r, p) for k in range(max_val + 1)])
        s = np.sum(pmf)
        return pmf / s if s > 0 else pmf

    def generate_corner_matrix(
        self,
        exp_home: float,
        exp_away: float,
        max_corners: int = 18
    ) -> np.ndarray:
        """Generates joint probability matrix for corners (0..18 x 0..18) using Negative Binomial."""
        h_probs = self._nbinom_pmf_series(exp_home, self.dispersion_factor, max_corners)
        a_probs = self._nbinom_pmf_series(exp_away, self.dispersion_factor, max_corners)

        matrix = np.outer(h_probs, a_probs)
        matrix_sum = np.sum(matrix)
        if matrix_sum > 0:
            matrix /= matrix_sum
        return matrix

    def extract_corner_ou(
        self,
        matrix: np.ndarray,
        lines: Optional[List[float]] = None
    ) -> Dict[float, Dict[str, float]]:
        """Extracts Corner Over/Under probabilities (e.g. 8.5, 9.5, 10.0, 10.5, 11.5)."""
        if lines is None:
            lines = [8.5, 9.5, 10.0, 10.5, 11.5]

        results = {}
        for line in lines:
            over_res = calculate_ou_probabilities(matrix, line, is_over=True)
            under_res = calculate_ou_probabilities(matrix, line, is_over=False)
            results[line] = {
                "over_prob": float(over_res["effective_win_prob"]),
                "under_prob": float(under_res["effective_win_prob"])
            }
        return results

    def compute_manual_ev(
        self,
        matrix: np.ndarray,
        market_type: str,
        line: float,
        odds: float,
        selection: str = "OVER"
    ) -> Dict[str, Any]:
        """Compute EV when user enters line and bookmaker odds manually."""
        if market_type == "OU":
            is_over = (selection.upper() == "OVER")
            res = calculate_ou_probabilities(matrix, line, is_over=is_over)
            prob = res["effective_win_prob"]
        else:  # AH
            res = calculate_ah_probabilities(matrix, line)
            prob = res["effective_win_prob"] if selection.upper() == "HOME" else (1.0 - res["effective_win_prob"])

        fair_odds = 1.0 / max(0.001, prob)
        ev = prob * (odds - 1.0) - (1.0 - prob)
        return {
            "market": f"Corners {market_type}",
            "line": line,
            "selection": selection,
            "user_odds": odds,
            "model_prob": float(prob),
            "fair_odds": float(fair_odds),
            "ev": float(ev),
            "edge": float(prob - (1.0 / odds)),
            "label": "Thử nghiệm"
        }


class CardsModel:
    """
    Cards forecasting model factoring referee strictness, team fouls, and match heat.
    """

    @staticmethod
    def compute_expected_cards(
        referee_avg_cards: float = 3.75,
        league_avg_cards: float = 3.75,
        home_yellow_avg: float = 1.8,
        away_yellow_avg: float = 1.95,
        is_derby: bool = False
    ) -> float:
        """Calculates expected total cards in the match with referee shrinkage."""
        shrunk_ref = 0.7 * referee_avg_cards + 0.3 * league_avg_cards
        base = (home_yellow_avg + away_yellow_avg) * (shrunk_ref / max(1.0, league_avg_cards))
        if is_derby:
            base *= 1.20
        return float(max(1.0, base))

    @staticmethod
    def calculate_card_ou_probs(exp_cards: float, line: float = 3.5, max_cards: int = 15) -> Dict[str, float]:
        """
        Over/Under cards probability using Poisson distribution and standard O/U settlement,
        properly handling PUSH on whole lines (e.g. line 3.0) and half-win/loss on quarter lines.
        """
        p_win_ov, p_hw_ov, p_push, p_hl_ov, p_loss_ov = 0.0, 0.0, 0.0, 0.0, 0.0

        for k in range(max_cards + 1):
            prob = float(poisson.pmf(k, exp_cards))
            outcome_ov = evaluate_ou_line_outcome(k, line, is_over=True)
            if outcome_ov == "WIN":
                p_win_ov += prob
            elif outcome_ov == "HALF_WIN":
                p_hw_ov += prob
            elif outcome_ov == "PUSH":
                p_push += prob
            elif outcome_ov == "HALF_LOSS":
                p_hl_ov += prob
            else:
                p_loss_ov += prob

        total = p_win_ov + p_hw_ov + p_push + p_hl_ov + p_loss_ov
        if total > 0:
            p_win_ov /= total
            p_hw_ov /= total
            p_push /= total
            p_hl_ov /= total
            p_loss_ov /= total

        eff_over = p_win_ov + 0.5 * p_hw_ov
        eff_under = p_loss_ov + 0.5 * p_hl_ov

        return {
            "line": line,
            "over_prob": float(eff_over),
            "under_prob": float(eff_under),
            "p_win_over": float(p_win_ov),
            "p_push": float(p_push),
            "p_win_under": float(p_loss_ov),
            "fair_over_odds": float(1.0 / max(0.01, eff_over)),
            "fair_under_odds": float(1.0 / max(0.01, eff_under)),
            "label": "Thử nghiệm"
        }
