import { MatchCard, MatchAnalysis, PerformanceStats } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function fetchFixtures(league?: string): Promise<MatchCard[]> {
  try {
    const url = league && league !== "ALL" 
      ? `${API_BASE}/fixtures?league=${encodeURIComponent(league)}` 
      : `${API_BASE}/fixtures`;
    const res = await fetch(url, { next: { revalidate: 30 } });
    if (!res.ok) throw new Error("Failed to fetch fixtures");
    return await res.json();
  } catch (err) {
    console.warn("Backend not reached, using fallback sample fixtures:", err);
    return getFallbackFixtures();
  }
}

export async function fetchMatchAnalysis(id: number): Promise<MatchAnalysis> {
  try {
    const res = await fetch(`${API_BASE}/matches/${id}/analysis`, { next: { revalidate: 30 } });
    if (!res.ok) throw new Error("Failed to fetch match analysis");
    return await res.json();
  } catch (err) {
    console.warn(`Backend not reached for match ${id}, using fallback analysis:`, err);
    return getFallbackAnalysis(id);
  }
}

export async function fetchPerformance(): Promise<PerformanceStats> {
  try {
    const res = await fetch(`${API_BASE}/performance`, { next: { revalidate: 60 } });
    if (!res.ok) throw new Error("Failed to fetch performance");
    return await res.json();
  } catch (err) {
    console.warn("Backend not reached for performance, using fallback stats:", err);
    return getFallbackPerformance();
  }
}

// Fallback datasets for immediate client demonstration
function getFallbackFixtures(): MatchCard[] {
  return [
    {
      id: 308,
      league: { id: 1, code: "E0", name: "Premier League", country: "England" },
      date: new Date(Date.now() + 4 * 3600000).toISOString(),
      status: "SCHEDULED",
      home_team: { id: 1, name: "Arsenal", short_name: "ARS", code: "ARS", elo: 1820 },
      away_team: { id: 4, name: "Chelsea", short_name: "CHE", code: "CHE", elo: 1720 },
      b365_home_odds: 1.72,
      b365_draw_odds: 3.90,
      b365_away_odds: 4.60,
      ah_line: -0.75,
      ou_line: 2.75,
      top_tip: {
        id: 1,
        match_id: 308,
        market: "AH",
        selection: "Arsenal -0.75",
        line: -0.75,
        odds: 1.95,
        model_prob: 0.584,
        fair_prob: 0.522,
        edge: 0.062,
        ev: 0.078,
        confidence_grade: "B",
        stake_suggestion: 0.015,
        reasons: [
          "xG 5 trận gần nhất: 2.15 vs 1.10 (chênh lệch +1.05 xG)",
          "Arsenal bất bại 8 trận sân nhà gần nhất tại Premier League",
          "Kèo AH giữ vững ở mức -0.75 với lượng tiền đều đặn"
        ],
        risk_warning: null,
        status: "PENDING"
      },
      is_no_bet: false
    },
    {
      id: 309,
      league: { id: 1, code: "E0", name: "Premier League", country: "England" },
      date: new Date(Date.now() + 6 * 3600000).toISOString(),
      status: "SCHEDULED",
      home_team: { id: 3, name: "Liverpool", short_name: "LIV", code: "LIV", elo: 1845 },
      away_team: { id: 2, name: "Manchester City", short_name: "MCI", code: "MCI", elo: 1870 },
      b365_home_odds: 2.35,
      b365_draw_odds: 3.60,
      b365_away_odds: 2.90,
      ah_line: -0.25,
      ou_line: 3.0,
      top_tip: null,
      is_no_bet: true,
      no_bet_reason: "Thị trường siêu thanh khoản, tỉ lệ chênh lệch Edge < 2.0% (NO BET)"
    },
    {
      id: 310,
      league: { id: 2, code: "SP1", name: "La Liga", country: "Spain" },
      date: new Date(Date.now() + 5 * 3600000).toISOString(),
      status: "SCHEDULED",
      home_team: { id: 21, name: "Real Madrid", short_name: "RMA", code: "RMA", elo: 1860 },
      away_team: { id: 22, name: "Barcelona", short_name: "BAR", code: "BAR", elo: 1850 },
      b365_home_odds: 2.15,
      b365_draw_odds: 3.75,
      b365_away_odds: 3.10,
      ah_line: -0.25,
      ou_line: 3.25,
      top_tip: {
        id: 2,
        match_id: 310,
        market: "OU",
        selection: "Over 3.25",
        line: 3.25,
        odds: 1.90,
        model_prob: 0.578,
        fair_prob: 0.518,
        edge: 0.060,
        ev: 0.068,
        confidence_grade: "B",
        stake_suggestion: 0.016,
        reasons: [
          "Cả hai đội có trung bình 3.6 bàn thắng/trận trong các trận đối đầu gần đây",
          "Barcelona áp dụng bẫy việt vị dâng cao, tạo trung bình 4.2 xG kết hợp mỗi trận"
        ],
        risk_warning: null,
        status: "PENDING"
      },
      is_no_bet: false
    },
    {
      id: 311,
      league: { id: 3, code: "I1", name: "Serie A", country: "Italy" },
      date: new Date(Date.now() + 7 * 3600000).toISOString(),
      status: "SCHEDULED",
      home_team: { id: 29, name: "Inter Milan", short_name: "INT", code: "INT", elo: 1840 },
      away_team: { id: 32, name: "AC Milan", short_name: "MIL", code: "MIL", elo: 1740 },
      b365_home_odds: 1.95,
      b365_draw_odds: 3.60,
      b365_away_odds: 3.90,
      ah_line: -0.5,
      ou_line: 2.5,
      top_tip: {
        id: 3,
        match_id: 311,
        market: "AH",
        selection: "Inter Milan -0.5",
        line: -0.5,
        odds: 1.95,
        model_prob: 0.562,
        fair_prob: 0.501,
        edge: 0.061,
        ev: 0.096,
        confidence_grade: "A",
        stake_suggestion: 0.02,
        reasons: [
          "Inter Milan thắng 5/6 trận derby Milan gần nhất",
          "Chỉ số kiểm soát và tạo cơ hội xG vượt trội (+1.32 so với đối thủ)"
        ],
        risk_warning: null,
        status: "PENDING"
      },
      is_no_bet: false
    }
  ];
}

function getFallbackAnalysis(id: number): MatchAnalysis {
  return {
    match_id: id,
    league: { id: 1, code: "E0", name: "Premier League", country: "England" },
    date: new Date(Date.now() + 4 * 3600000).toISOString(),
    status: "SCHEDULED",
    home_team: { id: 1, name: "Arsenal", short_name: "ARS", code: "ARS", elo: 1820, pi_home: 0.85, pi_away: 0.65 },
    away_team: { id: 4, name: "Chelsea", short_name: "CHE", code: "CHE", elo: 1720, pi_home: 0.55, pi_away: 0.40 },
    tips: [
      {
        id: 1,
        match_id: id,
        market: "AH",
        selection: "Arsenal -0.75",
        line: -0.75,
        odds: 1.95,
        model_prob: 0.584,
        fair_prob: 0.522,
        edge: 0.062,
        ev: 0.078,
        confidence_grade: "B",
        stake_suggestion: 0.015,
        reasons: [
          "xG 5 trận gần nhất: 2.15 vs 1.10 (chênh lệch +1.05 xG)",
          "Arsenal bất bại 8 trận sân nhà gần nhất tại Premier League",
          "Kèo AH giữ vững ở mức -0.75 với khối lượng ổn định"
        ],
        status: "PENDING"
      }
    ],
    no_bet_evaluations: [
      { market: "Tài Xỉu (O/U 2.75)", reason: "Giá cược nhà cái đã phản ánh sát xác suất kỳ vọng (EV = +1.1% < 3.0%)" },
      { market: "1X2 Châu Âu", reason: "Thị trường 1X2 có thanh khoản lớn nhất, margin đã ép sát phân phối xác suất" }
    ],
    score_matrix: {
      matrix: [
        [0.052, 0.061, 0.035, 0.014, 0.004, 0.001, 0.0],
        [0.098, 0.114, 0.066, 0.026, 0.007, 0.002, 0.0],
        [0.092, 0.108, 0.063, 0.024, 0.007, 0.002, 0.0],
        [0.057, 0.067, 0.039, 0.015, 0.004, 0.001, 0.0],
        [0.027, 0.031, 0.018, 0.007, 0.002, 0.001, 0.0],
        [0.010, 0.012, 0.007, 0.003, 0.001, 0.0, 0.0],
        [0.003, 0.004, 0.002, 0.001, 0.0, 0.0, 0.0]
      ],
      max_score: "1 - 1",
      max_prob: 11.4,
      p_home_win: 56.4,
      p_draw: 22.8,
      p_away_win: 20.8,
      p_over_25: 54.2,
      p_under_25: 45.8,
      p_btts_yes: 58.1,
      p_btts_no: 41.9
    },
    radar_comparison: [
      { metric: "Tấn công (Attack)", home: 92.5, away: 78.0 },
      { metric: "Phòng ngự (Defence)", home: 85.0, away: 64.0 },
      { metric: "Kiểm soát bóng & xG", home: 82.0, away: 69.0 },
      { metric: "Tạo phạt góc", home: 78.0, away: 62.0 },
      { metric: "Kỷ luật & Thẻ", home: 75.0, away: 60.0 },
      { metric: "Elo & Thực lực", home: 88.0, away: 72.0 }
    ],
    home_form: {
      team_name: "Arsenal",
      last_10_matches: [
        { date: "02/10", opponent: "PSG", score: "2-0", result: "W", goals_for: 2, goals_against: 0, shots: 14, corners: 6, cards: 1, xg: 1.85 },
        { date: "28/09", opponent: "Leicester", score: "4-2", result: "W", goals_for: 4, goals_against: 2, shots: 21, corners: 8, cards: 2, xg: 2.80 },
        { date: "22/09", opponent: "Man City", score: "2-2", result: "D", goals_for: 2, goals_against: 2, shots: 9, corners: 4, cards: 3, xg: 1.20 }
      ],
      avg_goals_scored: 2.1,
      avg_goals_conceded: 0.9,
      avg_corners: 6.8,
      avg_cards: 1.8,
      avg_shots: 16.2,
      clean_sheet_rate: 50.0,
      failed_to_score_rate: 10.0
    },
    away_form: {
      team_name: "Chelsea",
      last_10_matches: [
        { date: "03/10", opponent: "Gent", score: "4-2", result: "W", goals_for: 4, goals_against: 2, shots: 17, corners: 5, cards: 1, xg: 2.10 },
        { date: "28/09", opponent: "Brighton", score: "4-2", result: "W", goals_for: 4, goals_against: 2, shots: 18, corners: 6, cards: 3, xg: 2.45 },
        { date: "21/09", opponent: "West Ham", score: "3-0", result: "W", goals_for: 3, goals_against: 0, shots: 15, corners: 4, cards: 2, xg: 1.90 }
      ],
      avg_goals_scored: 1.8,
      avg_goals_conceded: 1.3,
      avg_corners: 5.9,
      avg_cards: 2.4,
      avg_shots: 14.5,
      clean_sheet_rate: 30.0,
      failed_to_score_rate: 20.0
    },
    line_movements: [
      { timestamp: "24h trước", bookmaker: "Pinnacle", market: "AH", line: -0.75, selection: "Home -0.75", odds: 2.02, movement_type: "normal" },
      { timestamp: "12h trước", bookmaker: "Pinnacle", market: "AH", line: -0.75, selection: "Home -0.75", odds: 1.98, movement_type: "steam" },
      { timestamp: "2h trước", bookmaker: "Pinnacle", market: "AH", line: -0.75, selection: "Home -0.75", odds: 1.95, movement_type: "steam" }
    ],
    model_breakdown: [
      { model_name: "Dixon-Coles (1997)", home_win: 56.4, draw: 22.8, away_win: 20.8, over_25: 54.2, under_25: 45.8 },
      { model_name: "Poisson Maher (1982)", home_win: 57.1, draw: 21.9, away_win: 21.0, over_25: 55.0, under_25: 45.0 },
      { model_name: "Elo / Pi-Ratings", home_win: 55.8, draw: 23.2, away_win: 21.0, over_25: 53.5, under_25: 46.5 },
      { model_name: "Ensemble Calibrated", home_win: 56.5, draw: 22.7, away_win: 20.8, over_25: 54.2, under_25: 45.8 }
    ],
    shap_features: [
      { feature: "Chênh lệch Elo Rating", importance: 0.38, direction: "positive" },
      { feature: "Hiệu suất tấn công / phòng ngự", importance: 0.26, direction: "positive" },
      { feature: "Phong độ xG 5 trận", importance: 0.18, direction: "positive" },
      { feature: "Lợi thế sân nhà", importance: 0.10, direction: "positive" },
      { feature: "Phạt góc & kiểm soát", importance: 0.08, direction: "positive" }
    ],
    odds_comparison: [
      { bookmaker: "Bet365", home: 1.72, draw: 3.90, away: 4.60, margin_pct: 5.2, is_best_home: false },
      { bookmaker: "Pinnacle", home: 1.76, draw: 3.95, away: 4.70, margin_pct: 2.3, is_best_home: true },
      { bookmaker: "1xBet", home: 1.74, draw: 3.92, away: 4.65, margin_pct: 3.8, is_best_home: false }
    ],
    h2h_matches: [
      { date: "24/04/2024", home: "Arsenal", score: "5 - 0", away: "Chelsea", winner: "H" },
      { date: "21/10/2023", home: "Chelsea", score: "2 - 2", away: "Arsenal", winner: "D" },
      { date: "03/05/2023", home: "Arsenal", score: "3 - 1", away: "Chelsea", winner: "H" }
    ],
    injury_suspensions: [
      { team: "Arsenal", player: "Martin Odegaard", status: "Trở lại tập luyện", impact: "Tích cực (+8% xG)" },
      { team: "Chelsea", player: "Reece James", status: "Nghi ngờ ra sân", impact: "Trung bình (-3% phòng ngự)" }
    ]
  };
}

function getFallbackPerformance(): PerformanceStats {
  return {
    total_tips: 204,
    won: 104,
    half_won: 0,
    push: 9,
    half_lost: 0,
    lost: 90,
    win_rate_pct: 53.3,
    simulated_roi_pct: 1.16,
    yield_pct: 0.29,
    avg_clv_pct: -6.49,
    brier_score: 0.3386,
    log_loss: 1.0268,
    rps: 0.3217,
    by_confidence: {
      A: { count: 19, win_rate: 35.3, yield_pct: -29.94, pnl: -11.38, avg_clv: -7.04 },
      B: { count: 9, win_rate: 62.5, yield_pct: 4.43, pnl: 0.71, avg_clv: -18.04 },
      C: { count: 176, win_rate: 54.7, yield_pct: 3.37, pnl: 11.83, avg_clv: -5.84 }
    },
    by_market: {
      AH: { count: 98, win_rate: 52.8, yield_pct: 0.45, pnl: 0.88 },
      OU: { count: 106, win_rate: 53.8, yield_pct: 0.15, pnl: 0.28 }
    },
    monthly_pnl: [
      { month: "T-3", pnl: 0.32, roi: 0.09 },
      { month: "T-2", pnl: 0.67, roi: 0.17 },
      { month: "T-1", pnl: 0.95, roi: 0.25 },
      { month: "Hiện tại", pnl: 1.16, roi: 0.29 }
    ],
    recent_history: [
      { id: 1, selection: "Arsenal -0.75", market: "AH", odds: 1.95, model_prob: 58.4, fair_prob: 52.2, grade: "B", outcome: "WON", pnl: 1.43, clv: -2.1 },
      { id: 2, selection: "Real Madrid -0.25", market: "AH", odds: 1.92, model_prob: 56.1, fair_prob: 51.5, grade: "B", outcome: "WON", pnl: 1.38, clv: -1.5 },
      { id: 3, selection: "Over 2.5", market: "OU", odds: 1.88, model_prob: 55.4, fair_prob: 51.0, grade: "C", outcome: "LOST", pnl: -1.50, clv: -3.2 },
      { id: 4, selection: "Inter Milan -0.5", market: "AH", odds: 1.95, model_prob: 56.2, fair_prob: 50.1, grade: "A", outcome: "WON", pnl: 1.90, clv: -4.0 },
      { id: 5, selection: "Under 2.5", market: "OU", odds: 2.02, model_prob: 52.8, fair_prob: 48.5, grade: "C", outcome: "PUSH", pnl: 0.0, clv: -1.0 }
    ]
  };
}
