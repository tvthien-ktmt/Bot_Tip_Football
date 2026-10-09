import os
import logging
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx
import pandas as pd
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.entities import League, Season, Team, TeamAlias, Match, OddsSnapshot
from backend.app.data.team_mapper import normalize_team_name

logger = logging.getLogger(__name__)

LEAGUE_CONFIGS = [
    {"code": "E0", "name": "Premier League", "country": "England"},
    {"code": "SP1", "name": "La Liga", "country": "Spain"},
    {"code": "I1", "name": "Serie A", "country": "Italy"},
    {"code": "D1", "name": "Bundesliga", "country": "Germany"},
    {"code": "F1", "name": "Ligue 1", "country": "France"},
]


class FootballDataUKIngestion:
    """Ingests historical and current season match CSVs from football-data.co.uk"""

    BASE_URL = "https://www.football-data.co.uk/mmz4281"

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or (settings.DATA_DIR / "raw")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def get_csv_url(self, season_code: str, league_code: str) -> str:
        """e.g. season_code='2425', league_code='E0' -> https://www.football-data.co.uk/mmz4281/2425/E0.csv"""
        return f"{self.BASE_URL}/{season_code}/{league_code}.csv"

    def download_csv(self, season_code: str, league_code: str) -> Optional[Path]:
        """Download CSV if not cached or refreshable."""
        file_path = self.data_dir / f"{season_code}_{league_code}.csv"
        url = self.get_csv_url(season_code, league_code)
        
        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(resp.content)
                    logger.info(f"Downloaded CSV from {url} to {file_path}")
                    return file_path
                else:
                    logger.warning(f"Failed to download {url}: HTTP {resp.status_code}")
        except Exception as e:
            logger.warning(f"Error downloading {url}: {e}")

        if file_path.exists():
            return file_path
        return None

    def parse_csv_file(self, file_path: Path) -> pd.DataFrame:
        """Parse raw CSV file safely handling varied encodings and missing headers."""
        try:
            df = pd.read_csv(file_path, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="latin1")

        # Strip whitespace from column headers
        df.columns = [c.strip() for c in df.columns]
        return df

    def sync_to_db(self, db: Session, season_code: str = "2425", season_name: str = "2024-2025") -> int:
        """Download and ingest all configured leagues into database."""
        total_matches_synced = 0

        # Ensure leagues exist
        league_map = {}
        for l_cfg in LEAGUE_CONFIGS:
            league = db.query(League).filter_by(code=l_cfg["code"]).first()
            if not league:
                league = League(code=l_cfg["code"], name=l_cfg["name"], country=l_cfg["country"])
                db.add(league)
                db.commit()
                db.refresh(league)
            league_map[l_cfg["code"]] = league

        for l_cfg in LEAGUE_CONFIGS:
            code = l_cfg["code"]
            league = league_map[code]

            # Season
            season = db.query(Season).filter_by(league_id=league.id, name=season_name).first()
            if not season:
                season = Season(league_id=league.id, name=season_name, is_current=True)
                db.add(season)
                db.commit()
                db.refresh(season)

            file_path = self.download_csv(season_code, code)
            if not file_path or not file_path.exists():
                logger.info(f"CSV not found for {code}, skipping live sync.")
                continue

            df = self.parse_csv_file(file_path)
            if "HomeTeam" not in df.columns or "AwayTeam" not in df.columns:
                continue

            # Load or create teams
            for _, row in df.iterrows():
                h_name_raw = str(row.get("HomeTeam", "")).strip()
                a_name_raw = str(row.get("AwayTeam", "")).strip()
                if not h_name_raw or not a_name_raw or pd.isna(row.get("FTHG")):
                    continue

                h_norm = normalize_team_name(h_name_raw)
                a_norm = normalize_team_name(a_name_raw)

                home_team = db.query(Team).filter_by(name=h_norm).first()
                if not home_team:
                    home_team = Team(name=h_norm, league_id=league.id)
                    db.add(home_team)
                    db.commit()
                    db.refresh(home_team)
                    # Add alias
                    db.add(TeamAlias(team_id=home_team.id, alias=h_name_raw, source="football-data.co.uk"))
                    db.commit()

                away_team = db.query(Team).filter_by(name=a_norm).first()
                if not away_team:
                    away_team = Team(name=a_norm, league_id=league.id)
                    db.add(away_team)
                    db.commit()
                    db.refresh(away_team)
                    # Add alias
                    db.add(TeamAlias(team_id=away_team.id, alias=a_name_raw, source="football-data.co.uk"))
                    db.commit()

                # Parse date
                raw_date = str(row.get("Date", ""))
                match_dt = None
                for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
                    try:
                        match_dt = datetime.datetime.strptime(raw_date, fmt)
                        break
                    except ValueError:
                        continue
                if not match_dt:
                    continue

                # Check if match exists
                existing = db.query(Match).filter_by(
                    league_id=league.id,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    date=match_dt
                ).first()

                fthg = int(row["FTHG"]) if pd.notna(row.get("FTHG")) else None
                ftag = int(row["FTAG"]) if pd.notna(row.get("FTAG")) else None
                hthg = int(row["HTHG"]) if pd.notna(row.get("HTHG")) else None
                htag = int(row["HTAG"]) if pd.notna(row.get("HTAG")) else None

                hs = int(row["HS"]) if pd.notna(row.get("HS")) else None
                as_ = int(row["AS"]) if pd.notna(row.get("AS")) else None
                hst = int(row["HST"]) if pd.notna(row.get("HST")) else None
                ast_ = int(row["AST"]) if pd.notna(row.get("AST")) else None
                hc = int(row["HC"]) if pd.notna(row.get("HC")) else None
                ac = int(row["AC"]) if pd.notna(row.get("AC")) else None
                hy = int(row["HY"]) if pd.notna(row.get("HY")) else None
                ay = int(row["AY"]) if pd.notna(row.get("AY")) else None
                hr = int(row["HR"]) if pd.notna(row.get("HR")) else None
                ar = int(row["AR"]) if pd.notna(row.get("AR")) else None

                # Odds
                b365_h = float(row["B365H"]) if pd.notna(row.get("B365H")) else None
                b365_d = float(row["B365D"]) if pd.notna(row.get("B365D")) else None
                b365_a = float(row["B365A"]) if pd.notna(row.get("B365A")) else None
                
                # Closing Odds
                cl_h = float(row["B365CH"]) if pd.notna(row.get("B365CH")) else (
                    float(row["PSCH"]) if pd.notna(row.get("PSCH")) else b365_h
                )
                cl_d = float(row["B365CD"]) if pd.notna(row.get("B365CD")) else (
                    float(row["PSCD"]) if pd.notna(row.get("PSCD")) else b365_d
                )
                cl_a = float(row["B365CA"]) if pd.notna(row.get("B365CA")) else (
                    float(row["PSCA"]) if pd.notna(row.get("PSCA")) else b365_a
                )

                # AH
                ah_line = float(row["AHh"]) if pd.notna(row.get("AHh")) else None
                ah_h = float(row["B365AHH"]) if pd.notna(row.get("B365AHH")) else None
                ah_a = float(row["B365AHA"]) if pd.notna(row.get("B365AHA")) else None

                # O/U
                ou_o = float(row["B365>2.5"]) if pd.notna(row.get("B365>2.5")) else None
                ou_u = float(row["B365<2.5"]) if pd.notna(row.get("B365<2.5")) else None

                if not existing:
                    match_obj = Match(
                        league_id=league.id,
                        season_id=season.id,
                        date=match_dt,
                        home_team_id=home_team.id,
                        away_team_id=away_team.id,
                        status="FINISHED" if fthg is not None else "SCHEDULED",
                        home_score=fthg,
                        away_score=ftag,
                        ht_home_score=hthg,
                        ht_away_score=htag,
                        home_shots=hs,
                        away_shots=as_,
                        home_shots_target=hst,
                        away_shots_target=ast_,
                        home_corners=hc,
                        away_corners=ac,
                        home_yellow=hy,
                        away_yellow=ay,
                        home_red=hr,
                        away_red=ar,
                        b365_home_odds=b365_h,
                        b365_draw_odds=b365_d,
                        b365_away_odds=b365_a,
                        closing_home_odds=cl_h,
                        closing_draw_odds=cl_d,
                        closing_away_odds=cl_a,
                        ah_line=ah_line,
                        ah_home_odds=ah_h,
                        ah_away_odds=ah_a,
                        ou_line=2.5 if (ou_o or ou_u) else None,
                        ou_over_odds=ou_o,
                        ou_under_odds=ou_u
                    )
                    db.add(match_obj)
                    total_matches_synced += 1

            db.commit()

        logger.info(f"Synced {total_matches_synced} matches from football-data.co.uk")
        return total_matches_synced
