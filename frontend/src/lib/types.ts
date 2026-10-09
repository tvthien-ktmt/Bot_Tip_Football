export interface LeagueSummary {
  id: number;
  code: string;
  name: string;
  country: string;
}

export interface TeamSummary {
  id: number;
  name: string;
  short_name?: string;
  code?: string;
  logo_url?: string;
  elo?: number;
  pi_home?: number;
  pi_away?: number;
}

export interface TipItem {
  id: number;
  match_id: number;
  market: string;
  selection: string;
  line?: number;
  odds: number;
  model_prob: number;
  fair_prob: number;
  edge: number;
  ev: number;
  confidence_grade: "A" | "B" | "C" | "D";
  stake_suggestion: number;
  reasons: string[];
  risk_warning?: string | null;
  status: string;
  result_pnl?: number;
  clv?: number | null;
}

export interface MatchCard {
  id: number;
  league: LeagueSummary;
  date: string;
  status: string;
  home_team: TeamSummary;
  away_team: TeamSummary;
  home_score?: number;
  away_score?: number;
  b365_home_odds?: number;
  b365_draw_odds?: number;
  b365_away_odds?: number;
  ah_line?: number;
  ou_line?: number;
  top_tip?: TipItem | null;
  is_no_bet: boolean;
  no_bet_reason?: string | null;
}

export interface ScoreMatrixData {
  matrix: number[][];
  max_score: string;
  max_prob: number;
  p_home_win: number;
  p_draw: number;
  p_away_win: number;
  p_over_25: number;
  p_under_25: number;
  p_btts_yes: number;
  p_btts_no: number;
}

export interface RadarMetric {
  metric: string;
  home: number;
  away: number;
}

export interface FormMatch {
  date: string;
  opponent: string;
  score: string;
  result: "W" | "D" | "L";
  goals_for: number;
  goals_against: number;
  shots: number;
  corners: number;
  cards: number;
  xg?: number;
}

export interface TeamFormStats {
  team_name: string;
  last_10_matches: FormMatch[];
  avg_goals_scored: number;
  avg_goals_conceded: number;
  avg_corners: number;
  avg_cards: number;
  avg_shots: number;
  clean_sheet_rate: number;
  failed_to_score_rate: number;
}

export interface LineMovementPoint {
  timestamp: string;
  bookmaker: string;
  market: string;
  line?: number;
  selection: string;
  odds: number;
  movement_type?: "normal" | "steam" | "reverse";
}

export interface ModelComponentProb {
  model_name: string;
  home_win: number;
  draw: number;
  away_win: number;
  over_25: number;
  under_25: number;
}

export interface FeatureImportanceItem {
  feature: string;
  importance: number;
  direction: string;
}

export interface MatchAnalysis {
  match_id: number;
  league: LeagueSummary;
  date: string;
  status: string;
  home_team: TeamSummary;
  away_team: TeamSummary;
  home_score?: number;
  away_score?: number;
  tips: TipItem[];
  no_bet_evaluations: Array<{ market: string; reason: string }>;
  score_matrix: ScoreMatrixData;
  radar_comparison: RadarMetric[];
  home_form: TeamFormStats;
  away_form: TeamFormStats;
  line_movements: LineMovementPoint[];
  model_breakdown: ModelComponentProb[];
  shap_features: FeatureImportanceItem[];
  odds_comparison: Array<{
    bookmaker: string;
    home: number;
    draw: number;
    away: number;
    margin_pct: number;
    is_best_home: boolean;
  }>;
  h2h_matches: Array<{
    date: string;
    home: string;
    score: string;
    away: string;
    winner: string;
  }>;
  injury_suspensions: Array<{
    team: string;
    player: string;
    status: string;
    impact: string;
  }>;
}

export interface PerformanceStats {
  total_tips: number;
  won: number;
  half_won: number;
  push: number;
  half_lost: number;
  lost: number;
  win_rate_pct: number;
  simulated_roi_pct: number;
  yield_pct: number;
  avg_clv_pct: number;
  brier_score: number;
  log_loss: number;
  rps: number;
  by_confidence: Record<string, {
    count: number;
    win_rate: number;
    yield_pct: number;
    pnl: number;
    avg_clv: number;
  }>;
  by_market: Record<string, {
    count: number;
    win_rate: number;
    yield_pct: number;
    pnl: number;
  }>;
  monthly_pnl: Array<{ month: string; pnl: number; roi: number }>;
  recent_history: Array<{
    id: number;
    selection: string;
    market: string;
    odds: number;
    model_prob: number;
    fair_prob: number;
    grade: string;
    outcome: string;
    pnl: number;
    clv: number;
  }>;
}
