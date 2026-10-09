from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from scipy.optimize import minimize

from backend.app.math.devig import get_fair_probabilities, devig_shin, devig_multiplicative
from backend.app.math.dixon_coles import DixonColesModel
from backend.app.math.asian_handicap import calculate_ah_probabilities, calculate_ou_probabilities


class MarketImpliedModel:
    """
    M6: MARKET-IMPLIED MODEL (The Fundamental Prior).
    Takes market odds (1X2, O/U 2.5, Asian Handicap line/odds),
    de-vigs them (Shin / Multiplicative), and reverse-optimizes (lambda_home, lambda_away)
    such that the resulting Dixon-Coles score matrix accurately reconstructs:
    1. P(1X2)
    2. P(Over 2.5)
    3. Asian Handicap effective win probability.

    Serves as the rigorous probabilistic market prior. All subsequent ML models
    learn only the residual alpha relative to this implied distribution.
    """

    def __init__(self, devig_method: str = "shin", default_rho: float = -0.06):
        self.devig_method = devig_method
        self.default_rho = default_rho
        self.dc = DixonColesModel(rho=default_rho)

    def fit_from_odds(
        self,
        odds_1x2: Tuple[float, float, float],
        odds_ou25: Optional[Tuple[float, float]] = None,
        ah_line: Optional[float] = None,
        odds_ah: Optional[Tuple[float, float]] = None,
    ) -> Dict[str, Any]:
        """
        Reverse-solve (lambda_home, lambda_away) from bookmaker odds.
        """
        o_h, o_d, o_a = odds_1x2
        if any(np.isnan([o_h, o_d, o_a])) or any(o < 1.01 for o in [o_h, o_d, o_a]):
            # Fallback to balanced default if odds missing
            lambda_h, lambda_a = 1.35, 1.15
            score_mat = self.dc.score_matrix(lambda_h, lambda_a, rho=self.default_rho, max_goals=10)
            return {
                "lambda_home": lambda_h,
                "lambda_away": lambda_a,
                "rho": self.default_rho,
                "score_matrix": score_mat,
                "fair_1x2": [0.42, 0.28, 0.30],
                "fair_ou25": 0.52,
                "convergence": False,
            }

        # 1. De-vig 1X2
        fair_1x2 = get_fair_probabilities([o_h, o_d, o_a], method=self.devig_method)
        target_p_h, target_p_d, target_p_a = fair_1x2

        # 2. De-vig O/U 2.5 if present
        target_p_over = None
        if odds_ou25 and len(odds_ou25) == 2:
            ov, un = odds_ou25
            if not np.isnan(ov) and not np.isnan(un) and ov >= 1.01 and un >= 1.01:
                fair_ou = get_fair_probabilities([ov, un], method=self.devig_method)
                target_p_over = fair_ou[0]

        # 3. De-vig Asian Handicap if present
        target_p_ah_h = None
        if ah_line is not None and not np.isnan(ah_line) and odds_ah and len(odds_ah) == 2:
            ahh, aha = odds_ah
            if not np.isnan(ahh) and not np.isnan(aha) and ahh >= 1.01 and aha >= 1.01:
                fair_ah = get_fair_probabilities([ahh, aha], method=self.devig_method)
                target_p_ah_h = fair_ah[0]

        # Initial guess based on simple heuristic
        # If home favored (p_h > p_a), lam_h > lam_a
        total_exp_goals = 2.70
        if target_p_over is not None:
            total_exp_goals = 2.2 + 1.2 * target_p_over
        
        ratio = max(0.2, min(5.0, target_p_h / max(0.01, target_p_a)))
        init_lam_a = total_exp_goals / (1.0 + np.sqrt(ratio))
        init_lam_h = total_exp_goals - init_lam_a
        init_lam_h = float(np.clip(init_lam_h, 0.3, 4.0))
        init_lam_a = float(np.clip(init_lam_a, 0.3, 4.0))

        def loss_function(params: np.ndarray) -> float:
            lam_h, lam_a = params
            if lam_h <= 0.05 or lam_a <= 0.05:
                return 1e6

            matrix = self.dc.score_matrix(lam_h, lam_a, rho=self.default_rho, max_goals=10)

            # Probabilities from score matrix
            # 1X2
            p_h = np.sum(np.tril(matrix, -1))
            p_d = np.sum(np.diag(matrix))
            p_a = np.sum(np.triu(matrix, 1))

            loss = 3.0 * ((p_h - target_p_h) ** 2 + (p_d - target_p_d) ** 2 + (p_a - target_p_a) ** 2)

            # Over 2.5
            if target_p_over is not None:
                # Sum P(h + a > 2)
                p_ov = 0.0
                for h_g in range(11):
                    for a_g in range(11):
                        if h_g + a_g > 2:
                            p_ov += matrix[h_g, a_g]
                loss += 2.0 * ((p_ov - target_p_over) ** 2)

            # Asian handicap
            if target_p_ah_h is not None and ah_line is not None:
                ah_res = calculate_ah_probabilities(matrix, ah_line)
                loss += 2.0 * ((ah_res["effective_win_prob"] - target_p_ah_h) ** 2)

            return float(loss)

        res = minimize(
            loss_function,
            x0=[init_lam_h, init_lam_a],
            bounds=[(0.1, 5.5), (0.1, 5.5)],
            method="L-BFGS-B",
            options={"maxiter": 60, "ftol": 1e-7}
        )

        opt_lam_h, opt_lam_a = float(res.x[0]), float(res.x[1])
        score_matrix = self.dc.score_matrix(opt_lam_h, opt_lam_a, rho=self.default_rho, max_goals=10)

        p_h = float(np.sum(np.tril(score_matrix, -1)))
        p_d = float(np.sum(np.diag(score_matrix)))
        p_a = float(np.sum(np.triu(score_matrix, 1)))

        p_ov = float(sum(score_matrix[h, a] for h in range(11) for a in range(11) if h + a > 2))

        return {
            "lambda_home": opt_lam_h,
            "lambda_away": opt_lam_a,
            "rho": self.default_rho,
            "score_matrix": score_matrix,
            "model_1x2": [p_h, p_d, p_a],
            "fair_1x2": fair_1x2,
            "fair_ou25": target_p_over,
            "model_ou25": p_ov,
            "convergence": bool(res.success),
            "loss": float(res.fun),
        }
