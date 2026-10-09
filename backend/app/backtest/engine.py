import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.models.entities import Match, BacktestResult
from backend.app.math.dixon_coles import DixonColesModel
from backend.app.math.score_matrix import ScoreMatrixProcessor
from backend.app.math.devig import get_fair_probabilities
from backend.app.math.asian_handicap import evaluate_ah_line_outcome, evaluate_ou_line_outcome
from backend.app.math.tip_engine import TipEngine
from backend.app.backtest.metrics import BacktestMetricsTracker

logger = logging.getLogger(__name__)


class WalkForwardBacktestEngine:
    """
    Executes walk-forward historical simulation.
    Strictly preserves chronological order with zero lookahead bias.
    """

    def __init__(self, db: Session):
        self.db = db
        self.tip_engine = TipEngine()
        self.dc_model = DixonColesModel(rho=-0.06)

    def run_backtest(
        self,
        league_id: Optional[int] = None,
        min_history_matches: int = 20
    ) -> Dict[str, Any]:
        """
        Runs walk-forward backtest across finished historical matches.
        """
        query = self.db.query(Match).filter(Match.status == "FINISHED")
        if league_id:
            query = query.filter(Match.league_id == league_id)

        # Order chronologically
        matches = query.order_by(Match.date.asc()).all()
        if len(matches) < min_history_matches:
            return {"error": "Not enough finished matches for backtest"}

        tracker = BacktestMetricsTracker()

        for idx in range(min_history_matches, len(matches)):
            curr_match = matches[idx]
            past_matches = matches[:idx]  # Point-in-time slice: only matches strictly before curr_match

            # Calculate point-in-time attack and defence ratings
            h_past = [m for m in past_matches if m.home_team_id == curr_match.home_team_id or m.away_team_id == curr_match.home_team_id]
            a_past = [m for m in past_matches if m.home_team_id == curr_match.away_team_id or m.away_team_id == curr_match.away_team_id]

            if len(h_past) < 4 or len(a_past) < 4:
                continue

            # Average goals
            h_scored = sum(m.home_score if m.home_team_id == curr_match.home_team_id else m.away_score for m in h_past[-8:])
            h_conceded = sum(m.away_score if m.home_team_id == curr_match.home_team_id else m.home_score for m in h_past[-8:])
            a_scored = sum(m.home_score if m.home_team_id == curr_match.away_team_id else m.away_score for m in a_past[-8:])
            a_conceded = sum(m.away_score if m.home_team_id == curr_match.away_team_id else m.home_score for m in a_past[-8:])

            h_atk = max(0.6, (h_scored / len(h_past[-8:])) / 1.35)
            h_def = max(0.6, (h_conceded / len(h_past[-8:])) / 1.35)
            a_atk = max(0.6, (a_scored / len(a_past[-8:])) / 1.35)
            a_def = max(0.6, (a_conceded / len(a_past[-8:])) / 1.35)

            exp_h, exp_a = self.dc_model.compute_expected_goals(h_atk, h_def, a_atk, a_def)
            matrix = self.dc_model.generate_score_matrix(exp_h, exp_a)

            # Actual match result
            actual_gd = curr_match.home_score - curr_match.away_score
            actual_total = curr_match.home_score + curr_match.away_score
            actual_1x2 = "H" if actual_gd > 0 else ("D" if actual_gd == 0 else "A")

            # 1. Asian Handicap test
            if curr_match.ah_line is not None and curr_match.ah_home_odds and curr_match.ah_away_odds:
                line = curr_match.ah_line
                h_odds = curr_match.ah_home_odds
                a_odds = curr_match.ah_away_odds
                closing_h = curr_match.closing_home_odds or h_odds

                fair_probs = get_fair_probabilities([h_odds, a_odds], method="shin")
                fair_h_prob = fair_probs[0]

                ah_dict = ScoreMatrixProcessor.extract_ah_markets(matrix, lines=[line])
                model_h_prob = ah_dict[line]["home_prob"]
                h_breakdown = ah_dict[line]["home_breakdown"]

                tip = self.tip_engine.evaluate_market_selection(
                    market="AH",
                    selection=f"Home {line}",
                    line=line,
                    odds=h_odds,
                    model_prob=model_h_prob,
                    fair_prob=fair_h_prob,
                    ah_probs=h_breakdown,
                    sample_size=len(h_past)
                )

                if tip:
                    outcome = evaluate_ah_line_outcome(actual_gd, line)
                    stake = tip["stake_suggestion"] * 100.0  # units out of 100
                    pnl = 0.0

                    if outcome == "WIN":
                        pnl = stake * (h_odds - 1.0)
                    elif outcome == "HALF_WIN":
                        pnl = stake * 0.5 * (h_odds - 1.0)
                    elif outcome == "PUSH":
                        pnl = 0.0
                    elif outcome == "HALF_LOSS":
                        pnl = -stake * 0.5
                    elif outcome == "LOSS":
                        pnl = -stake

                    tracker.record_bet(
                        match_id=curr_match.id,
                        market="AH",
                        selection=tip["selection"],
                        confidence_grade=tip["confidence_grade"],
                        odds=h_odds,
                        closing_odds=closing_h,
                        model_prob=model_h_prob,
                        fair_prob=fair_h_prob,
                        stake=stake,
                        outcome=outcome,
                        pnl=pnl,
                        actual_1x2=actual_1x2
                    )

            # 2. Over / Under 2.5 test
            if curr_match.ou_over_odds and curr_match.ou_under_odds:
                o_odds = curr_match.ou_over_odds
                u_odds = curr_match.ou_under_odds
                fair_ou = get_fair_probabilities([o_odds, u_odds], method="shin")
                fair_o_prob = fair_ou[0]

                ou_dict = ScoreMatrixProcessor.extract_ou_markets(matrix, lines=[2.5])
                model_o_prob = ou_dict[2.5]["over_prob"]

                tip = self.tip_engine.evaluate_market_selection(
                    market="OU",
                    selection="Over 2.5",
                    line=2.5,
                    odds=o_odds,
                    model_prob=model_o_prob,
                    fair_prob=fair_o_prob,
                    sample_size=len(h_past)
                )

                if tip:
                    outcome = evaluate_ou_line_outcome(actual_total, 2.5, is_over=True)
                    stake = tip["stake_suggestion"] * 100.0
                    pnl = stake * (o_odds - 1.0) if outcome == "WIN" else -stake

                    tracker.record_bet(
                        match_id=curr_match.id,
                        market="OU",
                        selection=tip["selection"],
                        confidence_grade=tip["confidence_grade"],
                        odds=o_odds,
                        closing_odds=o_odds,
                        model_prob=model_o_prob,
                        fair_prob=fair_o_prob,
                        stake=stake,
                        outcome=outcome,
                        pnl=pnl,
                        actual_1x2=actual_1x2
                    )

        summary = tracker.summarize()

        # Save to database backtest_results table
        bt_record = BacktestResult(
            model_version="DixonColes-Ensemble-v1.0",
            market="ALL",
            test_period="Past 120 Days Walk-Forward",
            total_bets=summary["total_tips"],
            won_bets=summary["won"],
            half_won_bets=summary["half_won"],
            push_bets=summary["push"],
            half_lost_bets=summary["half_lost"],
            lost_bets=summary["lost"],
            roi=summary["simulated_roi_pct"],
            yield_pct=summary["yield_pct"],
            brier_score=summary["brier_score"],
            log_loss=summary["log_loss"],
            rps=summary["rps"],
            clv_avg=summary["avg_clv_pct"],
            calibration_data_json=json.dumps(summary["by_confidence"])
        )
        self.db.add(bt_record)
        self.db.commit()

        return summary
