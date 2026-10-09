import os
import glob
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

DIV_TO_LEAGUE = {
    "E0": {"name": "Premier League", "country": "England"},
    "E1": {"name": "Championship", "country": "England"},
    "SP1": {"name": "La Liga", "country": "Spain"},
    "I1": {"name": "Serie A", "country": "Italy"},
    "D1": {"name": "Bundesliga", "country": "Germany"},
}

FOLDER_TO_DIV = {
    "Premier League": "E0",
    "Championship": "E1",
    "La Liga": "SP1",
    "Serie A": "I1",
    "Bundesliga": "D1",
}


def parse_date_flexibly(date_series: pd.Series) -> pd.Series:
    """Parse dates with dayfirst=True and handle varied formats dd/mm/yyyy, dd/mm/yy."""
    # First try default dayfirst parsing
    parsed = pd.to_datetime(date_series, dayfirst=True, errors="coerce")
    # For any failures, attempt explicit formats
    if parsed.isna().any():
        mask = parsed.isna() & date_series.notna()
        for fmt in ["%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"]:
            try:
                parsed.loc[mask] = pd.to_datetime(date_series[mask], format=fmt, errors="coerce")
                mask = parsed.isna() & date_series.notna()
                if not mask.any():
                    break
            except Exception:
                continue
    return parsed


def infer_season_from_date(dt: pd.Timestamp) -> str:
    """
    Infer European football season from match date.
    Season starts around July/August of year N and ends around May/June of year N+1.
    If month >= 7 (July onwards), season is N/N+1 (e.g. 2025-08 -> '2025/26').
    If month < 7 (Jan to June), season is (N-1)/N (e.g. 2026-05 -> '2025/26').
    """
    if pd.isna(dt):
        return "Unknown"
    year = dt.year
    month = dt.month
    if month >= 7:
        start_year = year
        end_year = (year + 1) % 100
        return f"{start_year}/{end_year:02d}"
    else:
        start_year = year - 1
        end_year = year % 100
        return f"{start_year}/{end_year:02d}"


class CSVDataLoader:
    """
    Robust Ingestion Engine for 25 CSV files from football-data.co.uk.
    Enforces utf-8-sig encoding, BOM stripping, CRLF compatibility,
    flexible date-to-season parsing, odds fallback chain (Avg -> B365 -> BW -> Max),
    and comprehensive validation auditing.
    """

    def __init__(self, data_league_dir: Optional[Path] = None):
        self.data_league_dir = data_league_dir or (settings.BASE_DIR / "data_league")
        self.audit_log: Dict[str, Any] = {
            "files_processed": 0,
            "total_raw_rows": 0,
            "clean_rows": 0,
            "duplicate_rows_dropped": 0,
            "negative_scores_found": 0,
            "invalid_odds_found": 0,
            "file_reports": [],
        }

    def load_single_csv(self, file_path: Path) -> pd.DataFrame:
        """Read single CSV file safely with utf-8-sig encoding."""
        # Read with utf-8-sig to automatically strip BOM and handle CRLF
        df = pd.read_csv(file_path, encoding="utf-8-sig", low_memory=False)
        # Strip whitespace from headers
        df.columns = [str(c).strip() for c in df.columns]
        
        # Deduce Div if missing from parent folder
        folder_name = file_path.parent.name
        if "Div" not in df.columns or df["Div"].isna().all():
            df["Div"] = FOLDER_TO_DIV.get(folder_name, "Unknown")
        else:
            # Fill missing Div with folder default
            df["Div"] = df["Div"].fillna(FOLDER_TO_DIV.get(folder_name, "Unknown"))

        return df

    def extract_odds_chain(
        self,
        row: pd.Series,
        prefixes: List[str],
        suffixes: List[str],
    ) -> Tuple[Optional[float], ...]:
        """
        Follow fallback chain: Avg -> B365 -> BW -> Max -> PS.
        Returns tuple of values corresponding to suffixes, and the provider name used.
        """
        for prov in prefixes:
            vals = []
            valid = True
            for s in suffixes:
                col = f"{prov}{s}"
                val = row.get(col, np.nan)
                try:
                    val_f = float(val)
                    if np.isnan(val_f) or val_f < 1.01:
                        valid = False
                        break
                    vals.append(val_f)
                except (ValueError, TypeError):
                    valid = False
                    break
            if valid and len(vals) == len(suffixes):
                return tuple(vals) + (prov,)
        
        return tuple([np.nan] * len(suffixes)) + ("None",)

    def standardize_dataframe(self, df: pd.DataFrame, source_file: str) -> pd.DataFrame:
        """Standardize raw columns into unified match records."""
        # Parse Dates
        dates = parse_date_flexibly(df["Date"])
        df["match_date"] = dates
        df["season"] = dates.apply(infer_season_from_date)

        # Standardize Kickoff Time
        if "Time" in df.columns:
            df["kickoff_time"] = df["Time"].fillna("15:00").astype(str).str.strip()
        else:
            df["kickoff_time"] = "15:00"

        # Team names
        df["home_team"] = df["HomeTeam"].astype(str).str.strip()
        df["away_team"] = df["AwayTeam"].astype(str).str.strip()

        # Match statistics
        for col in ["FTHG", "FTAG", "HTHG", "HTAG", "HS", "AS", "HST", "AST", 
                    "HC", "AC", "HF", "AF", "HY", "AY", "HR", "AR"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            else:
                df[col] = np.nan

        # Referee
        df["referee"] = df["Referee"].fillna("Unknown").astype(str).str.strip() if "Referee" in df.columns else "Unknown"

        # Odds Fallback Chains for consensus: Avg -> B365 -> BW -> PS (Max is excluded as it represents extreme pricing, not market consensus)
        odds_providers_open = ["Avg", "B365", "BW", "PS"]
        odds_providers_close = ["AvgC", "B365C", "BWC", "PSC"]

        # 1X2 Open Odds
        open_1x2_data = []
        close_1x2_data = []
        open_ou25_data = []
        close_ou25_data = []
        open_ah_data = []
        close_ah_data = []

        for idx, row in df.iterrows():
            # 1X2 Open: e.g. AvgH, AvgD, AvgA
            o_h, o_d, o_a, prov_o1x2 = self.extract_odds_chain(row, odds_providers_open, ["H", "D", "A"])
            open_1x2_data.append((o_h, o_d, o_a, prov_o1x2))

            # 1X2 Close: e.g. AvgCH, AvgCD, AvgCA
            c_providers = ["Avg", "B365", "BW", "PS"]
            c_h, c_d, c_a, prov_c1x2 = self.extract_odds_chain(row, c_providers, ["CH", "CD", "CA"])
            close_1x2_data.append((c_h, c_d, c_a, prov_c1x2))

            # O/U 2.5 Open: e.g. Avg>2.5, Avg<2.5, B365>2.5...
            ou_o, ou_u, prov_oou = self.extract_odds_chain(row, ["Avg", "B365", "P", "BFE"], [">2.5", "<2.5"])
            open_ou25_data.append((ou_o, ou_u, prov_oou))

            # O/U 2.5 Close: AvgC>2.5, AvgC<2.5, Avg C>2.5, B365C>2.5...
            c_ou_over = np.nan
            c_ou_under = np.nan
            prov_cou = "None"
            for p_prefix in ["AvgC", "Avg C", "B365C", "PC", "BFEC"]:
                ov_col = f"{p_prefix}>2.5"
                un_col = f"{p_prefix}<2.5"
                ov_val = pd.to_numeric(row.get(ov_col, np.nan), errors="coerce")
                un_val = pd.to_numeric(row.get(un_col, np.nan), errors="coerce")
                if pd.notna(ov_val) and pd.notna(un_val) and ov_val >= 1.01 and un_val >= 1.01:
                    c_ou_over = float(ov_val)
                    c_ou_under = float(un_val)
                    prov_cou = p_prefix.strip()
                    break
            close_ou25_data.append((c_ou_over, c_ou_under, prov_cou))

            # Asian Handicap Open: AHh + AvgAHH/AvgAHA or B365AHH/B365AHA
            line_open = pd.to_numeric(row.get("AHh", np.nan), errors="coerce")
            ah_h, ah_a, prov_oah = self.extract_odds_chain(row, ["Avg", "B365", "P", "BFE"], ["AHH", "AHA"])
            open_ah_data.append((line_open, ah_h, ah_a, prov_oah))

            # Asian Handicap Close: AHCh + AvgCAHH/AvgCAHA or B365CAHH/B365CAHA
            line_close = pd.to_numeric(row.get("AHCh", np.nan), errors="coerce")
            # If AHCh is missing, check AHh as fallback
            if pd.isna(line_close):
                line_close = line_open
            c_ah_h, c_ah_a, prov_cah = self.extract_odds_chain(row, ["AvgC", "Avg", "B365C", "PCAH", "BFECA"], ["AHH", "AHA"])
            # Also check direct columns like AvgCAHH / B365CAHH
            if pd.isna(c_ah_h):
                for p_ah in ["Avg", "B365", "BFE"]:
                    h_val = pd.to_numeric(row.get(f"{p_ah}CAHH", np.nan), errors="coerce")
                    a_val = pd.to_numeric(row.get(f"{p_ah}CAHA", np.nan), errors="coerce")
                    if pd.notna(h_val) and pd.notna(a_val) and h_val >= 1.01 and a_val >= 1.01:
                        c_ah_h = float(h_val)
                        c_ah_a = float(a_val)
                        prov_cah = f"{p_ah}C"
                        break
            close_ah_data.append((line_close, c_ah_h, c_ah_a, prov_cah))

        # Assign standardized columns
        df["ref_open_h"] = [x[0] for x in open_1x2_data]
        df["ref_open_d"] = [x[1] for x in open_1x2_data]
        df["ref_open_a"] = [x[2] for x in open_1x2_data]
        df["ref_open_1x2_prov"] = [x[3] for x in open_1x2_data]

        df["ref_close_h"] = [x[0] for x in close_1x2_data]
        df["ref_close_d"] = [x[1] for x in close_1x2_data]
        df["ref_close_a"] = [x[2] for x in close_1x2_data]
        df["ref_close_1x2_prov"] = [x[3] for x in close_1x2_data]

        df["ref_open_over25"] = [x[0] for x in open_ou25_data]
        df["ref_open_under25"] = [x[1] for x in open_ou25_data]
        df["ref_open_ou_prov"] = [x[2] for x in open_ou25_data]

        df["ref_close_over25"] = [x[0] for x in close_ou25_data]
        df["ref_close_under25"] = [x[1] for x in close_ou25_data]
        df["ref_close_ou_prov"] = [x[2] for x in close_ou25_data]

        df["ah_open_line"] = [x[0] for x in open_ah_data]
        df["ref_open_ahh"] = [x[1] for x in open_ah_data]
        df["ref_open_aha"] = [x[2] for x in open_ah_data]
        df["ref_open_ah_prov"] = [x[3] for x in open_ah_data]

        df["ah_close_line"] = [x[0] for x in close_ah_data]
        df["ref_close_ahh"] = [x[1] for x in close_ah_data]
        df["ref_close_aha"] = [x[2] for x in close_ah_data]
        df["ref_close_ah_prov"] = [x[3] for x in close_ah_data]

        # Calculate closing overround for 1X2 when available
        with np.errstate(divide="ignore", invalid="ignore"):
            df["overround_close_1x2"] = (1.0 / df["ref_close_h"]) + (1.0 / df["ref_close_d"]) + (1.0 / df["ref_close_a"])
            df["overround_open_1x2"] = (1.0 / df["ref_open_h"]) + (1.0 / df["ref_open_d"]) + (1.0 / df["ref_open_a"])

        df["source_file"] = source_file
        return df

    def load_all_leagues(self) -> pd.DataFrame:
        """Scan and load all 25 CSV files, validate and return consolidated clean dataframe."""
        file_patterns = list(self.data_league_dir.glob("*/*.csv"))
        if not file_patterns:
            file_patterns = list(self.data_league_dir.glob("*.csv"))

        logger.info(f"Discovered {len(file_patterns)} CSV files in {self.data_league_dir}")
        dfs = []

        for f_path in sorted(file_patterns):
            try:
                raw_df = self.load_single_csv(f_path)
                n_raw = len(raw_df)
                self.audit_log["files_processed"] += 1
                self.audit_log["total_raw_rows"] += n_raw

                # Clean & standardize
                std_df = self.standardize_dataframe(raw_df, str(f_path.name))

                # Validation checks per file
                dups = std_df.duplicated(subset=["Div", "match_date", "home_team", "away_team"]).sum()
                neg_scores = ((std_df["FTHG"] < 0) | (std_df["FTAG"] < 0)).sum()
                
                # Check for odds < 1.01
                odds_cols = ["ref_open_h", "ref_open_d", "ref_open_a", "ref_close_h", "ref_close_d", "ref_close_a"]
                invalid_odds = ((std_df[odds_cols] < 1.01) & std_df[odds_cols].notna()).any(axis=1).sum()

                self.audit_log["duplicate_rows_dropped"] += int(dups)
                self.audit_log["negative_scores_found"] += int(neg_scores)
                self.audit_log["invalid_odds_found"] += int(invalid_odds)

                self.audit_log["file_reports"].append({
                    "file": f_path.name,
                    "league": std_df["Div"].iloc[0] if len(std_df) > 0 else "Unknown",
                    "rows": n_raw,
                    "duplicates": int(dups),
                    "negative_scores": int(neg_scores),
                    "invalid_odds": int(invalid_odds),
                    "seasons": list(std_df["season"].unique()),
                })

                dfs.append(std_df)
            except Exception as e:
                logger.error(f"Error processing {f_path}: {e}")
                self.audit_log["file_reports"].append({
                    "file": f_path.name,
                    "error": str(e),
                })

        if not dfs:
            raise RuntimeError("No CSV files loaded successfully!")

        all_matches = pd.concat(dfs, ignore_index=True)

        # Drop exact duplicate matches
        before_dedup = len(all_matches)
        all_matches = all_matches.drop_duplicates(subset=["Div", "match_date", "home_team", "away_team"]).reset_index(drop=True)
        dropped_dedup = before_dedup - len(all_matches)

        # Sort chronologically
        all_matches = all_matches.sort_values(by=["match_date", "kickoff_time", "home_team"]).reset_index(drop=True)

        self.audit_log["clean_rows"] = len(all_matches)
        logger.info(f"Loaded {len(all_matches)} clean matches across {self.audit_log['files_processed']} files.")

        # Save to Parquet and save audit log
        output_dir = settings.BASE_DIR / "backend" / "data"
        output_dir.mkdir(parents=True, exist_ok=True)
        parquet_path = output_dir / "cleaned_matches.parquet"
        all_matches.to_parquet(parquet_path, index=False)
        
        audit_path = output_dir / "data_audit_log.json"
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(self.audit_log, f, indent=2)

        return all_matches
