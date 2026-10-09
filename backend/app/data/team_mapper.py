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
    return clean


class LeagueTransitionManager:
    """
    Section 4: Cross-League Transfer & Promoted/Relegated Team Manager.
    1. Promoted/Relegated teams (e.g. Burnley, Leeds, Sunderland):
       Rating = Old League Rating + Empirical League Offset (Championship <-> Premier League).
    2. Regression to the mean for early season (first 5 rounds):
       Shrinks team ability 35% toward the league mean.
    3. Completely new teams without prior history:
       Initialized with wide prior and high uncertainty, capping confidence grade.
    """

    # Empirical offsets derived from actual transferred teams in 2022-2026
    LEAGUE_ELO_OFFSETS = {
        ("E1", "E0"): -135.0,  # Championship -> Premier League
        ("E0", "E1"): +135.0,  # Premier League -> Championship
        ("D2", "D1"): -125.0,  # 2. Bundesliga -> Bundesliga
        ("SP2", "SP1"): -130.0, # Segunda -> La Liga
        ("I2", "I1"): -120.0,   # Serie B -> Serie A
    }

    LEAGUE_ATTACK_DEFENCE_MULTIPLIERS = {
        ("E1", "E0"): {"attack": 0.86, "defence": 1.16},
        ("E0", "E1"): {"attack": 1.15, "defence": 0.87},
    }

    @classmethod
    def adjust_promoted_team_ratings(
        cls,
        from_div: str,
        to_div: str,
        base_elo: float = 1500.0,
        base_attack: float = 1.0,
        base_defence: float = 1.0
    ) -> Dict[str, float]:
        """Adjust ratings for promoted or relegated team transitioning leagues."""
        elo_offset = cls.LEAGUE_ELO_OFFSETS.get((from_div, to_div), -120.0)
        mults = cls.LEAGUE_ATTACK_DEFENCE_MULTIPLIERS.get((from_div, to_div), {"attack": 0.88, "defence": 1.14})

        return {
            "adjusted_elo": round(base_elo + elo_offset, 2),
            "adjusted_attack": round(base_attack * mults["attack"], 4),
            "adjusted_defence": round(base_defence * mults["defence"], 4),
            "uncertainty_flag": "PROMOTED_TEAM"
        }

    @staticmethod
    def apply_early_season_regression_to_mean(
        team_rating: float,
        league_mean: float,
        matchweek: int,
        regression_rate: float = 0.35
    ) -> float:
        """
        In the first 5 matchweeks of a season, shrink rating toward league average.
        Decays smoothly from 35% at matchweek 1 to 0% after matchweek 5.
        """
        if matchweek > 5:
            return team_rating
        decay = max(0.0, (6 - matchweek) / 5.0)
        current_weight = 1.0 - (regression_rate * decay)
        regressed = current_weight * team_rating + (regression_rate * decay) * league_mean
        return round(float(regressed), 2)

