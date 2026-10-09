from rapidfuzz import process, fuzz
from typing import Dict, Optional

# Standard canonical team names mapped from various aliases
MANUAL_ALIASES: Dict[str, str] = {
    # Premier League
    "man united": "Manchester United",
    "man utd": "Manchester United",
    "manchester utd": "Manchester United",
    "man city": "Manchester City",
    "tottenham": "Tottenham Hotspur",
    "spurs": "Tottenham Hotspur",
    "newcastle": "Newcastle United",
    "wolves": "Wolverhampton Wanderers",
    "wolverhampton": "Wolverhampton Wanderers",
    "nott'm forest": "Nottingham Forest",
    "nottingham": "Nottingham Forest",
    "brighton": "Brighton & Hove Albion",
    "brighton and hove albion": "Brighton & Hove Albion",
    "west ham": "West Ham United",
    "leicester": "Leicester City",
    "ipswich": "Ipswich Town",
    "southampton": "Southampton FC",

    # La Liga
    "ath bilbao": "Athletic Bilbao",
    "athletic club": "Athletic Bilbao",
    "atl madrid": "Atletico Madrid",
    "atlético madrid": "Atletico Madrid",
    "celta": "Celta Vigo",
    "celta de vigo": "Celta Vigo",
    "betis": "Real Betis",
    "sociedad": "Real Sociedad",
    "rayo": "Rayo Vallecano",
    "alaves": "Deportivo Alaves",
    "deportivo alavés": "Deportivo Alaves",
    "espanol": "Espanyol",
    "rce espanyol": "Espanyol",

    # Serie A
    "inter": "Inter Milan",
    "internazionale": "Inter Milan",
    "ac milan": "AC Milan",
    "milan": "AC Milan",
    "verona": "Hellas Verona",
    "hellas": "Hellas Verona",
    "roma": "AS Roma",

    # Bundesliga
    "bayern munich": "Bayern Munich",
    "bayern münchen": "Bayern Munich",
    "leverkusen": "Bayer Leverkusen",
    "bayer 04 leverkusen": "Bayer Leverkusen",
    "dortmund": "Borussia Dortmund",
    "bvb": "Borussia Dortmund",
    "m'gladbach": "Borussia Monchengladbach",
    "borussia mönchengladbach": "Borussia Monchengladbach",
    "frankfurt": "Eintracht Frankfurt",
    "rb leipzig": "RB Leipzig",

    # Ligue 1
    "psg": "Paris Saint-Germain",
    "paris sg": "Paris Saint-Germain",
    "paris saint germain": "Paris Saint-Germain",
    "marseille": "Olympique Marseille",
    "lyon": "Olympique Lyonnais",
    "saint-etienne": "Saint-Etienne",
    "st etienne": "Saint-Etienne",
}


def normalize_team_name(name: str, known_canonical_teams: Optional[list] = None) -> str:
    """Normalize team name using alias dictionary and rapidfuzz fallback."""
    if not name:
        return ""
    clean = name.strip()
    lower = clean.lower()

    if lower in MANUAL_ALIASES:
        return MANUAL_ALIASES[lower]

    if known_canonical_teams:
        match = process.extractOne(
            clean,
            known_canonical_teams,
            scorer=fuzz.token_sort_ratio,
            score_cutoff=85
        )
        if match:
            return match[0]

    return clean
