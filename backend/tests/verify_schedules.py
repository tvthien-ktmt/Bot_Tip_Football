import pandas as pd
from backend.app.data.csv_loader import CSVDataLoader
from backend.app.data.schedule_parser import load_all_schedules

def main():
    schedules = load_all_schedules()
    loader = CSVDataLoader()
    df_hist = loader.load_all_leagues()

    print("Total fixtures:", len(schedules))
    print("Total null dates:", schedules["match_date"].isna().sum())

    # Test Championship team names
    champ = schedules[schedules["Div"] == "E1"]
    birm_matches = champ[(champ["home_team"] == "Birmingham") | (champ["away_team"] == "Birmingham")]
    print("Birmingham matches in Championship:", len(birm_matches))
    buli_in_champ = champ[(champ["home_team"] == "Bundesliga") | (champ["away_team"] == "Bundesliga")]
    print("Bundesliga as team in Championship:", len(buli_in_champ))
    assert len(buli_in_champ) == 0, "Bundesliga should NOT be a team name in Championship!"
    assert len(birm_matches) == 38, f"Expected 38 Birmingham matches, got {len(birm_matches)}"

    # Test date ranges and team matches
    for div in ["E0", "E1", "SP1", "I1", "D1"]:
        sub = schedules[schedules["Div"] == div]
        min_d = sub["match_date"].min()
        max_d = sub["match_date"].max()
        print(f"Div {div}: {len(sub)} matches, min date: {min_d}, max date: {max_d}")
        assert min_d.year == 2026 and min_d.month == 10, f"Expected min date in 2026-10 for {div}, got {min_d}"

        # Check matching with historical CSV teams
        hist_teams = set(df_hist[df_hist["Div"] == div]["HomeTeam"].dropna().unique())
        sched_teams = set(sub["home_team"].dropna().unique()) | set(sub["away_team"].dropna().unique())
        unmatched = sched_teams - hist_teams
        print(f"  Unmatched teams in {div}:", unmatched if unmatched else "NONE (100% MATCH!)")
        assert len(unmatched) == 0, f"Unmatched teams in {div}: {unmatched}"

    print("ALL VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
