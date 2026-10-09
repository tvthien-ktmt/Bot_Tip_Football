from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd
from statsmodels.genmod.generalized_linear_model import GLM
from statsmodels.genmod.families import Poisson


class ShotBasedXGProxy:
    """
    M5: SHOT-BASED xG PROXY MODEL.
    Since raw xG is not present in football-data.co.uk CSVs,
    we estimate latent expected goals via Poisson GLM:
    Goals ~ ShotsOnTarget + (TotalShots - ShotsOnTarget) + HomeAdvantage
    and maintain exponential moving averages (EMA) of offensive/defensive shot quality.
    Reduces the variance/luck of final goal counts (lucky vs unlucky teams).
    """

    def __init__(self, alpha_ema: float = 0.15):
        self.alpha_ema = alpha_ema
        # Coefficients learned from historical baseline:
        # Typical goal probability per SOT is ~0.30 - 0.35; per off-target shot is ~0.02 - 0.04
        self.beta_sot = 0.315
        self.beta_shot_off = 0.032
        self.beta_intercept = 0.08
        self.team_shot_ratings: Dict[str, Dict[str, float]] = {}

    def fit_glm_coefficients(self, df: pd.DataFrame) -> "ShotBasedXGProxy":
        """Fit Poisson GLM on historical matches with shots and SOT."""
        valid_df = df.dropna(subset=["FTHG", "FTAG", "HS", "AS", "HST", "AST"]).copy()
        if len(valid_df) < 100:
            return self

        # Build home and away observations
        # Home: goals = FTHG, sot = HST, off = HS - HST
        home_obs = pd.DataFrame({
            "goals": valid_df["FTHG"],
            "sot": valid_df["HST"],
            "off": np.maximum(0, valid_df["HS"] - valid_df["HST"]),
            "is_home": 1.0,
        })
        away_obs = pd.DataFrame({
            "goals": valid_df["FTAG"],
            "sot": valid_df["AST"],
            "off": np.maximum(0, valid_df["AS"] - valid_df["AST"]),
            "is_home": 0.0,
        })
        comb = pd.concat([home_obs, away_obs], ignore_index=True)

        try:
            X = comb[["sot", "off", "is_home"]]
            X = sm_add_constant = np.column_stack([np.ones(len(comb)), X.values])
            y = comb["goals"].values
            glm = GLM(y, X, family=Poisson())
            res = glm.fit(disp=False)
            # Link is log, so expected goals = exp(b0 + b1*sot + b2*off + b3*home)
            # Or identity-based approximation
            self.beta_intercept = float(res.params[0])
            self.beta_sot = float(res.params[1])
            self.beta_shot_off = float(res.params[2])
        except Exception:
            # Safe defaults
            self.beta_sot = 0.315
            self.beta_shot_off = 0.032
            self.beta_intercept = 0.08

        return self

    def estimate_match_xg(self, shots: float, sot: float, is_home: bool = True) -> float:
        """Estimate single-match xG from shot profile."""
        sot_val = max(0.0, sot)
        off_val = max(0.0, shots - sot)
        home_bonus = 0.15 if is_home else 0.0
        # Direct expected goals proxy
        xg = self.beta_intercept + self.beta_sot * sot_val + self.beta_shot_off * off_val + home_bonus
        return float(max(0.15, xg))

    def update_team_ratings(self, df_chronological: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Compute EMA of offensive and defensive shot xG generation per team.
        """
        ratings: Dict[str, Dict[str, float]] = {}

        for _, row in df_chronological.iterrows():
            ht = str(row.get("home_team", "")).strip()
            at = str(row.get("away_team", "")).strip()
            if not ht or not at:
                continue

            hs = float(row.get("HS", 12.0)) if pd.notna(row.get("HS")) else 12.0
            hst = float(row.get("HST", 4.0)) if pd.notna(row.get("HST")) else 4.0
            as_ = float(row.get("AS", 10.0)) if pd.notna(row.get("AS")) else 10.0
            ast = float(row.get("AST", 3.0)) if pd.notna(row.get("AST")) else 3.0

            xg_h = self.estimate_match_xg(hs, hst, is_home=True)
            xg_a = self.estimate_match_xg(as_, ast, is_home=False)

            if ht not in ratings:
                ratings[ht] = {"off_xg": 1.45, "def_xg": 1.25}
            if at not in ratings:
                ratings[at] = {"off_xg": 1.35, "def_xg": 1.35}

            # Exponential update
            ratings[ht]["off_xg"] = (1 - self.alpha_ema) * ratings[ht]["off_xg"] + self.alpha_ema * xg_h
            ratings[ht]["def_xg"] = (1 - self.alpha_ema) * ratings[ht]["def_xg"] + self.alpha_ema * xg_a

            ratings[at]["off_xg"] = (1 - self.alpha_ema) * ratings[at]["off_xg"] + self.alpha_ema * xg_a
            ratings[at]["def_xg"] = (1 - self.alpha_ema) * ratings[at]["def_xg"] + self.alpha_ema * xg_h

        self.team_shot_ratings = ratings
        return ratings
