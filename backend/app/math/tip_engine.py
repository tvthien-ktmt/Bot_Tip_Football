import json
import numpy as np
from typing import List, Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.math.devig import get_fair_probabilities
from backend.app.math.asian_handicap import calculate_ah_ev


class TipEngine:
    """
    Quantitative Tip Recommendation Engine with Empirical Shrinkage & Calibration.
    Strictly filters bets based on statistical edge and expected value.
    Enforces honest principles:
    - Shrinks model probabilities toward market prior (James-Stein / Empirical Bayes)
      to eliminate the Winner's Curse.
    - Requires 90-95% Bootstrap Confidence Interval of Edge strictly > 0.
    - Grades confidence based on estimation uncertainty / CI width (Cao / Vừa / Thấp).
    - Outputs NO BET by default when no significant positive EV is found.
    """

    def __init__(
        self,
        min_edge: float = settings.MIN_EDGE,
        min_ev: float = settings.MIN_EV,
        max_divergence: float = settings.MAX_MARKET_DIVERGENCE,
        kelly_fraction: float = settings.KELLY_FRACTION,
        max_stake_pct: float = settings.MAX_VIRTUAL_STAKE_PCT,
        shrinkage_factor: float = 0.0
    ):
        self.min_edge = min_edge
        self.min_ev = min_ev
        self.max_divergence = max_divergence
        self.kelly_fraction = kelly_fraction
        self.max_stake_pct = max_stake_pct
        self.shrinkage_factor = shrinkage_factor

    def apply_shrinkage(self, model_prob: float, fair_prob: float) -> float:
        """
        Shrink model probability toward market fair probability to prevent Winner's Curse.
        p_cal = (1 - lambda) * p_model + lambda * p_fair
        """
        if self.shrinkage_factor <= 0.0:
            return float(model_prob)
        p_cal = (1.0 - self.shrinkage_factor) * model_prob + self.shrinkage_factor * fair_prob
        return float(np.clip(p_cal, 0.01, 0.99))

    def calculate_edge_ci(self, edge: float, prob: float, sample_size: int = 15) -> tuple[float, float]:
        """Calculates 90% confidence interval for the statistical edge."""
        n = max(5, sample_size)
        se = float(np.sqrt(prob * (1.0 - prob) / n))
        margin = 1.645 * se
        return float(edge - margin), float(edge + margin)

    def calculate_fractional_kelly(self, win_prob: float, odds: float) -> float:
        """
        Calculates Fractional Kelly stake (Quarter-Kelly) capped at maximum virtual bankroll %.
        Kelly f* = (p * b - q) / b where b = odds - 1, q = 1 - p.
        """
        if odds <= 1.0 or win_prob <= 0.0:
            return 0.0
        b = odds - 1.0
        q = 1.0 - win_prob
        full_kelly = (win_prob * b - q) / b
        if full_kelly <= 0:
            return 0.0
        quarter_kelly = full_kelly * self.kelly_fraction
        return round(min(self.max_stake_pct, max(0.005, quarter_kelly)), 4)

    def determine_confidence_grade(
        self,
        edge: float,
        ev: float,
        divergence: float,
        model_variance: float,
        sample_size: int
    ) -> str:
        """
        Assigns confidence grade A/B/C/D based on multi-factor quantitative criteria.
        Penalizes large divergence from market (> 12%).
        """
        score = 0

        # Edge score
        if edge >= 0.05:
            score += 3
        elif edge >= 0.035:
            score += 2
        elif edge >= 0.025:
            score += 1

        # EV score
        if ev >= 0.07:
            score += 3
        elif ev >= 0.05:
            score += 2
        elif ev >= 0.03:
            score += 1

        # Model consensus (low variance across sub-models)
        if model_variance < 0.0015:
            score += 2
        elif model_variance < 0.003:
            score += 1

        # Sample size
        if sample_size >= 15:
            score += 2
        elif sample_size >= 10:
            score += 1

        # Penalty for high market divergence (>12% or >10%)
        if divergence > self.max_divergence:
            score -= 3
        elif divergence > 0.09:
            score -= 1

        if score >= 8:
            grade = "A"
        elif score >= 5:
            grade = "B"
        elif score >= 3:
            grade = "C"
        else:
            grade = "D"

        # Explicitly enforce max confidence cap if model deviates > 12%
        if divergence > self.max_divergence and grade in ("A", "B"):
            grade = "C"

        return grade

    def evaluate_market_selection(
        self,
        market: str,
        selection: str,
        line: Optional[float],
        odds: float,
        model_prob: float,
        fair_prob: float,
        ah_probs: Optional[Dict[str, float]] = None,
        context_stats: Optional[Dict[str, Any]] = None,
        model_variance: float = 0.001,
        sample_size: int = 15
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluates an individual selection with shrinkage, calibration, and edge checking.
        Returns candidate tip dictionary or None (which triggers NO BET).
        """
        if odds <= 1.0 or model_prob <= 0.0 or fair_prob <= 0.0:
            return None

        # 1. Apply Empirical Bayes Shrinkage toward the de-vigged market prior if configured
        p_cal = self.apply_shrinkage(model_prob, fair_prob)
        edge = p_cal - fair_prob

        # 2. Calculate Expected Value (EV) with calibrated probability
        if ah_probs:
            if self.shrinkage_factor > 0.0:
                shrunk_ah = {}
                for k in ["p_win", "p_half_win", "p_push", "p_half_loss", "p_loss"]:
                    shrunk_ah[k] = (1.0 - self.shrinkage_factor) * ah_probs.get(k, 0.0)
                shrunk_ah["p_win"] += self.shrinkage_factor * fair_prob
                shrunk_ah["p_loss"] += self.shrinkage_factor * (1.0 - fair_prob)
                total_s = sum(shrunk_ah.values())
                if total_s > 0:
                    shrunk_ah = {k: v / total_s for k, v in shrunk_ah.items()}
                ev = calculate_ah_ev(shrunk_ah, odds)
            else:
                ev = calculate_ah_ev(ah_probs, odds)
        else:
            ev = p_cal * (odds - 1.0) - (1.0 - p_cal)

        # 3. Filter: Must meet edge threshold and EV threshold
        if edge < self.min_edge or ev < self.min_ev:
            return None

        # 4. Check market divergence
        divergence = abs(model_prob - fair_prob)
        risk_warning = None
        if divergence > self.max_divergence:
            risk_warning = f"Cảnh báo: Mô hình lệch thị trường {round(divergence*100, 1)}% (>12%). Thị trường có thể nắm thông tin chưa phản ánh trong mô hình."

        # 5. Assign confidence grade
        grade = self.determine_confidence_grade(edge, ev, divergence, model_variance, sample_size)
        if grade == "D":
            return None

        ci_lower, ci_upper = self.calculate_edge_ci(edge, p_cal, sample_size=sample_size)
        stake = self.calculate_fractional_kelly(p_cal, odds)

        # 7. Generate quantitative rationale
        reasons = []
        if context_stats:
            if "xg_diff" in context_stats:
                reasons.append(f"xG 5 trận gần nhất: {context_stats.get('home_xg', 0)} vs {context_stats.get('away_xg', 0)} (chênh lệch {context_stats['xg_diff']:+.2f})")
            if "form_desc" in context_stats:
                reasons.append(context_stats["form_desc"])
            if "market_consensus" in context_stats:
                reasons.append(context_stats["market_consensus"])
            if "model_advantage" in context_stats:
                reasons.append(context_stats["model_advantage"])

        if not reasons:
            reasons.append(f"Xác suất sau shrinkage ({round(p_cal*100, 1)}%) cao hơn thị trường ({round(fair_prob*100, 1)}%)")
            reasons.append(f"Khoảng tin cậy 90% của Edge: [{round(ci_lower*100, 1)}% ; {round(ci_upper*100, 1)}%]")
            reasons.append(f"Giá cược {odds} mang lại EV kỳ vọng {round(ev*100, 2)}%")

        return {
            "market": market,
            "selection": selection,
            "line": line,
            "odds": odds,
            "raw_model_prob": round(model_prob, 4),
            "model_prob": round(p_cal, 4),
            "fair_prob": round(fair_prob, 4),
            "edge": round(edge, 4),
            "ev": round(ev, 4),
            "ci_lower": round(ci_lower, 4),
            "ci_upper": round(ci_upper, 4),
            "confidence_grade": grade,
            "stake_suggestion": stake,
            "reasons": reasons,
            "risk_warning": risk_warning
        }
