import io
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx
import numpy as np
import pandas as pd

from backend.app.core.config import settings
from backend.app.data.csv_loader import CSVDataLoader, parse_date_flexibly
from backend.app.data.schedule_parser import load_all_schedules

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
    Client for acquiring upcoming unplayed matches for prediction.
    Priority order:
    1. Local schedule files (Lich_Thi_Dau/*.txt) — always available offline.
    2. Unplayed rows (missing FTHG) in 2026/27 season CSV/parquet files.
    3. Live fixtures from football-data.co.uk/fixtures.csv (online fallback).
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

    def load_schedule_fixtures(self, target_divs: List[str]) -> pd.DataFrame:
        """
        Load upcoming fixtures from local Lich_Thi_Dau TXT schedule files.
        These are always available offline and contain the full season calendar.
        """
        schedule_dir = settings.BASE_DIR / "Lich_Thi_Dau"
        if not schedule_dir.exists():
            logger.info("Lich_Thi_Dau directory not found, skipping schedule files.")
            return pd.DataFrame()

        try:
            all_schedules = load_all_schedules(schedule_dir)
            if all_schedules.empty:
                return pd.DataFrame()

            # Filter to target divisions
            filtered = all_schedules[all_schedules["Div"].isin(target_divs)].copy()

            # Filter to upcoming matches only (from today onwards)
            today = pd.Timestamp.now().normalize()
            if "match_date" in filtered.columns:
                filtered = filtered[filtered["match_date"] >= today].copy()

            logger.info(f"Loaded {len(filtered)} upcoming fixtures from schedule files")
            return filtered
        except Exception as e:
            logger.error(f"Error loading schedule fixtures: {e}")
            return pd.DataFrame()

    def get_upcoming_fixtures(self, target_divs: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Aggregate all upcoming unplayed matches across target leagues.
        Priority: Schedule files > Parquet unplayed > Live fixtures.csv
        """
        if target_divs is None:
            target_divs = ["E0", "E1", "SP1", "I1", "D1"]

        all_sources = []

        # Source 1: Local schedule TXT files (highest priority, always available)
        schedule_df = self.load_schedule_fixtures(target_divs)
        if not schedule_df.empty:
            all_sources.append(schedule_df)

        # Source 2: Check cleaned_matches.parquet for unplayed rows in 2026/27
        parquet_path = self.cache_dir / "cleaned_matches.parquet"
        if parquet_path.exists():
            try:
                df_all = pd.read_parquet(parquet_path)
                unplayed_mask = df_all["Div"].isin(target_divs) & df_all["FTHG"].isna()
                unplayed_from_files = df_all[unplayed_mask].copy()
                if not unplayed_from_files.empty:
                    all_sources.append(unplayed_from_files)
            except Exception as e:
                logger.warning(f"Error reading parquet: {e}")

        # Source 3: Live fixtures from football-data.co.uk
        live_raw = self.fetch_live_fixtures()
        if not live_raw.empty:
            try:
                live_raw.columns = [str(c).strip() for c in live_raw.columns]
                if "Div" in live_raw.columns:
                    div_mask = live_raw["Div"].isin(target_divs)
                    live_filtered = live_raw[div_mask].copy()
                    if not live_filtered.empty:
                        unplayed_from_live = self.loader.standardize_dataframe(
                            live_filtered, source_file="fixtures.csv"
                        )
                        all_sources.append(unplayed_from_live)
            except Exception as e:
                logger.warning(f"Error processing live fixtures: {e}")

        # Combine all sources
        if not all_sources:
            logger.warning("No unplayed fixtures found from any source.")
            return pd.DataFrame()

        combined = pd.concat(all_sources, ignore_index=True)

        # Deduplicate: prefer schedule data (first source) over others
        combined = combined.drop_duplicates(
            subset=["Div", "match_date", "home_team", "away_team"],
            keep="first"
        ).reset_index(drop=True)

        combined = combined.sort_values(
            by=["match_date", "kickoff_time", "home_team"]
        ).reset_index(drop=True)

        logger.info(f"Total upcoming fixtures: {len(combined)}")
        return combined
