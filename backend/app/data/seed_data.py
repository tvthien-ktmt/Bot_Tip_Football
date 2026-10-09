import datetime
import json
import random
from sqlalchemy.orm import Session
from backend.app.models.entities import (
    League, Season, Team, TeamAlias, Match, OddsSnapshot, Rating
)
from backend.app.core.database import SessionLocal, Base, engine


SEEDED_LEAGUES = [
    {"code": "E0", "name": "Premier League", "country": "England"},
    {"code": "SP1", "name": "La Liga", "country": "Spain"},
    {"code": "I1", "name": "Serie A", "country": "Italy"},
    {"code": "D1", "name": "Bundesliga", "country": "Germany"},
    {"code": "F1", "name": "Ligue 1", "country": "France"},
]

TEAMS_BY_LEAGUE = {
    "E0": [
        {"name": "Arsenal", "short_name": "ARS", "code": "ARS", "elo": 1820.0, "pi_h": 0.85, "pi_a": 0.65, "atk": 1.45, "defn": 0.75, "c_atk": 6.8, "c_def": 4.1},
        {"name": "Manchester City", "short_name": "MCI", "code": "MCI", "elo": 1870.0, "pi_h": 0.95, "pi_a": 0.80, "atk": 1.60, "defn": 0.70, "c_atk": 7.5, "c_def": 3.5},
        {"name": "Liverpool", "short_name": "LIV", "code": "LIV", "elo": 1845.0, "pi_h": 0.90, "pi_a": 0.72, "atk": 1.55, "defn": 0.78, "c_atk": 7.1, "c_def": 3.8},
        {"name": "Chelsea", "short_name": "CHE", "code": "CHE", "elo": 1720.0, "pi_h": 0.55, "pi_a": 0.40, "atk": 1.30, "defn": 0.95, "c_atk": 5.9, "c_def": 4.8},
        {"name": "Tottenham Hotspur", "short_name": "TOT", "code": "TOT", "elo": 1690.0, "pi_h": 0.45, "pi_a": 0.35, "atk": 1.25, "defn": 1.05, "c_atk": 5.8, "c_def": 5.2},
        {"name": "Manchester United", "short_name": "MUN", "code": "MUN", "elo": 1675.0, "pi_h": 0.40, "pi_a": 0.30, "atk": 1.15, "defn": 1.05, "c_atk": 5.4, "c_def": 5.1},
        {"name": "Newcastle United", "short_name": "NEW", "code": "NEW", "elo": 1680.0, "pi_h": 0.45, "pi_a": 0.32, "atk": 1.20, "defn": 1.00, "c_atk": 5.7, "c_def": 4.9},
        {"name": "Aston Villa", "short_name": "AVL", "code": "AVL", "elo": 1710.0, "pi_h": 0.52, "pi_a": 0.38, "atk": 1.28, "defn": 0.98, "c_atk": 5.5, "c_def": 4.7},
        {"name": "Brighton & Hove Albion", "short_name": "BHA", "code": "BHA", "elo": 1650.0, "pi_h": 0.35, "pi_a": 0.25, "atk": 1.18, "defn": 1.10, "c_atk": 5.2, "c_def": 5.0},
        {"name": "Fulham", "short_name": "FUL", "code": "FUL", "elo": 1580.0, "pi_h": 0.15, "pi_a": 0.05, "atk": 1.00, "defn": 1.15, "c_atk": 4.8, "c_def": 5.3},
        {"name": "Brentford", "short_name": "BRE", "code": "BRE", "elo": 1590.0, "pi_h": 0.18, "pi_a": 0.08, "atk": 1.08, "defn": 1.18, "c_atk": 4.9, "c_def": 5.5},
        {"name": "West Ham United", "short_name": "WHU", "code": "WHU", "elo": 1560.0, "pi_h": 0.10, "pi_a": -0.02, "atk": 0.95, "defn": 1.22, "c_atk": 4.5, "c_def": 5.6},
        {"name": "Bournemouth", "short_name": "BOU", "code": "BOU", "elo": 1575.0, "pi_h": 0.12, "pi_a": 0.02, "atk": 1.02, "defn": 1.16, "c_atk": 5.1, "c_def": 5.2},
        {"name": "Crystal Palace", "short_name": "CRY", "code": "CRY", "elo": 1565.0, "pi_h": 0.10, "pi_a": 0.00, "atk": 0.92, "defn": 1.12, "c_atk": 4.6, "c_def": 5.0},
        {"name": "Wolverhampton Wanderers", "short_name": "WOL", "code": "WOL", "elo": 1520.0, "pi_h": 0.00, "pi_a": -0.12, "atk": 0.88, "defn": 1.30, "c_atk": 4.2, "c_def": 5.8},
        {"name": "Everton", "short_name": "EVE", "code": "EVE", "elo": 1530.0, "pi_h": 0.02, "pi_a": -0.10, "atk": 0.85, "defn": 1.25, "c_atk": 4.3, "c_def": 5.7},
        {"name": "Nottingham Forest", "short_name": "NFO", "code": "NFO", "elo": 1620.0, "pi_h": 0.28, "pi_a": 0.18, "atk": 1.05, "defn": 1.02, "c_atk": 4.7, "c_def": 4.9},
        {"name": "Leicester City", "short_name": "LEI", "code": "LEI", "elo": 1470.0, "pi_h": -0.15, "pi_a": -0.25, "atk": 0.80, "defn": 1.40, "c_atk": 3.9, "c_def": 6.2},
        {"name": "Ipswich Town", "short_name": "IPS", "code": "IPS", "elo": 1450.0, "pi_h": -0.20, "pi_a": -0.30, "atk": 0.78, "defn": 1.45, "c_atk": 3.8, "c_def": 6.5},
        {"name": "Southampton FC", "short_name": "SOU", "code": "SOU", "elo": 1430.0, "pi_h": -0.25, "pi_a": -0.35, "atk": 0.72, "defn": 1.50, "c_atk": 3.6, "c_def": 6.8},
    ],
    "SP1": [
        {"name": "Real Madrid", "short_name": "RMA", "code": "RMA", "elo": 1860.0, "pi_h": 0.92, "pi_a": 0.78, "atk": 1.58, "defn": 0.72, "c_atk": 6.9, "c_def": 3.6},
        {"name": "Barcelona", "short_name": "BAR", "code": "BAR", "elo": 1850.0, "pi_h": 0.90, "pi_a": 0.75, "atk": 1.62, "defn": 0.75, "c_atk": 7.0, "c_def": 3.5},
        {"name": "Atletico Madrid", "short_name": "ATM", "code": "ATM", "elo": 1780.0, "pi_h": 0.72, "pi_a": 0.55, "atk": 1.35, "defn": 0.70, "c_atk": 5.8, "c_def": 3.9},
        {"name": "Athletic Bilbao", "short_name": "ATH", "code": "ATH", "elo": 1690.0, "pi_h": 0.48, "pi_a": 0.32, "atk": 1.20, "defn": 0.92, "c_atk": 5.5, "c_def": 4.5},
        {"name": "Real Sociedad", "short_name": "RSO", "code": "RSO", "elo": 1660.0, "pi_h": 0.38, "pi_a": 0.25, "atk": 1.10, "defn": 0.95, "c_atk": 5.2, "c_def": 4.7},
        {"name": "Villarreal", "short_name": "VIL", "code": "VIL", "elo": 1675.0, "pi_h": 0.42, "pi_a": 0.28, "atk": 1.30, "defn": 1.05, "c_atk": 5.4, "c_def": 5.0},
        {"name": "Real Betis", "short_name": "BET", "code": "BET", "elo": 1640.0, "pi_h": 0.32, "pi_a": 0.20, "atk": 1.08, "defn": 1.02, "c_atk": 5.0, "c_def": 4.8},
        {"name": "Sevilla", "short_name": "SEV", "code": "SEV", "elo": 1600.0, "pi_h": 0.20, "pi_a": 0.08, "atk": 1.00, "defn": 1.15, "c_atk": 4.8, "c_def": 5.2},
    ],
    "I1": [
        {"name": "Inter Milan", "short_name": "INT", "code": "INT", "elo": 1840.0, "pi_h": 0.88, "pi_a": 0.72, "atk": 1.52, "defn": 0.70, "c_atk": 6.8, "c_def": 3.8},
        {"name": "Juventus", "short_name": "JUV", "code": "JUV", "elo": 1760.0, "pi_h": 0.65, "pi_a": 0.50, "atk": 1.25, "defn": 0.68, "c_atk": 5.5, "c_def": 3.9},
        {"name": "Napoli", "short_name": "NAP", "code": "NAP", "elo": 1780.0, "pi_h": 0.70, "pi_a": 0.54, "atk": 1.38, "defn": 0.75, "c_atk": 6.0, "c_def": 4.2},
        {"name": "AC Milan", "short_name": "MIL", "code": "MIL", "elo": 1740.0, "pi_h": 0.60, "pi_a": 0.45, "atk": 1.35, "defn": 0.90, "c_atk": 5.8, "c_def": 4.6},
        {"name": "Atalanta", "short_name": "ATA", "code": "ATA", "elo": 1750.0, "pi_h": 0.62, "pi_a": 0.48, "atk": 1.45, "defn": 0.95, "c_atk": 6.2, "c_def": 4.5},
        {"name": "AS Roma", "short_name": "ROM", "code": "ROM", "elo": 1680.0, "pi_h": 0.42, "pi_a": 0.28, "atk": 1.15, "defn": 1.00, "c_atk": 5.3, "c_def": 4.8},
        {"name": "Lazio", "short_name": "LAZ", "code": "LAZ", "elo": 1690.0, "pi_h": 0.45, "pi_a": 0.30, "atk": 1.20, "defn": 0.98, "c_atk": 5.4, "c_def": 4.7},
    ],
    "D1": [
        {"name": "Bayern Munich", "short_name": "BAY", "code": "BAY", "elo": 1860.0, "pi_h": 0.94, "pi_a": 0.76, "atk": 1.70, "defn": 0.75, "c_atk": 7.8, "c_def": 3.5},
        {"name": "Bayer Leverkusen", "short_name": "B04", "code": "B04", "elo": 1810.0, "pi_h": 0.80, "pi_a": 0.65, "atk": 1.55, "defn": 0.82, "c_atk": 7.2, "c_def": 3.9},
        {"name": "Borussia Dortmund", "short_name": "BVB", "code": "BVB", "elo": 1730.0, "pi_h": 0.58, "pi_a": 0.40, "atk": 1.40, "defn": 1.02, "c_atk": 6.0, "c_def": 4.8},
        {"name": "RB Leipzig", "short_name": "RBL", "code": "RBL", "elo": 1740.0, "pi_h": 0.60, "pi_a": 0.42, "atk": 1.38, "defn": 0.92, "c_atk": 5.9, "c_def": 4.6},
        {"name": "Eintracht Frankfurt", "short_name": "SGE", "code": "SGE", "elo": 1680.0, "pi_h": 0.42, "pi_a": 0.26, "atk": 1.25, "defn": 1.10, "c_atk": 5.3, "c_def": 5.1},
        {"name": "VfB Stuttgart", "short_name": "VFB", "code": "VFB", "elo": 1670.0, "pi_h": 0.40, "pi_a": 0.25, "atk": 1.30, "defn": 1.15, "c_atk": 5.5, "c_def": 5.0},
    ],
    "F1": [
        {"name": "Paris Saint-Germain", "short_name": "PSG", "code": "PSG", "elo": 1830.0, "pi_h": 0.88, "pi_a": 0.70, "atk": 1.65, "defn": 0.70, "c_atk": 7.2, "c_def": 3.6},
        {"name": "Monaco", "short_name": "ASM", "code": "ASM", "elo": 1720.0, "pi_h": 0.55, "pi_a": 0.38, "atk": 1.35, "defn": 0.95, "c_atk": 5.8, "c_def": 4.8},
        {"name": "Olympique Marseille", "short_name": "OM", "code": "OM", "elo": 1700.0, "pi_h": 0.50, "pi_a": 0.32, "atk": 1.30, "defn": 0.98, "c_atk": 5.6, "c_def": 4.9},
        {"name": "Lille", "short_name": "LOSC", "code": "LOSC", "elo": 1680.0, "pi_h": 0.44, "pi_a": 0.28, "atk": 1.18, "defn": 0.90, "c_atk": 5.4, "c_def": 4.6},
        {"name": "Olympique Lyonnais", "short_name": "OL", "code": "OL", "elo": 1650.0, "pi_h": 0.35, "pi_a": 0.20, "atk": 1.20, "defn": 1.10, "c_atk": 5.2, "c_def": 5.0},
    ]
}


def seed_database(db: Session, force: bool = False):
    """Seed comprehensive teams, ratings, historical matches, and upcoming fixtures."""
    Base.metadata.create_all(bind=engine)

    existing_matches = db.query(Match).count()
    if existing_matches > 50 and not force:
        return

    # 1. Create Leagues & Seasons
    league_objs = {}
    for l_cfg in SEEDED_LEAGUES:
        league = db.query(League).filter_by(code=l_cfg["code"]).first()
        if not league:
            league = League(code=l_cfg["code"], name=l_cfg["name"], country=l_cfg["country"], active=True)
            db.add(league)
            db.commit()
            db.refresh(league)
        league_objs[l_cfg["code"]] = league

        # Current season
        season = db.query(Season).filter_by(league_id=league.id, name="2024-2025").first()
        if not season:
            season = Season(league_id=league.id, name="2024-2025", is_current=True)
            db.add(season)
            db.commit()

    # 2. Create Teams & Ratings
    team_objs = {}
    for code, teams_list in TEAMS_BY_LEAGUE.items():
        league = league_objs[code]
        for t_info in teams_list:
            team = db.query(Team).filter_by(name=t_info["name"]).first()
            if not team:
                team = Team(
                    name=t_info["name"],
                    short_name=t_info["short_name"],
                    code=t_info["code"],
                    league_id=league.id,
                    logo_url=f"/logos/{t_info['code'].lower()}.png"
                )
                db.add(team)
                db.commit()
                db.refresh(team)
                # Alias
                db.add(TeamAlias(team_id=team.id, alias=t_info["name"], source="canonical"))

            team_objs[t_info["name"]] = team

            # Rating
            r = db.query(Rating).filter_by(team_id=team.id).first()
            if not r:
                r = Rating(
                    team_id=team.id,
                    date=datetime.datetime.utcnow(),
                    elo=t_info["elo"],
                    pi_home=t_info["pi_h"],
                    pi_away=t_info["pi_a"],
                    attack_rating=t_info["atk"],
                    defence_rating=t_info["defn"],
                    corner_attack=t_info["c_atk"],
                    corner_defence=t_info["c_def"]
                )
                db.add(r)
        db.commit()

    # 3. Generate Historical Matches for Training & Form (Past 120 days)
    random.seed(42)  # Deterministic generation for reproducible calibration
    base_date = datetime.datetime.utcnow() - datetime.timedelta(days=120)

    for code, teams_list in TEAMS_BY_LEAGUE.items():
        league = league_objs[code]
        t_names = [t["name"] for t in teams_list]
        n_teams = len(t_names)

        # Generate round-robin match pairings
        match_idx = 0
        for i in range(n_teams):
            for j in range(n_teams):
                if i == j:
                    continue
                match_idx += 1
                match_date = base_date + datetime.timedelta(days=int(match_idx * 0.75))
                if match_date >= datetime.datetime.utcnow() - datetime.timedelta(days=1):
                    continue

                home_name = t_names[i]
                away_name = t_names[j]
                h_team = team_objs[home_name]
                a_team = team_objs[away_name]

                # Strength lookup
                h_info = next(t for t in teams_list if t["name"] == home_name)
                a_info = next(t for t in teams_list if t["name"] == away_name)

                # Simulated Poisson expected goals
                h_exp = max(0.4, 1.35 * h_info["atk"] / a_info["defn"])
                a_exp = max(0.3, 0.95 * a_info["atk"] / h_info["defn"])

                h_score = int(random.choices(range(6), weights=[
                    random.expovariate(1.0) / (k + 1) for k in range(6)
                ])[0])
                a_score = int(random.choices(range(6), weights=[
                    random.expovariate(1.2) / (k + 1) for k in range(6)
                ])[0])

                # Half-time
                ht_h = min(h_score, random.randint(0, 2))
                ht_a = min(a_score, random.randint(0, 1))

                # Shots & corners
                h_shots = int(h_exp * 4.5 + random.randint(2, 8))
                a_shots = int(a_exp * 4.2 + random.randint(2, 6))
                h_target = max(1, int(h_shots * 0.38 + h_score))
                a_target = max(1, int(a_shots * 0.35 + a_score))
                h_corners = int(h_info["c_atk"] * 0.8 + random.randint(1, 4))
                a_corners = int(a_info["c_atk"] * 0.7 + random.randint(1, 3))
                h_yellow = random.randint(0, 4)
                a_yellow = random.randint(1, 5)

                # Baseline odds
                prob_diff = (h_info["elo"] - a_info["elo"]) / 400.0
                p_h = max(0.15, min(0.75, 0.44 + prob_diff * 0.25))
                p_a = max(0.12, min(0.65, 0.28 - prob_diff * 0.22))
                p_d = max(0.18, 1.0 - p_h - p_a)

                # Add bookmaker margin ~ 5%
                margin = 1.05
                odds_h = round(1.0 / (p_h * margin), 2)
                odds_d = round(1.0 / (p_d * margin), 2)
                odds_a = round(1.0 / (p_a * margin), 2)

                # AH line
                ah_l = -0.75 if p_h > 0.60 else (-0.5 if p_h > 0.50 else (-0.25 if p_h > 0.44 else (0.0 if p_h > 0.38 else 0.5)))
                ah_h_odds = 1.95
                ah_a_odds = 1.95

                ou_l = 2.5
                ou_o_odds = 1.88
                ou_u_odds = 2.02

                m = Match(
                    league_id=league.id,
                    date=match_date,
                    home_team_id=h_team.id,
                    away_team_id=a_team.id,
                    status="FINISHED",
                    home_score=h_score,
                    away_score=a_score,
                    ht_home_score=ht_h,
                    ht_away_score=ht_a,
                    home_shots=h_shots,
                    away_shots=a_shots,
                    home_shots_target=h_target,
                    away_shots_target=a_target,
                    home_corners=h_corners,
                    away_corners=a_corners,
                    home_yellow=h_yellow,
                    away_yellow=a_yellow,
                    home_red=1 if random.random() < 0.08 else 0,
                    away_red=1 if random.random() < 0.10 else 0,
                    home_xg=round(h_exp + random.uniform(-0.3, 0.4), 2),
                    away_xg=round(a_exp + random.uniform(-0.2, 0.3), 2),
                    b365_home_odds=odds_h,
                    b365_draw_odds=odds_d,
                    b365_away_odds=odds_a,
                    closing_home_odds=round(odds_h * random.uniform(0.96, 1.04), 2),
                    closing_draw_odds=odds_d,
                    closing_away_odds=round(odds_a * random.uniform(0.96, 1.04), 2),
                    ah_line=ah_l,
                    ah_home_odds=ah_h_odds,
                    ah_away_odds=ah_a_odds,
                    ou_line=ou_l,
                    ou_over_odds=ou_o_odds,
                    ou_under_odds=ou_u_odds
                )
                db.add(m)

        db.commit()

    # 4. Generate UPCOMING Fixtures (Today and Tomorrow)
    now = datetime.datetime.utcnow()
    today_fixtures = [
        # Premier League marquee clashes
        {"league": "E0", "home": "Arsenal", "away": "Chelsea", "hours_ahead": 4, "ah": -0.75, "ah_h": 1.95, "ah_a": 1.95, "ou": 2.75, "ou_o": 1.92, "ou_u": 1.98, "h_odds": 1.72, "d_odds": 3.90, "a_odds": 4.60},
        {"league": "E0", "home": "Liverpool", "away": "Manchester City", "hours_ahead": 6, "ah": -0.25, "ah_h": 2.05, "ah_a": 1.85, "ou": 3.0, "ou_o": 1.85, "ou_u": 2.05, "h_odds": 2.35, "d_odds": 3.60, "a_odds": 2.90},
        {"league": "E0", "home": "Tottenham Hotspur", "away": "Newcastle United", "hours_ahead": 8, "ah": 0.0, "ah_h": 1.90, "ah_a": 2.00, "ou": 3.25, "ou_o": 1.95, "ou_u": 1.95, "h_odds": 2.55, "d_odds": 3.75, "a_odds": 2.65},
        {"league": "E0", "home": "Manchester United", "away": "Aston Villa", "hours_ahead": 24, "ah": 0.0, "ah_h": 1.98, "ah_a": 1.92, "ou": 2.75, "ou_o": 1.86, "ou_u": 2.04, "h_odds": 2.60, "d_odds": 3.50, "a_odds": 2.70},
        {"league": "E0", "home": "Brighton & Hove Albion", "away": "Fulham", "hours_ahead": 26, "ah": -0.5, "ah_h": 1.92, "ah_a": 1.98, "ou": 2.5, "ou_o": 1.82, "ou_u": 2.08, "h_odds": 1.90, "d_odds": 3.70, "a_odds": 4.00},
        {"league": "E0", "home": "Nottingham Forest", "away": "Ipswich Town", "hours_ahead": 28, "ah": -0.75, "ah_h": 1.88, "ah_a": 2.02, "ou": 2.5, "ou_o": 1.94, "ou_u": 1.94, "h_odds": 1.65, "d_odds": 4.00, "a_odds": 5.25},

        # La Liga
        {"league": "SP1", "home": "Real Madrid", "away": "Barcelona", "hours_ahead": 5, "ah": -0.25, "ah_h": 1.92, "ah_a": 1.98, "ou": 3.25, "ou_o": 1.90, "ou_u": 2.00, "h_odds": 2.15, "d_odds": 3.75, "a_odds": 3.10},
        {"league": "SP1", "home": "Atletico Madrid", "away": "Real Sociedad", "hours_ahead": 7, "ah": -0.75, "ah_h": 1.95, "ah_a": 1.95, "ou": 2.25, "ou_o": 1.95, "ou_u": 1.95, "h_odds": 1.70, "d_odds": 3.60, "a_odds": 5.50},
        {"league": "SP1", "home": "Athletic Bilbao", "away": "Real Betis", "hours_ahead": 25, "ah": -0.5, "ah_h": 1.85, "ah_a": 2.05, "ou": 2.5, "ou_o": 1.98, "ou_u": 1.90, "h_odds": 1.85, "d_odds": 3.50, "a_odds": 4.50},

        # Serie A
        {"league": "I1", "home": "Inter Milan", "away": "AC Milan", "hours_ahead": 7, "ah": -0.5, "ah_h": 1.95, "ah_a": 1.95, "ou": 2.5, "ou_o": 1.85, "ou_u": 2.05, "h_odds": 1.95, "d_odds": 3.60, "a_odds": 3.90},
        {"league": "I1", "home": "Juventus", "away": "AS Roma", "hours_ahead": 24, "ah": -0.5, "ah_h": 1.92, "ah_a": 1.98, "ou": 2.25, "ou_o": 1.96, "ou_u": 1.92, "h_odds": 1.88, "d_odds": 3.40, "a_odds": 4.40},
        {"league": "I1", "home": "Napoli", "away": "Atalanta", "hours_ahead": 27, "ah": -0.25, "ah_h": 1.90, "ah_a": 2.00, "ou": 2.75, "ou_o": 1.90, "ou_u": 2.00, "h_odds": 2.10, "d_odds": 3.50, "a_odds": 3.40},

        # Bundesliga
        {"league": "D1", "home": "Bayern Munich", "away": "Borussia Dortmund", "hours_ahead": 5, "ah": -1.25, "ah_h": 1.95, "ah_a": 1.95, "ou": 3.5, "ou_o": 1.88, "ou_u": 2.02, "h_odds": 1.45, "d_odds": 5.00, "a_odds": 6.00},
        {"league": "D1", "home": "Bayer Leverkusen", "away": "RB Leipzig", "hours_ahead": 26, "ah": -0.5, "ah_h": 1.90, "ah_a": 2.00, "ou": 3.0, "ou_o": 1.92, "ou_u": 1.96, "h_odds": 1.90, "d_odds": 3.90, "a_odds": 3.75},

        # Ligue 1
        {"league": "F1", "home": "Paris Saint-Germain", "away": "Olympique Marseille", "hours_ahead": 8, "ah": -1.0, "ah_h": 1.92, "ah_a": 1.98, "ou": 3.0, "ou_o": 1.85, "ou_u": 2.05, "h_odds": 1.55, "d_odds": 4.50, "a_odds": 5.50},
        {"league": "F1", "home": "Monaco", "away": "Lille", "hours_ahead": 28, "ah": -0.25, "ah_h": 1.94, "ah_a": 1.96, "ou": 2.5, "ou_o": 1.90, "ou_u": 2.00, "h_odds": 2.20, "d_odds": 3.50, "a_odds": 3.20},
    ]

    for fix in today_fixtures:
        league = league_objs[fix["league"]]
        h_team = team_objs[fix["home"]]
        a_team = team_objs[fix["away"]]

        fix_date = now + datetime.timedelta(hours=fix["hours_ahead"])
        m = Match(
            league_id=league.id,
            date=fix_date,
            home_team_id=h_team.id,
            away_team_id=a_team.id,
            status="SCHEDULED",
            b365_home_odds=fix["h_odds"],
            b365_draw_odds=fix["d_odds"],
            b365_away_odds=fix["a_odds"],
            ah_line=fix["ah"],
            ah_home_odds=fix["ah_h"],
            ah_away_odds=fix["ah_a"],
            ou_line=fix["ou"],
            ou_over_odds=fix["ou_o"],
            ou_under_odds=fix["ou_u"]
        )
        db.add(m)
        db.commit()
        db.refresh(m)

        # Generate sample line movement snapshots over the past 24 hours
        time_offsets = [24, 18, 12, 6, 2, 0]
        ah_moves = [-0.05, -0.03, 0.0, 0.02, 0.0, 0.0]
        ou_moves = [0.04, 0.02, 0.0, -0.02, 0.0, 0.0]

        for idx, hours_ago in enumerate(time_offsets):
            snap_time = now - datetime.timedelta(hours=hours_ago)
            # Bet365 1X2
            db.add(OddsSnapshot(
                match_id=m.id,
                bookmaker="Bet365",
                market="1X2",
                selection="Home",
                price=round(fix["h_odds"] + ah_moves[idx], 2),
                timestamp=snap_time,
                is_closing=(hours_ago == 0)
            ))
            db.add(OddsSnapshot(
                match_id=m.id,
                bookmaker="Pinnacle",
                market="AH",
                line=fix["ah"],
                selection=f"Home {fix['ah']}",
                price=round(fix["ah_h"] + ah_moves[idx], 2),
                timestamp=snap_time,
                is_closing=(hours_ago == 0)
            ))
            db.add(OddsSnapshot(
                match_id=m.id,
                bookmaker="Pinnacle",
                market="OU",
                line=fix["ou"],
                selection=f"Over {fix['ou']}",
                price=round(fix["ou_o"] + ou_moves[idx], 2),
                timestamp=snap_time,
                is_closing=(hours_ago == 0)
            ))

    db.commit()
    print("Database successfully seeded with historical & upcoming matches!")


if __name__ == "__main__":
    db = SessionLocal()
    seed_database(db, force=True)
    db.close()
