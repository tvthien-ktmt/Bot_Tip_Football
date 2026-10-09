import sys
import io

# Ensure UTF-8 output on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import logging
import json
from pathlib import Path
import pandas as pd

from backend.app.core.config import settings
from backend.app.data.csv_loader import CSVDataLoader
from backend.app.data.fixtures_client import UpcomingFixturesClient
from backend.app.backtest.walkforward import WalkForwardEvaluator
from backend.app.pipeline.match_predictor import MatchPredictor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("keolab_cli")


def run_audit(args):
    """Run data ingestion and audit on 25 CSV files."""
    print("=" * 70)
    print("KÈOLAB - DATA AUDIT & GOLDEN TEST VERIFICATION")
    print("=" * 70)
    loader = CSVDataLoader()
    df_all = loader.load_all_leagues()
    audit = loader.audit_log

    print(f"Files Processed:        {audit['files_processed']} / 25")
    print(f"Total Raw Rows:         {audit['total_raw_rows']}")
    print(f"Clean Matches Loaded:   {audit['clean_rows']}")
    print(f"Duplicate Rows Dropped: {audit['duplicate_rows_dropped']}")
    print(f"Negative Scores Found:  {audit['negative_scores_found']}")
    print(f"Invalid Odds (< 1.01):  {audit['invalid_odds_found']}")
    print(f"Parquet Saved At:       backend/data/cleaned_matches.parquet")
    print("=" * 70)


def run_backtest(args):
    """Run chronological walk-forward backtest across all 5 leagues."""
    print("=" * 70)
    print("KÈOLAB - CHRONOLOGICAL WALK-FORWARD BACKTEST")
    print("=" * 70)
    print("Zero Lookahead Bias | 1,000 Bootstrap Resamples | Hold-Out 2025/26")
    print(f"Prediction Mode: {args.mode}")
    print("-" * 70)

    evaluator = WalkForwardEvaluator()
    results = evaluator.run_all_leagues_and_generate_report()

    league_names = {
        "E0": "Premier League",
        "E1": "Championship",
        "SP1": "La Liga",
        "I1": "Serie A",
        "D1": "Bundesliga"
    }

    print("\nTỔNG KẾT KẾT QUẢ WALK-FORWARD (Hold-out 2023-2026):")
    print("-" * 75)
    print(f"{'Giải đấu':<18} | {'Trận':<5} | {'Model RPS':<10} | {'Mkt RPS':<8} | {'Acc %':<6} | {'Tips':<5} | {'Yield %':<7}")
    print("-" * 75)

    for div, data in results.items():
        sub = data[args.mode]
        name = league_names.get(div, div)
        if "metrics" in sub:
            m_rps = sub["metrics"]["model_final"]["rps"]
            c_rps = sub["metrics"]["market_close"]["rps"]
            acc = sub["metrics"]["model_final"]["accuracy"]
            tips_c = sub["simulation_tips"]["total_tips"]
            yield_val = sub["simulation_tips"]["yield_pct"]
            print(f"{name:<18} | {sub['evaluated_matches']:<5} | {m_rps:<10} | {c_rps:<8} | {acc:<6.1f} | {tips_c:<5} | {yield_val:<7.2f}%")

    print("-" * 75)
    print("\nBáo cáo chi tiết đã được xuất tự động tại:")
    print("  - Markdown: backend/reports/backtest_report.md")
    print("  - HTML:     backend/reports/backtest_report.html")
    print("  - Model Card: backend/reports/model_card.json")
    print("=" * 70)


def run_predict(args):
    """Generate predictions & tips for upcoming 2026/27 fixtures."""
    print("=" * 70)
    print("KÈOLAB - DỰ ĐOÁN & RA TIP ĐỊNH LƯỢNG (MÙA 2026/27)")
    print(f"Ngày mốc: 09/10/2026 | Chế độ: {args.mode}")
    print("=" * 70)

    fixtures_client = UpcomingFixturesClient()
    target_divs = None if args.div == "ALL" else [args.div]
    fixtures_df = fixtures_client.get_upcoming_fixtures(target_divs=target_divs)

    if fixtures_df.empty:
        print("Không tìm thấy fixtures sắp đá cho tiêu chí yêu cầu.")
        return

    # Load historical matches for context
    parquet_path = settings.BASE_DIR / "backend" / "data" / "cleaned_matches.parquet"
    hist_df = pd.read_parquet(parquet_path) if parquet_path.exists() else None

    predictor = MatchPredictor(mode=args.mode)

    total_matches = len(fixtures_df)
    tips_count = 0
    no_bet_count = 0

    print(f"Tìm thấy {total_matches} trận sắp đá. Đang tính toán ma trận xác suất...\n")

    for idx, row in fixtures_df.iterrows():
        pred = predictor.predict_match(row, historical_matches=hist_df)
        m = pred["match"]
        xg = pred["expected_goals"]
        probs = pred["probs"]

        print(f"[{m['league']}] {m['date']} {m['kickoff']} | {m['home']} vs {m['away']}")
        print(f"  xG Dự Báo:  {m['home']} {xg['home']} - {xg['away']} {m['away']} (Tổng: {xg['total']})")
        print(f"  Xác Suất:   1X2: [{probs['1x2'][0]*100:.1f}%, {probs['1x2'][1]*100:.1f}%, {probs['1x2'][2]*100:.1f}%] | O/U 2.5: {probs['over_under']['2.5']*100:.1f}% | Góc TB: {probs['corners']['mean']}")

        if pred["is_no_bet"]:
            no_bet_count += 1
            print(f"  QUYẾT ĐỊNH: [NO BET] - {pred['no_bet_reason']}")
        else:
            tips_count += len(pred["tips"])
            print(f"  QUYẾT ĐỊNH: [CÓ TIP KHẢ THI]")
            for t in pred["tips"]:
                print(f"    * Kèo: {t['market']} - {t['selection']} @ {t['odds']} | EV: {t['ev']*100:+.1f}% | Edge: {t['edge']*100:+.1f}% | Hạng: {t['grade']} | Vốn ảo: {t['stake_virtual']}")
                for r in t["reasons"]:
                    print(f"      - {r}")

        print("-" * 70)

    print("\nTỔNG HỢP RA TIP:")
    print(f"  Tổng trận phân tích: {total_matches}")
    print(f"  Số tip đủ điều kiện: {tips_count}")
    print(f"  Số trận NO BET:       {no_bet_count} ({no_bet_count/total_matches*100:.1f}%)")
    print("\nKhuyến cáo: Mọi nhận định mang tính học thuật & giải trí. Không đảm bảo lợi nhuận.")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="KèoLab Quantitative Football Tip Analyzer CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Audit command
    subparsers.add_parser("audit", help="Validate and audit 25 CSV data files")

    # Backtest command
    bt_parser = subparsers.add_parser("backtest", help="Run walk-forward chronological backtest")
    bt_parser.add_argument("--mode", choices=["T-24h", "T-1h"], default="T-24h", help="Prediction cutoff mode")

    # Predict command
    pred_parser = subparsers.add_parser("predict", help="Generate tips for upcoming 2026/27 matches")
    pred_parser.add_argument("--mode", choices=["T-24h", "T-1h"], default="T-24h", help="Prediction cutoff mode")
    pred_parser.add_argument("--div", default="ALL", help="League Div (E0, E1, SP1, I1, D1, or ALL)")

    args = parser.parse_args()
    if args.command == "audit":
        run_audit(args)
    elif args.command == "backtest":
        run_backtest(args)
    elif args.command == "predict":
        run_predict(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
