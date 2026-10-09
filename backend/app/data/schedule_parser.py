"""
Schedule Parser for Lich_Thi_Dau TXT files.

Handles 5 different fixture schedule formats:
- Premier League / La Liga / Championship / Serie A: Vietnamese day-date headers
  with venue/team/time/team blocks
- Bundesliga: Mixed tab-delimited table format + vertical block format

All output is a standardized DataFrame with columns:
  Div, HomeTeam, AwayTeam, Date, Time, match_date, kickoff_time, home_team, away_team,
  home_team_display, away_team_display, season, round_number
"""
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Map league TXT filename to football-data.co.uk Div code
LEAGUE_FILE_TO_DIV = {
    "Premier League": "E0",
    "Championship": "E1",
    "La Liga": "SP1",
    "Serie A": "I1",
    "Bundesliga": "D1",
}

# Canonical team name mapping to match historical football-data.co.uk CSVs
# Crucial requirement: Championship team named 'Bundesliga' is actually 'Birmingham'
LEAGUE_TEAM_MAP: Dict[str, Dict[str, str]] = {
    "E0": {
        "Hull City": "Hull",
        "Man Utd": "Man United",
        "Nottingham Forest": "Nott'm Forest",
    },
    "E1": {
        # User requirement: "Lưu ý đội tên Bundesliga ở giải hạng Nhất Anh Championship tên thật là Birmingham nhé"
        "Bundesliga": "Birmingham",
        "Blackburn Rovers": "Blackburn",
        "Bolton Wanderers": "Bolton",
        "Cardiff City": "Cardiff",
        "Charlton Athletic": "Charlton",
        "Derby County": "Derby",
        "Lincoln City": "Lincoln",
        "Norwich City": "Norwich",
        "Preston North": "Preston",
        "Stoke City": "Stoke",
        "Swansea City": "Swansea",
        "Wolverhampton": "Wolves",
    },
    "SP1": {
        "Athletic Club": "Ath Bilbao",
        "Atletico": "Ath Madrid",
        "Barca": "Barcelona",
        "Celta Vigo": "Celta",
        "Deportivo La Coruna": "La Coruna",
        "Espanyol": "Espanol",
        "Racing Santander": "Santander",
        "Rayo Vallecano": "Vallecano",
        "Real Betis": "Betis",
    },
    "I1": {
        "AS Roma": "Roma",
    },
    "D1": {
        "B. Monchengladbach": "M'gladbach",
        "Borussia M'gladbach": "M'gladbach",
        "Borussia Mönchengladbach": "M'gladbach",
        "Borussia Mnchengladbach": "M'gladbach",
        "Bayer Leverkusen": "Leverkusen",
        "Borussia Dortmund": "Dortmund",
        "Cologne": "FC Koln",
        "FC Köln": "FC Koln",
        "FC Koln": "FC Koln",
        "FC Kln": "FC Koln",
        "Eintracht Frankfurt": "Ein Frankfurt",
        "Frankfurt": "Ein Frankfurt",
        "FC Augsburg": "Augsburg",
        "FC Schalke 04": "Schalke 04",
        "Schalke": "Schalke 04",
        "FSV Mainz 05": "Mainz",
        "Hamburger": "Hamburg",
        "Hamburger SV": "Hamburg",
        "SC Freiburg": "Freiburg",
        "SC Paderborn 07": "Paderborn",
        "SV Elversberg": "Elversberg",
        "TSG Hoffenheim": "Hoffenheim",
        "VfB Stuttgart": "Stuttgart",
    },
}

# Display friendly names
CANONICAL_TO_DISPLAY: Dict[str, str] = {
    "Nott'm Forest": "Nottingham Forest",
    "Man United": "Manchester United",
    "Man City": "Manchester City",
    "Ath Bilbao": "Athletic Bilbao",
    "Ath Madrid": "Atletico Madrid",
    "Espanol": "Espanyol",
    "Vallecano": "Rayo Vallecano",
    "Betis": "Real Betis",
    "Ein Frankfurt": "Eintracht Frankfurt",
    "M'gladbach": "Borussia M'gladbach",
    "FC Koln": "FC Köln",
    "Schalke 04": "Schalke 04",
    "Roma": "AS Roma",
    "Wolves": "Wolverhampton",
}

# Vietnamese day names to detect date header lines
VN_DAYS = [
    "thứ hai", "thứ ba", "thứ tư", "thứ năm", "thứ sáu",
    "thứ bảy", "chủ nhật",
]

# Time pattern HH:MM
TIME_RE = re.compile(r"^\d{1,2}:\d{2}$")

# Bundesliga tab-delimited match line: "10/10 - 20:30\tTeamA\tvs\tTeamB"
BULI_TAB_RE = re.compile(r"^(\d{1,2}/\d{1,2})\s*-\s*(\d{1,2}:\d{2})\t(.+?)\tvs\t(.+?)$")
# Bundesliga tab-delimited match with full date: "19/12 - 20/12/2026\tTeamA\tvs\tTeamB"
BULI_RANGE_RE = re.compile(r"^(\d{1,2}/\d{1,2})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})")
# Bundesliga date-only line: "05/12/2026"
BULI_DATE_ONLY_RE = re.compile(r"^(\d{1,2}/\d{1,2}/\d{4})$")
# Round header
ROUND_RE = re.compile(r"vòng\s+(\d+)", re.IGNORECASE)


def _is_date_header(line: str) -> bool:
    """Check if line is a Vietnamese date header like 'Thứ bảy, 10/10/2026' or 'Thứ Bảy, 10 tháng 10'."""
    lower = line.lower().strip()
    return any(lower.startswith(d) for d in VN_DAYS)


def _is_round_header(line: str) -> bool:
    """Check if line is a round header like 'Vòng 6' or 'Vòng 5 (10/10 – 11/10/2026)'."""
    lower = line.lower().strip()
    return lower.startswith("vòng ")


def _is_venue_line(line: str) -> bool:
    """Heuristic: venue lines typically contain stadium names with commas or stadium keywords."""
    lower = line.lower().strip()
    venue_keywords = [
        "stadium", "park", "road", "bridge", "lane", "field", "ground",
        "arena", "etihad", "anfield", "emirates", "old trafford",
        "amex", "selhurst", "portman", "craven", "elland",
        "vitality", "mkm", "hill dickinson", "coventry building", "sân vận động"
    ]
    if any(kw in lower for kw in venue_keywords):
        return True
    return False


def _is_table_header(line: str) -> bool:
    """Bundesliga table header: 'Thời gian thi đấu\tĐội nhà\tTỷ số\tĐội khách'."""
    lower = line.lower().strip()
    return "thời gian" in lower or "đội nhà" in lower or "tỷ số" in lower


def _is_skip_line(line: str) -> bool:
    """Lines to skip: 'vs', 'Tỷ số', 'Đội nhà', 'Đội khách', empty, or section headers."""
    stripped = line.strip()
    if not stripped:
        return True
    lower = stripped.lower()
    skip_tokens = [
        "vs", "tỷ số", "đội nhà", "đội khách", "thời gian thi đấu",
        "giai đoạn", "lượt về", "hạ màn"
    ]
    return lower in skip_tokens or any(lower.startswith(s) for s in ["giai đoạn"])


def _parse_vn_date(line: str, default_year: int = 2026) -> Optional[str]:
    """
    Parse Vietnamese date header and return ISO date string (YYYY-MM-DD).
    Handles:
    - 'Thứ bảy, 10/10/2026' -> '2026-10-10'
    - 'Thứ Bảy, 10 tháng 10' -> '2026-10-10'
    - 'Thứ bảy 10/10/2026' -> '2026-10-10'
    - 'Thứ Bảy, 17 tháng 1' -> '2027-01-17'
    """
    line = line.strip().rstrip(",").strip()

    # 1. Try dd/mm/yyyy
    m_full = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", line)
    if m_full:
        day, month, year = int(m_full.group(1)), int(m_full.group(2)), int(m_full.group(3))
        return f"{year}-{month:02d}-{day:02d}"

    # 2. Try Vietnamese "DD tháng MM" format e.g. "10 tháng 10", "17 tháng 1"
    m_thang = re.search(r"(\d{1,2})\s*th[aá]ng\s*(\d{1,2})", line, re.IGNORECASE)
    if m_thang:
        day = int(m_thang.group(1))
        month = int(m_thang.group(2))
        year = default_year if month >= 7 else default_year + 1
        return f"{year}-{month:02d}-{day:02d}"

    # 3. Try dd/mm (no year)
    m_slash = re.search(r"(\d{1,2})/(\d{1,2})", line)
    if m_slash:
        day, month = int(m_slash.group(1)), int(m_slash.group(2))
        year = default_year if month >= 7 else default_year + 1
        return f"{year}-{month:02d}-{day:02d}"

    return None


def _normalize_team_for_div(team_name: str, div: str) -> Tuple[str, str]:
    """
    Normalize team name to football-data standard canonical name and display name.
    Handles Championship 'Bundesliga' -> 'Birmingham'.
    """
    cleaned = team_name.strip()
    div_map = LEAGUE_TEAM_MAP.get(div, {})
    canonical = div_map.get(cleaned, cleaned)
    display = CANONICAL_TO_DISPLAY.get(canonical, cleaned if cleaned != "Bundesliga" else "Birmingham")
    return canonical, display


def parse_premier_league_format(lines: List[str], div: str, default_year: int = 2026) -> List[Dict[str, Any]]:
    """
    Parse PL/La Liga/Championship/Serie A format:
    Date header -> [Venue] -> HomeTeam (x2) -> Time -> AwayTeam (x2) -> repeat
    """
    fixtures = []
    current_date = None
    current_round = None
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Skip empty / metadata lines
        if not line or _is_table_header(line) or _is_skip_line(line):
            i += 1
            continue

        # Date header
        if _is_date_header(line):
            parsed = _parse_vn_date(line, default_year)
            if parsed:
                current_date = parsed
            i += 1
            continue

        # Round header
        if _is_round_header(line):
            rm = ROUND_RE.search(line)
            if rm:
                current_round = int(rm.group(1))
            i += 1
            continue

        # Venue line (skip it)
        if _is_venue_line(line):
            i += 1
            continue

        # Match block: HomeTeam, HomeTeam, Time, AwayTeam, AwayTeam
        if current_date and not TIME_RE.match(line) and not _is_date_header(line):
            home_team_raw = line
            j = i + 1

            # Skip duplicate team name line
            while j < len(lines) and lines[j].strip() == home_team_raw:
                j += 1

            # Look for time
            if j < len(lines) and TIME_RE.match(lines[j].strip()):
                kickoff = lines[j].strip()
                j += 1

                # Get away team
                if j < len(lines) and lines[j].strip():
                    away_team_raw = lines[j].strip()
                    j += 1

                    # Skip duplicate away team name
                    while j < len(lines) and lines[j].strip() == away_team_raw:
                        j += 1

                    h_canon, h_disp = _normalize_team_for_div(home_team_raw, div)
                    a_canon, a_disp = _normalize_team_for_div(away_team_raw, div)

                    fixtures.append({
                        "Div": div,
                        "HomeTeam": h_canon,
                        "AwayTeam": a_canon,
                        "home_team": h_canon,
                        "away_team": a_canon,
                        "home_team_display": h_disp,
                        "away_team_display": a_disp,
                        "Date": current_date,
                        "Time": kickoff,
                        "round_number": current_round,
                    })
                    i = j
                    continue
                else:
                    i = j
                    continue
            else:
                i += 1
                continue
        else:
            i += 1
            continue

    return fixtures


def parse_bundesliga_format(lines: List[str], div: str = "D1", default_year: int = 2026) -> List[Dict[str, Any]]:
    """
    Parse Bundesliga format which has multiple sub-formats:
    1. Tab-delimited: "10/10 - 20:30\tTeamA\tvs\tTeamB"
    2. Vertical block (Vòng 12+): Date line, empty, Time, empty, HomeTeam, empty, vs, empty, AwayTeam
    3. Range date format: "19/12 - 20/12/2026\tTeamA\tvs\tTeamB"
    """
    fixtures = []
    current_round = None
    current_date_str = None
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Skip empties
        if not line or _is_skip_line(line) or _is_table_header(line):
            i += 1
            continue

        # Round header
        if _is_round_header(line):
            rm = ROUND_RE.search(line)
            if rm:
                current_round = int(rm.group(1))
            # Try to extract date from round header like "Vòng 5 (10/10 – 11/10/2026)"
            date_m = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", line)
            if date_m:
                d, m_val, y = date_m.group(1).split("/")
                current_date_str = f"{y}-{int(m_val):02d}-{int(d):02d}"
            i += 1
            continue

        # Tab-delimited match line: "10/10 - 20:30\tTeamA\tvs\tTeamB"
        tab_m = BULI_TAB_RE.match(line)
        if tab_m:
            date_part = tab_m.group(1)
            time_part = tab_m.group(2)
            home_raw = tab_m.group(3).strip()
            away_raw = tab_m.group(4).strip()

            dd, mm = date_part.split("/")
            year = default_year if int(mm) >= 7 else default_year + 1
            date_iso = f"{year}-{int(mm):02d}-{int(dd):02d}"

            h_canon, h_disp = _normalize_team_for_div(home_raw, div)
            a_canon, a_disp = _normalize_team_for_div(away_raw, div)

            fixtures.append({
                "Div": div,
                "HomeTeam": h_canon,
                "AwayTeam": a_canon,
                "home_team": h_canon,
                "away_team": a_canon,
                "home_team_display": h_disp,
                "away_team_display": a_disp,
                "Date": date_iso,
                "Time": time_part,
                "round_number": current_round,
            })
            i += 1
            continue

        # Range date format: "19/12 - 20/12/2026\tTeamA\tvs\tTeamB"
        range_m = BULI_RANGE_RE.match(line)
        if range_m:
            date_m = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", line)
            if date_m:
                d, m_val, y = date_m.group(1).split("/")
                current_date_str = f"{y}-{int(m_val):02d}-{int(d):02d}"

            parts = line.split("\t")
            if len(parts) >= 4 and "vs" in parts[2].lower():
                home_raw = parts[1].strip()
                away_raw = parts[3].strip()
                h_canon, h_disp = _normalize_team_for_div(home_raw, div)
                a_canon, a_disp = _normalize_team_for_div(away_raw, div)

                fixtures.append({
                    "Div": div,
                    "HomeTeam": h_canon,
                    "AwayTeam": a_canon,
                    "home_team": h_canon,
                    "away_team": a_canon,
                    "home_team_display": h_disp,
                    "away_team_display": a_disp,
                    "Date": current_date_str or f"{default_year}-01-01",
                    "Time": "20:30",
                    "round_number": current_round,
                })
            i += 1
            continue

        # Full date line: "05/12/2026"
        date_only_m = BULI_DATE_ONLY_RE.match(line)
        if date_only_m:
            d, m_val, y = date_only_m.group(1).split("/")
            current_date_str = f"{y}-{int(m_val):02d}-{int(d):02d}"
            i += 1
            continue

        # Bundesliga Hạ Màn format: "22/05/2027 - 20:30\tTeamA\tvs\tTeamB"
        full_date_tab_m = re.match(r"(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}:\d{2})\t(.+?)\tvs\t(.+?)$", line)
        if full_date_tab_m:
            d, m_val, y = full_date_tab_m.group(1).split("/")
            date_iso = f"{y}-{int(m_val):02d}-{int(d):02d}"
            home_raw = full_date_tab_m.group(3).strip()
            away_raw = full_date_tab_m.group(4).strip()
            h_canon, h_disp = _normalize_team_for_div(home_raw, div)
            a_canon, a_disp = _normalize_team_for_div(away_raw, div)

            fixtures.append({
                "Div": div,
                "HomeTeam": h_canon,
                "AwayTeam": a_canon,
                "home_team": h_canon,
                "away_team": a_canon,
                "home_team_display": h_disp,
                "away_team_display": a_disp,
                "Date": date_iso,
                "Time": full_date_tab_m.group(2),
                "round_number": current_round,
            })
            i += 1
            continue

        # Vertical block format: look for Time line, then HomeTeam, vs, AwayTeam
        if TIME_RE.match(line):
            kickoff = line
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                home_raw = lines[j].strip()
                j += 1
                while j < len(lines) and (not lines[j].strip() or lines[j].strip().lower() == "vs"):
                    j += 1
                if j < len(lines):
                    away_raw = lines[j].strip()
                    j += 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1

                    h_canon, h_disp = _normalize_team_for_div(home_raw, div)
                    a_canon, a_disp = _normalize_team_for_div(away_raw, div)

                    fixtures.append({
                        "Div": div,
                        "HomeTeam": h_canon,
                        "AwayTeam": a_canon,
                        "home_team": h_canon,
                        "away_team": a_canon,
                        "home_team_display": h_disp,
                        "away_team_display": a_disp,
                        "Date": current_date_str or f"{default_year}-01-01",
                        "Time": kickoff,
                        "round_number": current_round,
                    })
                    i = j
                    continue

        i += 1

    return fixtures


def _infer_season(date_str: str) -> str:
    """Infer season from ISO date string (July year N to June year N+1 is N/(N+1))."""
    try:
        dt = pd.Timestamp(date_str)
        year = dt.year
        month = dt.month
        if month >= 7:
            return f"{year}/{(year + 1) % 100:02d}"
        else:
            return f"{year - 1}/{year % 100:02d}"
    except Exception:
        return "2026/27"


def parse_schedule_file(file_path: Path, default_year: int = 2026) -> pd.DataFrame:
    """
    Parse a single schedule TXT file and return standardized DataFrame.
    Auto-detects format based on filename/content.
    """
    league_name = file_path.stem
    div = LEAGUE_FILE_TO_DIV.get(league_name, "Unknown")

    with open(file_path, "r", encoding="utf-8-sig") as f:
        raw_text = f.read()

    lines = raw_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    if league_name == "Bundesliga":
        fixtures = parse_bundesliga_format(lines, div=div, default_year=default_year)
    else:
        fixtures = parse_premier_league_format(lines, div=div, default_year=default_year)

    if not fixtures:
        logger.warning(f"No fixtures parsed from {file_path}")
        return pd.DataFrame()

    df = pd.DataFrame(fixtures)

    # Standardize column names for compatibility with UpcomingFixturesClient
    df["match_date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["kickoff_time"] = df["Time"].fillna("15:00")
    df["home_team"] = df["HomeTeam"].astype(str).str.strip()
    df["away_team"] = df["AwayTeam"].astype(str).str.strip()
    df["season"] = df["Date"].apply(_infer_season)

    # Mark as unplayed
    df["FTHG"] = np.nan
    df["FTAG"] = np.nan
    df["FTR"] = np.nan

    # Empty odds columns (fixtures don't have odds yet)
    for col in [
        "HS", "AS", "HST", "AST", "HC", "AC", "HF", "AF", "HY", "AY", "HR", "AR",
        "ref_open_h", "ref_open_d", "ref_open_a", "ref_close_h", "ref_close_d", "ref_close_a",
        "ref_open_over25", "ref_open_under25", "ref_close_over25", "ref_close_under25",
        "ah_open_line", "ref_open_ahh", "ref_open_aha",
        "ah_close_line", "ref_close_ahh", "ref_close_aha"
    ]:
        df[col] = np.nan

    df["referee"] = "Unknown"
    df["source_file"] = f"Lich_Thi_Dau/{league_name}.txt"

    logger.info(f"Parsed {len(df)} fixtures from {file_path.name}")
    return df


def load_all_schedules(schedule_dir: Optional[Path] = None, default_year: int = 2026) -> pd.DataFrame:
    """
    Load and parse all schedule TXT files from the Lich_Thi_Dau directory.
    Returns a consolidated DataFrame of all upcoming fixtures across leagues.
    """
    if schedule_dir is None:
        from backend.app.core.config import settings
        schedule_dir = settings.BASE_DIR / "Lich_Thi_Dau"

    if not schedule_dir.exists():
        logger.warning(f"Schedule directory not found: {schedule_dir}")
        return pd.DataFrame()

    txt_files = list(schedule_dir.glob("*.txt"))
    if not txt_files:
        logger.warning(f"No .txt files found in {schedule_dir}")
        return pd.DataFrame()

    dfs = []
    for f in sorted(txt_files):
        try:
            df = parse_schedule_file(f, default_year=default_year)
            if not df.empty:
                dfs.append(df)
        except Exception as e:
            logger.error(f"Error parsing {f.name}: {e}")

    if not dfs:
        return pd.DataFrame()

    combined = pd.concat(dfs, ignore_index=True)
    combined = combined.drop_duplicates(
        subset=["Div", "match_date", "home_team", "away_team"]
    ).reset_index(drop=True)
    combined = combined.sort_values(
        by=["match_date", "kickoff_time", "home_team"]
    ).reset_index(drop=True)

    logger.info(f"Total schedule fixtures loaded: {len(combined)} across {len(dfs)} leagues")
    return combined
