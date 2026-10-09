import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from backend.app.core.config import settings
from backend.app.data.csv_loader import CSVDataLoader, parse_date_flexibly, infer_season_from_date


def test_golden_premier_league_2025_2026():
    """
    GOLDEN TEST on Season 20252026.csv (Premier League 2025/26):
    Must match exact golden benchmarks (to 3 decimal places):
    - 380 matches, 132 columns, 20 teams, 23 referees, Div=E0, 2025-08-15 to 2026-05-24.
    - H/D/A: 42.6% / 27.4% / 30.0%.
    - Mean goals: Home 1.53, Away 1.22, Total 2.75.
    - Over 2.5: 55.0%, BTTS: 56.1%.
    - Corners/match: mean 10.00 (std 3.27).
    - Yellow cards: mean 3.75.
    - Overround Avg close: 1.057.
    - Market benchmark (de-vig proportional AvgCH/AvgCD/AvgCA):
      - RPS: 0.2045
      - Log loss: 1.0118
      - Accuracy argmax: 49.5%
      - Avg open: RPS 0.2053
    """
    file_path = settings.BASE_DIR / "data_league" / "Premier League" / "Season 20252026.csv"
    assert file_path.exists(), f"Golden test file not found at {file_path}"

    loader = CSVDataLoader()
    df_raw = loader.load_single_csv(file_path)

    # 1. Shape and structure
    assert len(df_raw) == 380, f"Expected 380 rows, got {len(df_raw)}"
    assert df_raw.shape[1] == 132, f"Expected 132 columns, got {df_raw.shape[1]}"
    assert (df_raw["Div"] == "E0").all(), "All rows must have Div='E0'"
    assert len(df_raw["HomeTeam"].unique()) == 20, "Expected 20 unique teams"
    assert len(df_raw["Referee"].dropna().unique()) == 23, "Expected 23 referees"

    dates = parse_date_flexibly(df_raw["Date"])
    assert dates.min() == pd.Timestamp("2025-08-15"), f"Expected min date 2025-08-15, got {dates.min()}"
    assert dates.max() == pd.Timestamp("2026-05-24"), f"Expected max date 2026-05-24, got {dates.max()}"

    # 2. H/D/A proportions (42.6% / 27.4% / 30.0%)
    ftr_counts = df_raw["FTR"].value_counts(normalize=True)
    assert pytest.approx(ftr_counts["H"], abs=0.001) == 0.426
    assert pytest.approx(ftr_counts["D"], abs=0.001) == 0.274
    assert pytest.approx(ftr_counts["A"], abs=0.001) == 0.300

    # 3. Mean goals (Home 1.53, Away 1.22, Total 2.75)
    hg = df_raw["FTHG"].mean()
    ag = df_raw["FTAG"].mean()
    tg = (df_raw["FTHG"] + df_raw["FTAG"]).mean()
    assert pytest.approx(hg, abs=0.01) == 1.53
    assert pytest.approx(ag, abs=0.01) == 1.22
    assert pytest.approx(tg, abs=0.01) == 2.75

    # 4. Over 2.5 = 55.0%, BTTS = 56.1%
    o25 = ((df_raw["FTHG"] + df_raw["FTAG"]) > 2.5).mean()
    btts = ((df_raw["FTHG"] > 0) & (df_raw["FTAG"] > 0)).mean()
    assert pytest.approx(o25, abs=0.001) == 0.550
    assert pytest.approx(btts, abs=0.001) == 0.561

    # 5. Corners: mean 10.00, std 3.27
    total_corners = df_raw["HC"] + df_raw["AC"]
    assert pytest.approx(total_corners.mean(), abs=0.01) == 10.00
    assert pytest.approx(total_corners.std(), abs=0.01) == 3.27

    # 6. Yellow cards: mean 3.75
    total_yellow = df_raw["HY"] + df_raw["AY"]
    assert pytest.approx(total_yellow.mean(), abs=0.01) == 3.75

    # 7. Overround Avg close = 1.057
    inv_close = (1.0 / df_raw["AvgCH"] + 1.0 / df_raw["AvgCD"] + 1.0 / df_raw["AvgCA"]).mean()
    assert pytest.approx(inv_close, abs=0.001) == 1.057

    # 8. Market benchmark proportional de-vig
    p_h = (1.0 / df_raw["AvgCH"]) / (1.0 / df_raw["AvgCH"] + 1.0 / df_raw["AvgCD"] + 1.0 / df_raw["AvgCA"])
    p_d = (1.0 / df_raw["AvgCD"]) / (1.0 / df_raw["AvgCH"] + 1.0 / df_raw["AvgCD"] + 1.0 / df_raw["AvgCA"])
    p_a = (1.0 / df_raw["AvgCA"]) / (1.0 / df_raw["AvgCH"] + 1.0 / df_raw["AvgCD"] + 1.0 / df_raw["AvgCA"])

    y_h = (df_raw["FTR"] == "H").astype(float)
    y_d = (df_raw["FTR"] == "D").astype(float)
    y_a = (df_raw["FTR"] == "A").astype(float)

    # RPS = 0.5 * [(p_h - y_h)^2 + ((p_h + p_d) - (y_h + y_d))^2]
    rps_close = 0.5 * ((p_h - y_h) ** 2 + ((p_h + p_d) - (y_h + y_d)) ** 2).mean()
    assert pytest.approx(rps_close, abs=0.0005) == 0.2045

    # Log loss
    eps = 1e-15
    ll_close = - (y_h * np.log(np.clip(p_h, eps, 1)) + y_d * np.log(np.clip(p_d, eps, 1)) + y_a * np.log(np.clip(p_a, eps, 1))).mean()
    assert pytest.approx(ll_close, abs=0.0005) == 1.0118

    # Accuracy argmax = 49.5%
    preds = np.where(p_h > np.maximum(p_d, p_a), "H", np.where(p_d > p_a, "D", "A"))
    acc_close = (preds == df_raw["FTR"]).mean()
    assert pytest.approx(acc_close, abs=0.001) == 0.495

    # Avg open RPS = 0.2053
    p_ho = (1.0 / df_raw["AvgH"]) / (1.0 / df_raw["AvgH"] + 1.0 / df_raw["AvgD"] + 1.0 / df_raw["AvgA"])
    p_do = (1.0 / df_raw["AvgD"]) / (1.0 / df_raw["AvgH"] + 1.0 / df_raw["AvgD"] + 1.0 / df_raw["AvgA"])
    p_ao = (1.0 / df_raw["AvgA"]) / (1.0 / df_raw["AvgH"] + 1.0 / df_raw["AvgD"] + 1.0 / df_raw["AvgA"])
    rps_open = 0.5 * ((p_ho - y_h) ** 2 + ((p_ho + p_do) - (y_h + y_d)) ** 2).mean()
    assert pytest.approx(rps_open, abs=0.0005) == 0.2053


def test_loader_all_25_files_and_seasons():
    """Verify loading all 25 files across all 5 leagues without crashing."""
    loader = CSVDataLoader()
    df_all = loader.load_all_leagues()

    assert loader.audit_log["files_processed"] == 25, f"Expected 25 files, got {loader.audit_log['files_processed']}"
    assert len(df_all) > 7500, f"Expected >7500 matches, got {len(df_all)}"

    expected_divs = {"E0", "E1", "SP1", "I1", "D1"}
    actual_divs = set(df_all["Div"].unique())
    assert expected_divs.issubset(actual_divs), f"Missing divs: {expected_divs - actual_divs}"

    # Verify seasons derived from Date
    seasons = set(df_all["season"].unique())
    assert "2022/23" in seasons
    assert "2023/24" in seasons
    assert "2024/25" in seasons
    assert "2025/26" in seasons
    assert "2026/27" in seasons

    # Verify parquet was generated
    parquet_path = settings.BASE_DIR / "backend" / "data" / "cleaned_matches.parquet"
    assert parquet_path.exists(), "Cleaned matches parquet was not created"
