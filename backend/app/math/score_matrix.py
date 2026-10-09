from typing import Dict, Any, List, Tuple
import numpy as np
from backend.app.math.asian_handicap import (
    calculate_ah_probabilities,
    calculate_ou_probabilities
)


class ScoreMatrixProcessor:
    """
    Extracts all consistent goal-based market probabilities from a score matrix.
    Ensures internal coherence between 1X2, O/U, AH, and BTTS.
    """

    @staticmethod
    def extract_1x2_probabilities(matrix: np.ndarray) -> Dict[str, float]:
        """Calculates Home Win, Draw, and Away Win probabilities."""
        p_home = float(np.sum(np.tril(matrix, -1)))
        p_draw = float(np.sum(np.diag(matrix)))
        p_away = float(np.sum(np.triu(matrix, 1)))

        total = p_home + p_draw + p_away
        return {
            "home": p_home / total,
            "draw": p_draw / total,
            "away": p_away / total
        }

    @staticmethod
    def extract_btts_probabilities(matrix: np.ndarray) -> Dict[str, float]:
        """Calculates Both Teams To Score (BTTS) Yes and No."""
        # Submatrix starting from index (1, 1) to (max, max)
        p_yes = float(np.sum(matrix[1:, 1:]))
        p_no = 1.0 - p_yes
        return {
            "yes": max(0.0, min(1.0, p_yes)),
            "no": max(0.0, min(1.0, p_no))
        }

    @staticmethod
    def extract_ou_markets(matrix: np.ndarray, lines: List[float] = None) -> Dict[float, Dict[str, float]]:
        """
        Calculates Over and Under probabilities for a list of goal lines.
        Default lines: [0.5, 1.5, 2.0, 2.25, 2.5, 2.75, 3.0, 3.5, 4.5]
        """
        if lines is None:
            lines = [0.5, 1.5, 2.0, 2.25, 2.5, 2.75, 3.0, 3.5, 4.5]

        results = {}
        for line in lines:
            over_dict = calculate_ou_probabilities(matrix, line, is_over=True)
            under_dict = calculate_ou_probabilities(matrix, line, is_over=False)
            results[line] = {
                "over_prob": over_dict["effective_win_prob"],
                "under_prob": under_dict["effective_win_prob"],
                "over_breakdown": over_dict,
                "under_breakdown": under_dict
            }
        return results

    @staticmethod
    def extract_ah_markets(matrix: np.ndarray, lines: List[float] = None) -> Dict[float, Dict[str, Any]]:
        """
        Calculates Asian Handicap home and away probabilities for handicap lines.
        Default lines: [-2.0, -1.75, -1.5, -1.25, -1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
        """
        if lines is None:
            lines = [-2.0, -1.75, -1.5, -1.25, -1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]

        results = {}
        for line in lines:
            home_breakdown = calculate_ah_probabilities(matrix, line)
            # Away handicap is the exact opposite line: -line
            away_breakdown = calculate_ah_probabilities(matrix.T, -line)

            results[line] = {
                "home_prob": home_breakdown["effective_win_prob"],
                "away_prob": away_breakdown["effective_win_prob"],
                "home_breakdown": home_breakdown,
                "away_breakdown": away_breakdown
            }
        return results

    @staticmethod
    def get_most_likely_score(matrix: np.ndarray) -> Tuple[int, int, float]:
        """Finds (home_goals, away_goals, probability) for highest probability cell."""
        idx = np.unravel_index(np.argmax(matrix, axis=None), matrix.shape)
        return int(idx[0]), int(idx[1]), float(matrix[idx])
