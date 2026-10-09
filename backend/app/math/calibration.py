from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression


def calculate_brier_score(y_true: List[int], y_prob: List[float]) -> float:
    """Mean squared difference between predicted probabilities and outcomes."""
    if len(y_true) == 0:
        return 0.0
    return float(np.mean([(p - y)**2 for y, p in zip(y_true, y_prob)]))


def calculate_log_loss(y_true: List[int], y_prob: List[float], eps: float = 1e-15) -> float:
    """Logarithmic loss metric."""
    if len(y_true) == 0:
        return 0.0
    losses = []
    for y, p in zip(y_true, y_prob):
        p_clipped = max(eps, min(1.0 - eps, p))
        losses.append(-(y * np.log(p_clipped) + (1 - y) * np.log(1 - p_clipped)))
    return float(np.mean(losses))


def calculate_rps_1x2(p_home: float, p_draw: float, p_away: float, outcome: str) -> float:
    """
    Ranked Probability Score (RPS) for 3-outcome 1X2 market (Constantinou & Fenton).
    outcome in ('H', 'D', 'A')
    """
    p_vec = [p_home, p_draw, p_away]
    if outcome == "H":
        y_vec = [1, 0, 0]
    elif outcome == "D":
        y_vec = [0, 1, 0]
    else:
        y_vec = [0, 0, 1]

    # Cumulative probabilities
    cum_p = np.cumsum(p_vec)
    cum_y = np.cumsum(y_vec)

    # For K=3 outcomes, denominator is (K - 1) = 2
    rps = (1.0 / 2.0) * np.sum((cum_p[:2] - cum_y[:2]) ** 2)
    return float(rps)


def compute_reliability_curve(
    y_true: List[int],
    y_prob: List[float],
    n_bins: int = 10
) -> Tuple[List[Dict[str, Any]], float]:
    """
    Generates reliability bins and Expected Calibration Error (ECE).
    """
    if len(y_true) == 0:
        return [], 0.0

    bins = np.linspace(0.0, 1.0, n_bins + 1)
    bin_data = []
    total_samples = len(y_true)
    ece = 0.0

    for i in range(n_bins):
        low, high = bins[i], bins[i+1]
        indices = [
            idx for idx, p in enumerate(y_prob)
            if (p >= low and p < high) or (i == n_bins - 1 and p >= low and p <= high)
        ]
        count = len(indices)
        if count > 0:
            avg_pred = float(np.mean([y_prob[idx] for idx in indices]))
            avg_obs = float(np.mean([y_true[idx] for idx in indices]))
            ece += (count / total_samples) * abs(avg_pred - avg_obs)
            bin_data.append({
                "bin_center": round((low + high) / 2.0, 3),
                "predicted_prob": round(avg_pred, 4),
                "observed_freq": round(avg_obs, 4),
                "sample_count": count
            })
        else:
            bin_data.append({
                "bin_center": round((low + high) / 2.0, 3),
                "predicted_prob": round((low + high) / 2.0, 3),
                "observed_freq": round((low + high) / 2.0, 3),
                "sample_count": 0
            })

    return bin_data, float(ece)


class ProbabilityCalibrator:
    """Calibrates raw probabilities using Platt scaling or Isotonic Regression."""

    def __init__(self, method: str = "platt"):
        self.method = method
        self.model = LogisticRegression() if method == "platt" else IsotonicRegression(out_of_bounds="clip")
        self.is_fitted = False

    def fit(self, probs: np.ndarray, y: np.ndarray):
        if len(probs) < 20:
            return self
        if self.method == "platt":
            X = np.log(np.clip(probs, 1e-4, 1 - 1e-4) / (1.0 - np.clip(probs, 1e-4, 1 - 1e-4))).reshape(-1, 1)
            self.model.fit(X, y)
        else:
            self.model.fit(probs, y)
        self.is_fitted = True
        return self

    def calibrate(self, prob: float) -> float:
        if not self.is_fitted:
            return float(prob)
        if self.method == "platt":
            logit = np.log(np.clip(prob, 1e-4, 1 - 1e-4) / (1.0 - np.clip(prob, 1e-4, 1 - 1e-4))).reshape(1, -1)
            return float(self.model.predict_proba(logit)[0, 1])
        else:
            return float(self.model.predict([prob])[0])
