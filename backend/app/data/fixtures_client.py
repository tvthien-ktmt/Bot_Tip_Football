import io
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx
import numpy as np
import pandas as pd

from backend.app.core.config import settings
from backend.app.data.csv_loader import CSVDataLoader, parse_date_flexibly

logger = logging.getLogger(__name__)

FIXTURES_URL = "https://www.football-data.co.uk/fixtures.csv"

DIV_NAMES = {
    "E0": "Premier League",
    "E1": "Championship",
    "SP1": "La Liga",
    "I1": "Serie A",
    "D1": "Bundesliga"
}


class UpcomingFixturesClient:
    """
    Client for acquiring upcoming unplayed matches for prediction:
    1. Checks for unplayed rows (missing FTHG) in 2026/27 season files.
    2. Downloads live fixtures from football-data.co.uk/fixtures.csv.
    3. Supports manual fixture insertion / CSV upload.
    Standardizes reference odds for 1X2, O/U 2.5, and Asian Handicap.
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or (settings.BASE_DIR / "backend" / "data")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.loader = CSVDataLoader()

    def fetch_live_fixtures(self) -> pd.DataFrame:
        """Fetch fixtures.csv from football-data.co.uk or use local fallback."""
        csv_path = self.cache_dir / "latest_fixtures.csv"
        try:
            with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                resp = client.get(FIXTURES_URL)
                if resp.status_code == 200:
                    with open(csv_path, "wb") as f:
                        f.write(resp.content)
                    logger.info("Successfully fetched fresh fixtures.csv from football-data.co.uk")
                    df = pd.read_csv(io.BytesIO(resp.content), encoding="utf-8-sig", low_memory=False)
                    return df
        except Exception as e:
            logger.warning(f"Could not reach {FIXTURES_URL}: {e}")

        if csv_path.exists():
            return pd.read_csv(csv_path, encoding="utf-8-sig", low_memory=False)

        return pd.DataFrame()

    def get_upcoming_fixtures(self, target_divs: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Aggregate all upcoming unplayed matches across target leagues.
        Target date is around 2026-10-09.
        """
        if target_divs is None:
            target_divs = ["E0", "E1", "SP1", "I1", "D1"]

        # First, check cleaned_matches.parquet for unplayed rows in 2026/27
        parquet_path = self.cache_dir / "cleaned_matches.parquet"
        unplayed_from_files = pd.DataFrame()
        if parquet_path.exists():
            df_all = pd.read_parquet(parquet_path)
            unplayed_mask = df_all["Div"].isin(target_divs) & df_all["FTHG"].isna()
            unplayed_from_files = df_all[unplayed_mask].copy()

        # Next, fetch live fixtures
        live_raw = self.fetch_live_fixtures()
        unplayed_from_live = pd.DataFrame()
        if not live_raw.empty:
            live_raw.columns = [str(c).strip() for c in live_raw.columns]
            div_mask = live_raw["Div"].isin(target_divs)
            live_filtered = live_raw[div_mask].copy()
            if not live_filtered.empty:
                unplayed_from_live = self.loader.standardize_dataframe(live_filtered, source_file="fixtures.csv")

        # Combine
        combined = pd.concat([unplayed_from_files, unplayed_from_live], ignore_index=True)
        if combined.empty:
            logger.warning("No unplayed fixtures found automatically.")
            return pd.DataFrame()

        # Deduplicate
        combined = combined.drop_duplicates(subset=["Div", "match_date", "home_team", "away_team"]).reset_index(drop=True)
        combined = combined.sort_values(by=["match_date", "kickoff_time", "home_team"]).reset_index(drop=True)
        return combined
