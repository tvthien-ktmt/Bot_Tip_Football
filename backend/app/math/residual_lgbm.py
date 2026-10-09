from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
import lightgbm as lgb
try:
    import shap
except ImportError:
    shap = None


class ResidualLGBMModel:
    """
    M7: GRADIENT BOOSTING (LIGHTGBM) RESIDUAL LEARNER.
    Learns residual edge: Target = (Actual_Outcome) - (Market_Implied_Prob).
    If the market is fully efficient, residuals are pure white noise and the model
    predicts 0 (no residual edge). If inefficiencies exist, it captures subtle predictive
    signals from shot pressure, opponent-adjusted form, referee tendencies, and line movements.
    Includes SHAP explanation generator.
    """

    def __init__(self, mode: str = "T-24h"):
        """
        mode: 'T-24h' (strictly opening market info) or 'T-1h' (closing odds and line shifts allowed).
        """
        self.mode = mode
        self.model: Optional[lgb.LGBMRegressor] = None
        self.feature_names: List[str] = []
        self.explainer: Optional[Any] = None

    def build_features_for_match(
        self,
        match_row: pd.Series,
        m2_prob_h: float,
        mkt_prob_h: float,
        home_elo: float,
        away_elo: float,
        pi_exp_gd: float,
        m5_xg_diff: float,
        home_form_5: float,
        away_form_5: float,
        home_rest_days: float,
        away_rest_days: float,
        referee_cards_avg: float,
        league_avg_cards: float = 3.75,
        matchweek: int = 10,
    ) -> Dict[str, float]:
        """
        Construct point-in-time features strictly using pre-match data.
        In T-24h mode, line movement features are strictly 0.0.
        """
        feats = {
            "diff_m2_market_h": float(m2_prob_h - mkt_prob_h),
            "diff_elo_scaled": float((home_elo + 65.0 - away_elo) / 400.0),
            "pi_expected_gd": float(pi_exp_gd),
            "m5_shot_xg_diff": float(m5_xg_diff),
            "home_form_5": float(home_form_5),
            "away_form_5": float(away_form_5),
            "rest_days_diff": float(np.clip(home_rest_days - away_rest_days, -14.0, 14.0)),
            "referee_cards_shrunk": float(0.7 * referee_cards_avg + 0.3 * league_avg_cards),
            "matchweek": float(matchweek),
        }

        # Market line movements only available in T-1h mode
        if self.mode == "T-1h":
            line_open = pd.to_numeric(match_row.get("ah_open_line", np.nan), errors="coerce")
            line_close = pd.to_numeric(match_row.get("ah_close_line", np.nan), errors="coerce")
            ah_shift = (line_close - line_open) if (pd.notna(line_open) and pd.notna(line_close)) else 0.0

            odds_open_h = pd.to_numeric(match_row.get("ref_open_h", np.nan), errors="coerce")
            odds_close_h = pd.to_numeric(match_row.get("ref_close_h", np.nan), errors="coerce")
            odds_ratio_h = (odds_close_h / odds_open_h - 1.0) if (pd.notna(odds_open_h) and pd.notna(odds_close_h) and odds_open_h > 0) else 0.0

            feats["line_shift_ah"] = float(ah_shift)
            feats["odds_shift_h"] = float(odds_ratio_h)
        else:
            # Strictly zeroed in T-24h mode to eliminate leakage
            feats["line_shift_ah"] = 0.0
            feats["odds_shift_h"] = 0.0

        return feats

    def train(
        self,
        X_train: pd.DataFrame,
        y_residual_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_residual_val: Optional[pd.Series] = None,
    ) -> "ResidualLGBMModel":
        """
        Train regularized LightGBM on residuals with early stopping.
        """
        self.feature_names = list(X_train.columns)
        self.model = lgb.LGBMRegressor(
            n_estimators=150,
            learning_rate=0.03,
            max_depth=3,
            num_leaves=7,
            min_child_samples=25,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.5,
            reg_lambda=1.0,
            random_state=42,
            verbosity=-1,
        )

        if X_val is not None and y_residual_val is not None and len(X_val) > 20:
            self.model.fit(
                X_train,
                y_residual_train,
                eval_set=[(X_val, y_residual_val)],
                callbacks=[lgb.early_stopping(stopping_rounds=15, verbose=False)],
            )
        else:
            self.model.fit(X_train, y_residual_train)

        # Fit SHAP explainer
        if shap is not None:
            try:
                self.explainer = shap.TreeExplainer(self.model)
            except Exception:
                self.explainer = None

        return self

    def predict_residual(self, features: Dict[str, float]) -> float:
        """Predict expected residual delta above/below market probability."""
        if self.model is None:
            return 0.0
        row_df = pd.DataFrame([features])[self.feature_names]
        delta = float(self.model.predict(row_df)[0])
        # Shrink large extreme predictions
        return float(np.clip(delta, -0.15, 0.15))

    def explain_prediction(self, features: Dict[str, float]) -> Dict[str, float]:
        """Return SHAP contributions for each feature."""
        if self.explainer is None or self.model is None:
            # Fallback to feature importance
            if self.model is not None and hasattr(self.model, "feature_importances_"):
                imp = self.model.feature_importances_
                tot = max(1e-5, sum(imp))
                return {fn: float(v / tot) for fn, v in zip(self.feature_names, imp)}
            return {}

        row_df = pd.DataFrame([features])[self.feature_names]
        shap_values = self.explainer.shap_values(row_df)
        if isinstance(shap_values, list):
            vals = shap_values[0][0]
        elif len(shap_values.shape) > 1:
            vals = shap_values[0]
        else:
            vals = shap_values

        return {fn: float(v) for fn, v in zip(self.feature_names, vals)}
