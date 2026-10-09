import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class League(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)  # E0, SP1, I1, D1, F1
    name = Column(String(100), nullable=False)                         # Premier League, La Liga, etc.
    country = Column(String(50), nullable=False)
    active = Column(Boolean, default=True)

    matches = relationship("Match", back_populates="league")
    teams = relationship("Team", back_populates="league")


class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    name = Column(String(20), nullable=False)  # "2024-2025"
    is_current = Column(Boolean, default=True)

    matches = relationship("Match", back_populates="season")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    name = Column(String(100), unique=True, index=True, nullable=False)
    short_name = Column(String(50), nullable=True)
    code = Column(String(10), nullable=True)
    logo_url = Column(String(255), nullable=True)

    league = relationship("League", back_populates="teams")
    aliases = relationship("TeamAlias", back_populates="team", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="team", cascade="all, delete-orphan")


class TeamAlias(Base):
    __tablename__ = "team_aliases"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    alias = Column(String(100), index=True, nullable=False)
    source = Column(String(50), nullable=False)  # e.g. "football-data.co.uk", "odds-api"

    team = relationship("Team", back_populates="aliases")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=True)
    date = Column(DateTime, nullable=False, index=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    status = Column(String(20), default="SCHEDULED")  # FINISHED, SCHEDULED, LIVE

    # Full Time & Half Time scores
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    ht_home_score = Column(Integer, nullable=True)
    ht_away_score = Column(Integer, nullable=True)

    # In-depth match stats
    home_shots = Column(Integer, nullable=True)
    away_shots = Column(Integer, nullable=True)
    home_shots_target = Column(Integer, nullable=True)
    away_shots_target = Column(Integer, nullable=True)
    home_corners = Column(Integer, nullable=True)
    away_corners = Column(Integer, nullable=True)
    home_yellow = Column(Integer, nullable=True)
    away_yellow = Column(Integer, nullable=True)
    home_red = Column(Integer, nullable=True)
    away_red = Column(Integer, nullable=True)
    home_xg = Column(Float, nullable=True)
    away_xg = Column(Float, nullable=True)

    # Market odds snapshot (1X2 closing or latest)
    b365_home_odds = Column(Float, nullable=True)
    b365_draw_odds = Column(Float, nullable=True)
    b365_away_odds = Column(Float, nullable=True)
    closing_home_odds = Column(Float, nullable=True)
    closing_draw_odds = Column(Float, nullable=True)
    closing_away_odds = Column(Float, nullable=True)
    
    # Asian Handicap and Over/Under consensus lines
    ah_line = Column(Float, nullable=True)      # e.g., -0.75
    ah_home_odds = Column(Float, nullable=True) # e.g., 1.95
    ah_away_odds = Column(Float, nullable=True) # e.g., 1.95
    ou_line = Column(Float, nullable=True)      # e.g., 2.5 or 2.75
    ou_over_odds = Column(Float, nullable=True) # e.g., 1.85
    ou_under_odds = Column(Float, nullable=True)

    league = relationship("League", back_populates="matches")
    season = relationship("Season", back_populates="matches")
    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])
    
    odds_snapshots = relationship("OddsSnapshot", back_populates="match", cascade="all, delete-orphan")
    tips = relationship("Tip", back_populates="match", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="match", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_matches_date_league", "date", "league_id"),
    )


class OddsSnapshot(Base):
    __tablename__ = "odds_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    bookmaker = Column(String(50), nullable=False)  # Bet365, Pinnacle, 1xBet, Avg
    market = Column(String(30), nullable=False)     # 1X2, AH, OU, CORNER_OU, CORNER_AH, BTTS
    line = Column(Float, nullable=True)             # e.g. -0.5, 2.5, 9.5
    selection = Column(String(30), nullable=False)  # Home, Away, Draw, Over, Under, Yes, No
    price = Column(Float, nullable=False)           # Decimal odds e.g. 1.95
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    is_closing = Column(Boolean, default=False)

    match = relationship("Match", back_populates="odds_snapshots")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    elo = Column(Float, default=1500.0)
    pi_home = Column(Float, default=0.0)
    pi_away = Column(Float, default=0.0)
    attack_rating = Column(Float, default=1.0)
    defence_rating = Column(Float, default=1.0)
    corner_attack = Column(Float, default=5.0)
    corner_defence = Column(Float, default=5.0)

    team = relationship("Team", back_populates="ratings")


class ModelRun(Base):
    __tablename__ = "model_runs"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(50), nullable=False)
    version = Column(String(30), nullable=False)
    run_at = Column(DateTime, default=datetime.datetime.utcnow)
    parameters_json = Column(Text, nullable=True)
    metrics_json = Column(Text, nullable=True)  # brier, log_loss, rps, etc.


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    model_name = Column(String(50), nullable=False)  # Poisson, Dixon-Coles, Elo, LightGBM, Ensemble
    version = Column(String(30), nullable=False)
    market = Column(String(30), nullable=False)
    line = Column(Float, nullable=True)
    selection = Column(String(30), nullable=False)
    prob = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    match = relationship("Match", back_populates="predictions")


class Tip(Base):
    __tablename__ = "tips"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    market = Column(String(30), nullable=False)      # AH, OU, 1X2, BTTS, CORNER_AH, CORNER_OU
    selection = Column(String(50), nullable=False)   # e.g. "Arsenal -0.75", "Over 2.5", "Home"
    line = Column(Float, nullable=True)              # -0.75, 2.5
    odds = Column(Float, nullable=False)             # Best available decimal odds
    model_prob = Column(Float, nullable=False)       # Calibrated ensemble prob
    fair_prob = Column(Float, nullable=False)        # De-vigged market prob
    edge = Column(Float, nullable=False)             # model_prob - fair_prob
    ev = Column(Float, nullable=False)               # Expected Value percentage
    confidence_grade = Column(String(5), nullable=False) # A, B, C, D
    stake_suggestion = Column(Float, nullable=False) # Virtual bankroll stake % (Quarter Kelly)
    reasons_json = Column(Text, nullable=False)      # Bullet reasons array as JSON string
    risk_warning = Column(String(255), nullable=True)# High market divergence warning or injury warning
    status = Column(String(20), default="PENDING")   # PENDING, WON, HALF_WON, PUSH, HALF_LOST, LOST, VOID
    result_pnl = Column(Float, default=0.0)
    clv = Column(Float, nullable=True)               # Closing Line Value (%)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    match = relationship("Match", back_populates="tips")


class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, index=True)
    model_version = Column(String(50), nullable=False)
    market = Column(String(30), nullable=False)
    league_code = Column(String(20), nullable=True)
    test_period = Column(String(50), nullable=False)
    total_bets = Column(Integer, default=0)
    won_bets = Column(Integer, default=0)
    half_won_bets = Column(Integer, default=0)
    push_bets = Column(Integer, default=0)
    half_lost_bets = Column(Integer, default=0)
    lost_bets = Column(Integer, default=0)
    roi = Column(Float, default=0.0)
    yield_pct = Column(Float, default=0.0)
    brier_score = Column(Float, default=0.0)
    log_loss = Column(Float, default=0.0)
    rps = Column(Float, default=0.0)
    clv_avg = Column(Float, default=0.0)
    calibration_data_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.datetime.utcnow)
    note = Column(String(255), nullable=True)
