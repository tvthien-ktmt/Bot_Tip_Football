import json
from typing import List, Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.math.devig import get_fair_probabilities
from backend.app.math.asian_handicap import calculate_ah_ev


class TipEngine:
    """
    Quantitative Tip Recommendation Engine.
    Strictly filters bets based on statistical edge and expected value.
    Enforces honest principles: penalizes extreme market divergence and outputs NO BET when appropriate.
    """

    def __init__(
        self,
        min_edge: float = settings.MIN_EDGE,
        min_ev: float = settings.MIN_EV,
        max_divergence: float = settings.MAX_MARKET_DIVERGENCE,
        kelly_fraction: float = settings.KELLY_FRACTION,
        max_stake_pct: float = settings.MAX_VIRTUAL_STAKE_PCT
    ):
        self.min_edge = min_edge
        self.min_ev = min_ev
        self.max_divergence = max_divergence
        self.kelly_fraction = kelly_fraction
        self.max_stake_pct = max_stake_pct

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
        Penalizes large divergence from market.
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
        Evaluates an individual selection. Returns candidate tip dictionary or None.
        """
        if odds <= 1.0 or model_prob <= 0.0 or fair_prob <= 0.0:
            return None

        edge = model_prob - fair_prob

        # Calculate EV
        if ah_probs:
            ev = calculate_ah_ev(ah_probs, odds)
        else:
            ev = model_prob * (odds - 1.0) - (1.0 - model_prob)

        # Check basic thresholds
        if edge < self.min_edge or ev < self.min_ev:
            return None

        divergence = abs(model_prob - fair_prob)
        risk_warning = None
        if divergence > self.max_divergence:
            risk_warning = f"Cảnh báo: Mô hình lệch thị trường {round(divergence*100, 1)}% (>12%). Thị trường có thể nắm thông tin chưa phản ánh trong mô hình."

        grade = self.determine_confidence_grade(edge, ev, divergence, model_variance, sample_size)
        stake = self.calculate_fractional_kelly(model_prob, odds)

        # Generate bullet reasons from context stats
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
            reasons.append(f"Xác suất mô hình ({round(model_prob*100, 1)}%) cao hơn thị trường ({round(fair_prob*100, 1)}%)")
            reasons.append(f"Giá cược {odds} mang lại EV kỳ vọng {round(ev*100, 2)}%")

        return {
            "market": market,
            "selection": selection,
            "line": line,
            "odds": odds,
            "model_prob": round(model_prob, 4),
            "fair_prob": round(fair_prob, 4),
            "edge": round(edge, 4),
            "ev": round(ev, 4),
            "confidence_grade": grade,
            "stake_suggestion": stake,
            "reasons": reasons,
            "risk_warning": risk_warning
        }
