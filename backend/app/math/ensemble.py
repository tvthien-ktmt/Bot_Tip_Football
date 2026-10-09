from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from scipy.special import expit, logit


class LogLinearEnsemble:
    """
    M8: ENSEMBLE VIA LOG-LINEAR POOLING.
    Formula:
    logit(p_final) = logit(p_market) + w * (logit(p_model) - logit(p_market))
    where w in [0, 1] is learned via walk-forward log loss / RPS optimization.

    If w ≈ 0, the engine honestly concludes:
    'Không có edge ngoài thị trường (No edge beyond market)'
    and reports this clearly to the user without forcing bets.
    """

    def __init__(self, w: float = 0.15, threshold_no_edge: float = 0.04):
        self.w = float(np.clip(w, 0.0, 1.0))
        self.threshold_no_edge = threshold_no_edge

    def pool_binary(self, p_market: float, p_model: float, custom_w: Optional[float] = None) -> Tuple[float, bool]:
        """
        Pool binary probabilities (e.g. Over 2.5, BTTS, Asian Handicap side).
        Returns: (p_final, has_edge_flag)
        """
        weight = self.w if custom_w is None else float(np.clip(custom_w, 0.0, 1.0))

        # Clip probabilities to avoid infinite logits
        eps = 1e-6
        pm = float(np.clip(p_market, eps, 1.0 - eps))
        pmo = float(np.clip(p_model, eps, 1.0 - eps))

        # Logit combination
        logit_mkt = logit(pm)
        logit_mod = logit(pmo)

        logit_final = logit_mkt + weight * (logit_mod - logit_mkt)
        p_final = float(expit(logit_final))

        has_edge = (weight > self.threshold_no_edge) and (abs(p_final - p_market) > 0.015)
        return p_final, has_edge

    def pool_1x2(
        self,
        p_market_1x2: List[float],
        p_model_1x2: List[float],
        custom_w: Optional[float] = None,
    ) -> Tuple[List[float], bool]:
        """
        Multi-class log-linear pooling for 1X2 market.
        log(p_final_i) = log(p_market_i) + w * (log(p_model_i) - log(p_market_i)) + C
        Returns: ([p_h, p_d, p_a], has_edge_flag)
        """
        weight = self.w if custom_w is None else float(np.clip(custom_w, 0.0, 1.0))

        eps = 1e-6
        pm = np.clip(np.array(p_market_1x2, dtype=np.float64), eps, 1.0)
        pmo = np.clip(np.array(p_model_1x2, dtype=np.float64), eps, 1.0)

        # Normalize inputs
        pm = pm / np.sum(pm)
        pmo = pmo / np.sum(pmo)

        log_pm = np.log(pm)
        log_pmo = np.log(pmo)

        log_final = log_pm + weight * (log_pmo - log_pm)
        p_final = np.exp(log_final - np.max(log_final))
        p_final = p_final / np.sum(p_final)

        max_divergence = float(np.max(np.abs(p_final - pm)))
        has_edge = (weight > self.threshold_no_edge) and (max_divergence > 0.02)

        return [float(p) for p in p_final], has_edge
