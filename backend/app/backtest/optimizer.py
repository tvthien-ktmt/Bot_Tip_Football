import logging
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
import optuna

from backend.app.core.config import settings
from backend.app.backtest.walkforward import WalkForwardEvaluator

logger = logging.getLogger(__name__)
optuna.logging.set_verbosity(optuna.logging.WARNING)


class OptunaHyperparameterTuner:
    """
    Optuna optimization engine for walk-forward parameters:
    - xi: time decay rate in [0.0005, 0.004]
    - w: log-linear pooling weight in [0.0, 0.35]
    - min_edge: edge threshold in [0.015, 0.06]
    - min_ev: EV threshold in [0.02, 0.08]
    Evaluated on validation seasons (prior to 2025/26 hold-out).
    """

    def __init__(self, n_trials: int = 15):
        self.n_trials = n_trials
        self.evaluator = WalkForwardEvaluator()

    def optimize_league_parameters(self, league_div: str = "E0") -> Dict[str, Any]:
        """Run study to find optimal hyperparameters for a league."""
        def objective(trial: optuna.Trial) -> float:
            xi = trial.suggest_float("xi", 0.0005, 0.0040, log=True)
            w = trial.suggest_float("w", 0.0, 0.30)
            min_edge = trial.suggest_float("min_edge", 0.015, 0.055)
            min_ev = trial.suggest_float("min_ev", 0.02, 0.07)

            res = self.evaluator.run_league_backtest(
                league_div=league_div,
                mode="T-24h",
                xi=xi,
                w=w,
                min_edge=min_edge,
                min_ev=min_ev,
            )
            if "metrics" not in res:
                return 1.0

            # Objective: minimize RPS of final model
            return float(res["metrics"]["model_final"]["rps"])

        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=self.n_trials)

        best_params = study.best_params
        best_val = study.best_value
        logger.info(f"Optimal parameters for {league_div}: {best_params} (best RPS: {best_val:.4f})")

        return {
            "league": league_div,
            "best_rps": round(best_val, 4),
            "best_params": best_params,
        }
