import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any


class TeamSummary(BaseModel):
    id: int
    name: str
    short_name: Optional[str] = None
    code: Optional[str] = None
    logo_url: Optional[str] = None
    elo: Optional[float] = None
    pi_home: Optional[float] = None
    pi_away: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class LeagueSummary(BaseModel):
    id: int
    code: str
    name: str
    country: str

    model_config = ConfigDict(from_attributes=True)


class TipOut(BaseModel):
    id: int
    match_id: int
    market: str  # AH, OU, 1X2, BTTS, CORNER_AH, CORNER_OU
    selection: str
    line: Optional[float] = None
    odds: float
    model_prob: float
    fair_prob: float
    edge: float
    ev: float
    confidence_grade: str  # A, B, C, D
    stake_suggestion: float
    reasons: List[str]
    risk_warning: Optional[str] = None
    status: str
    result_pnl: Optional[float] = 0.0
    clv: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class NoBetReason(BaseModel):
    match_id: int
    home_team: str
    away_team: str
    market: str
    reason: str  # "No positive edge", "High market divergence (>12%)", "Insufficient sample size"


class MatchCardOut(BaseModel):
    id: int
    league: LeagueSummary
    date: datetime.datetime
    status: str
    home_team: TeamSummary
    away_team: TeamSummary
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    b365_home_odds: Optional[float] = None
    b365_draw_odds: Optional[float] = None
    b365_away_odds: Optional[float] = None
    ah_line: Optional[float] = None
    ou_line: Optional[float] = None
    top_tip: Optional[TipOut] = None
    is_no_bet: bool = False
    no_bet_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OddsSnapshotItem(BaseModel):
    bookmaker: str
    market: str
    line: Optional[float] = None
    selection: str
    price: float
    timestamp: datetime.datetime
    is_closing: bool = False

    model_config = ConfigDict(from_attributes=True)


class ScoreCell(BaseModel):
    home_goals: int
    away_goals: int
    probability: float


class ScoreMatrixData(BaseModel):
    matrix: List[List[float]]  # 0..6 or 0..10
    max_score: str
    max_prob: float
    p_home_win: float
    p_draw: float
    p_away_win: float
    p_over_25: float
    p_under_25: float
    p_btts_yes: float
    p_btts_no: float


class RadarMetric(BaseModel):
    metric: str
    home: float
    away: float


class FormMatch(BaseModel):
    date: str
    opponent: str
    score: str
    result: str  # W, D, L
    goals_for: int
    goals_against: int
    shots: int
    corners: int
    cards: int
    xg: Optional[float] = None


class TeamFormStats(BaseModel):
    team_name: str
    last_10_matches: List[FormMatch]
    avg_goals_scored: float
    avg_goals_conceded: float
    avg_corners: float
    avg_cards: float
    avg_shots: float
    clean_sheet_rate: float
    failed_to_score_rate: float


class LineMovementPoint(BaseModel):
    timestamp: str
    bookmaker: str
    market: str
    line: Optional[float] = None
    selection: str
    odds: float
    movement_type: Optional[str] = None  # normal, steam, reverse


class ModelComponentProb(BaseModel):
    model_name: str
    home_win: float
    draw: float
    away_win: float
    over_25: float
    under_25: float


class FeatureImportanceItem(BaseModel):
    feature: str
    importance: float
    direction: str  # positive, negative


class MatchAnalysisOut(BaseModel):
    match_id: int
    league: LeagueSummary
    date: datetime.datetime
    status: str
    home_team: TeamSummary
    away_team: TeamSummary
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    
    # Tips & Decisions
    tips: List[TipOut]
    no_bet_evaluations: List[Dict[str, Any]]
    
    # Quantitative Visual Data
    score_matrix: ScoreMatrixData
    radar_comparison: List[RadarMetric]
    home_form: TeamFormStats
    away_form: TeamFormStats
    line_movements: List[LineMovementPoint]
    model_breakdown: List[ModelComponentProb]
    shap_features: List[FeatureImportanceItem]
    odds_comparison: List[Dict[str, Any]]
    h2h_matches: List[Dict[str, Any]]
    injury_suspensions: List[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)


class CalibrationBin(BaseModel):
    bin_center: float
    predicted_prob: float
    observed_freq: float
    sample_count: int


class CalibrationCurveOut(BaseModel):
    market: str
    bins: List[CalibrationBin]
    brier_score: float
    log_loss: float
    rps: float
    ece: float  # Expected Calibration Error


class PerformanceStatsOut(BaseModel):
    total_tips: int
    won: int
    half_won: int
    push: int
    half_lost: int
    lost: int
    win_rate_pct: float
    simulated_roi_pct: float
    yield_pct: float
    avg_clv_pct: float
    brier_score: float
    log_loss: float
    rps: float
    by_confidence: Dict[str, Dict[str, Any]]  # Grade A, B, C, D hit rate & ROI
    by_market: Dict[str, Dict[str, Any]]
    monthly_pnl: List[Dict[str, Any]]
    recent_history: List[Dict[str, Any]]
