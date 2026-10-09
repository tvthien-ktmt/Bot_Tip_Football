from typing import Tuple, Dict, Optional, List
import numpy as np
import pandas as pd
from scipy.stats import poisson
from scipy.optimize import minimize


class DixonColesModel:
    """
    Dixon & Coles (1997) model with low-score correlation parameter rho and time-decay xi.
    Adjusts the probability of 0-0, 1-0, 0-1, and 1-1 scores.
    Supports maximum likelihood estimation (MLE) with attack constraint sum(attack) = 0
    and exponential time-decay weighting exp(-xi * days).
    """

    def __init__(self, rho: float = -0.06, home_adv: float = 1.25, xi: float = 0.0019):
        self.rho = rho
        self.home_adv = home_adv
        self.xi = xi  # Exponential time decay per day
        self.team_ratings: Dict[str, Dict[str, float]] = {}

    def tau_adjustment(self, x: int, y: int, lambda_h: float, mu_a: float, rho: Optional[float] = None) -> float:
        """Tau correlation multiplier from Dixon & Coles (1997) eq (4.1)."""
        r = self.rho if rho is None else rho
        if x == 0 and y == 0:
            return max(0.01, 1.0 - lambda_h * mu_a * r)
        elif x == 0 and y == 1:
            # Dixon & Coles eq 4.1: τ(0,1) = 1 + λ₁ρ
            return max(0.01, 1.0 + lambda_h * r)
        elif x == 1 and y == 0:
            # Dixon & Coles eq 4.1: τ(1,0) = 1 + μ₂ρ
            return max(0.01, 1.0 + mu_a * r)
        elif x == 1 and y == 1:
            return max(0.01, 1.0 - r)
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
        max_goals: int = 10,
        rho: Optional[float] = None
    ) -> np.ndarray:
        """
        Generates score matrix with Dixon-Coles rho adjustment on low scores.
        """
        matrix = np.zeros((max_goals + 1, max_goals + 1), dtype=np.float64)

        for x in range(max_goals + 1):
            p_x = poisson.pmf(x, exp_home)
            for y in range(max_goals + 1):
                p_y = poisson.pmf(y, exp_away)
                adj = self.tau_adjustment(x, y, exp_home, exp_away, rho=rho)
                matrix[x, y] = p_x * p_y * adj

        # Normalize matrix to strictly sum to 1.0
        matrix_sum = np.sum(matrix)
        if matrix_sum > 0:
            matrix /= matrix_sum

        return matrix

    def score_matrix(
        self,
        lambda_home: float,
        lambda_away: float,
        rho: Optional[float] = None,
        max_goals: int = 10
    ) -> np.ndarray:
        """Convenience alias for generate_score_matrix."""
        return self.generate_score_matrix(lambda_home, lambda_away, max_goals=max_goals, rho=rho)

    def fit(
        self,
        df: pd.DataFrame,
        xi: Optional[float] = None,
        reference_date: Optional[pd.Timestamp] = None
    ) -> "DixonColesModel":
        """
        Fit attack/defence parameters per team, home advantage, and rho
        via weighted log-likelihood with time decay exp(-xi * days) and constraint sum(attack) = 0.
        """
        decay_xi = self.xi if xi is None else xi
        valid_df = df.dropna(subset=["FTHG", "FTAG", "home_team", "away_team"]).copy()
        if len(valid_df) < 20:
            return self

        teams = sorted(list(set(valid_df["home_team"]).union(set(valid_df["away_team"]))))
        n_teams = len(teams)
        team_to_idx = {t: i for i, t in enumerate(teams)}

        # Dates & Weights
        if "match_date" in valid_df.columns:
            dates = pd.to_datetime(valid_df["match_date"])
        else:
            dates = pd.to_datetime(valid_df["Date"], dayfirst=True)
            
        ref_date = reference_date or dates.max()
        days_ago = (ref_date - dates).dt.total_seconds() / 86400.0
        weights = np.exp(-decay_xi * np.maximum(0, days_ago.values))

        home_indices = valid_df["home_team"].map(team_to_idx).values
        away_indices = valid_df["away_team"].map(team_to_idx).values
        fthg = valid_df["FTHG"].values.astype(int)
        ftag = valid_df["FTAG"].values.astype(int)

        # Initial parameters:
        # log_attack (n_teams - 1), log_defence (n_teams), log_home_adv (1), rho (1)
        # Total parameters = (n_teams - 1) + n_teams + 1 + 1 = 2 * n_teams + 1
        # We enforce sum(attack) = 0 by setting attack[n-1] = -sum(attack[0:n-1])
        x0 = np.zeros(2 * n_teams + 1)  # attack (n-1), defence (n), home_adv (1), rho (1)
        x0[-2] = 0.25  # log home advantage ~ 1.28
        x0[-1] = -0.05  # initial rho

        def loss_func(params):
            log_att = np.zeros(n_teams)
            log_att[:-1] = params[: n_teams - 1]
            log_att[-1] = -np.sum(log_att[:-1])  # constraint sum(log_att) = 0

            log_def = params[n_teams - 1 : 2 * n_teams - 1]
            log_gamma = params[-2]
            rho_val = np.clip(params[-1], -0.15, 0.15)

            # lambda_h = exp(log_att_h + log_def_a + log_gamma)
            # mu_a = exp(log_att_a + log_def_h)
            lam_h = np.exp(np.clip(log_att[home_indices] + log_def[away_indices] + log_gamma, -4.0, 3.0))
            mu_a = np.exp(np.clip(log_att[away_indices] + log_def[home_indices], -4.0, 3.0))

            # Poisson log pmf + tau adjustment
            # log(P(x|lam)) = x*log(lam) - lam - log(x!)
            log_pmf_h = fthg * np.log(lam_h) - lam_h
            log_pmf_a = ftag * np.log(mu_a) - mu_a

            # Tau adjustment
            tau_vals = np.ones(len(valid_df))
            m00 = (fthg == 0) & (ftag == 0)
            m01 = (fthg == 0) & (ftag == 1)
            m10 = (fthg == 1) & (ftag == 0)
            m11 = (fthg == 1) & (ftag == 1)

            tau_vals[m00] = np.maximum(0.01, 1.0 - lam_h[m00] * mu_a[m00] * rho_val)
            tau_vals[m01] = np.maximum(0.01, 1.0 + lam_h[m01] * rho_val)
            tau_vals[m10] = np.maximum(0.01, 1.0 + mu_a[m10] * rho_val)
            tau_vals[m11] = np.maximum(0.01, 1.0 - rho_val)

            log_lik = weights * (log_pmf_h + log_pmf_a + np.log(tau_vals))
            return -np.sum(log_lik)

        res = minimize(loss_func, x0, method="L-BFGS-B", options={"maxiter": 500, "disp": False})
        assert len(res.x) == 2 * n_teams + 1, f"Expected 2*n+1 parameters, got {len(res.x)}"

        opt_att = np.zeros(n_teams)
        opt_att[:-1] = res.x[: n_teams - 1]
        opt_att[-1] = -np.sum(opt_att[:-1])

        opt_def = res.x[n_teams - 1 : 2 * n_teams - 1]
        self.home_adv = float(np.exp(res.x[-2]))
        self.rho = float(np.clip(res.x[-1], -0.15, 0.15))

        self.team_ratings = {}
        for t, idx in team_to_idx.items():
            self.team_ratings[t] = {
                "attack": float(np.exp(opt_att[idx])),
                "defence": float(np.exp(opt_def[idx]))
            }

        return self
