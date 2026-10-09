"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { fetchMatchAnalysis } from "@/lib/api";
import { MatchAnalysis } from "@/lib/types";
import ScoreHeatmap from "@/components/ScoreHeatmap";
import RadarChartComponent from "@/components/RadarChart";
import FormChart from "@/components/FormChart";
import LineMovementChart from "@/components/LineMovementChart";
import ManualOddsCalculator from "@/components/ManualOddsCalculator";
import {
  ArrowLeft, Activity, Award, ShieldAlert, AlertTriangle,
  Flame, TrendingUp, HelpCircle, BarChart2, Users, Layers, Calculator
} from "lucide-react";

export default function MatchCenterPage() {
  const params = useParams();
  const matchId = Number(params?.id) || 308;

  const [analysis, setAnalysis] = useState<MatchAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [showWhyModal, setShowWhyModal] = useState<boolean>(false);

  useEffect(() => {
    async function loadAnalysis() {
      setLoading(true);
      try {
        const data = await fetchMatchAnalysis(matchId);
        setAnalysis(data);
      } catch (err) {
        console.error("Failed to load match analysis:", err);
      } finally {
        setLoading(false);
      }
    }
    loadAnalysis();
  }, [matchId]);

  if (loading || !analysis) {
    return (
      <div className="py-20 text-center space-y-4">
        <div className="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="text-slate-400 text-sm">Đang tính toán ma trận xác suất và phân tích mô hình...</p>
      </div>
    );
  }

  const hTeam = analysis.home_team.name;
  const aTeam = analysis.away_team.name;

  return (
    <div className="space-y-6">
      {/* Back button */}
      <Link
        href="/"
        className="inline-flex items-center space-x-1.5 text-xs text-slate-400 hover:text-emerald-400 font-medium transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Quay lại danh sách trận đấu</span>
      </Link>

      {/* Match Header Hero Card */}
      <div className="rounded-3xl bg-slate-900/90 border border-slate-800 p-6 sm:p-8 shadow-2xl relative overflow-hidden">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 font-semibold text-xs uppercase tracking-wider">
              {analysis.league.name}
            </span>
            <span className="text-xs text-slate-500">•</span>
            <span className="text-xs text-slate-400">
              {new Date(analysis.date).toLocaleDateString("vi-VN", { weekday: "long", day: "2-digit", month: "2-digit", year: "numeric" })}
            </span>
          </div>
          <span className="text-xs font-mono text-slate-500">Match Analysis Center</span>
        </div>

        {/* Head-to-Head Banner */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 items-center py-6">
          {/* Home */}
          <div className="flex items-center space-x-4">
            <div className="w-14 h-14 rounded-2xl bg-emerald-950/60 border border-emerald-500/40 flex items-center justify-center text-xl font-bold text-emerald-400 shadow-lg shadow-emerald-950/40">
              {hTeam.slice(0, 1)}
            </div>
            <div>
              <h2 className="text-xl sm:text-2xl font-extrabold text-white leading-tight">{hTeam}</h2>
              <div className="flex items-center space-x-2 text-xs text-slate-400 mt-1">
                <span>Elo: <strong className="text-slate-200">{Math.round(analysis.home_team.elo || 1500)}</strong></span>
                <span>•</span>
                <span>Pi(H): <strong className="text-emerald-400">{(analysis.home_team.pi_home || 0).toFixed(2)}</strong></span>
              </div>
            </div>
          </div>

          {/* VS & Score Badge */}
          <div className="text-center">
            <div className="inline-block px-4 py-2 rounded-2xl bg-slate-800/80 border border-slate-700/80">
              <span className="text-xs text-slate-400 uppercase tracking-widest font-semibold block">Sắp diễn ra</span>
              <span className="text-lg font-bold text-slate-300 font-mono">VS</span>
            </div>
          </div>

          {/* Away */}
          <div className="flex items-center justify-start sm:justify-end space-x-4 text-left sm:text-right">
            <div>
              <h2 className="text-xl sm:text-2xl font-extrabold text-white leading-tight">{aTeam}</h2>
              <div className="flex items-center sm:justify-end space-x-2 text-xs text-slate-400 mt-1">
                <span>Elo: <strong className="text-slate-200">{Math.round(analysis.away_team.elo || 1500)}</strong></span>
                <span>•</span>
                <span>Pi(A): <strong className="text-sky-400">{(analysis.away_team.pi_away || 0).toFixed(2)}</strong></span>
              </div>
            </div>
            <div className="w-14 h-14 rounded-2xl bg-sky-950/60 border border-sky-500/40 flex items-center justify-center text-xl font-bold text-sky-400 shadow-lg shadow-sky-950/40">
              {aTeam.slice(0, 1)}
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex overflow-x-auto gap-2 border-b border-slate-800 pb-2">
        {[
          { id: "overview", label: "Tổng Quan & Tips", icon: Award },
          { id: "calculator", label: "Nhập Odds Thủ Công (Góc/Thẻ)", icon: Calculator },
          { id: "heatmap", label: "Ma Trận Tỉ Số", icon: Activity },
          { id: "radar", label: "Radar So Sánh", icon: BarChart2 },
          { id: "form", label: "Phong Độ 10 Trận", icon: Users },
          { id: "line_movement", label: "Biến Động Kèo", icon: TrendingUp },
          { id: "models", label: "Ensemble Models", icon: Layers },
          { id: "odds", label: "So Sánh Nhà Cái", icon: Flame },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                isActive
                  ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/30"
                  : "bg-slate-900/60 text-slate-400 hover:text-white hover:bg-slate-800"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* TAB CONTENT 1: OVERVIEW & TIPS */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* Active Tips Section */}
          <div className="space-y-4">
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <Award className="w-4 h-4 text-emerald-400" />
              <span>Gợi Ý Định Lượng Có Lợi Thế (+EV)</span>
            </h3>

            {analysis.tips && analysis.tips.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {analysis.tips.map((tip) => (
                  <div
                    key={tip.id}
                    className="p-5 rounded-2xl bg-slate-900/90 border border-emerald-500/30 space-y-3 shadow-xl"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="text-base font-bold text-emerald-400">
                          {tip.selection}
                        </span>
                        <span className="font-mono font-bold text-sm text-white px-2 py-0.5 bg-emerald-500/20 rounded">
                          @{tip.odds}
                        </span>
                      </div>
                      <span className="px-2 py-0.5 rounded text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                        Độ tin cậy: Hạng {tip.confidence_grade}
                      </span>
                    </div>

                    <div className="grid grid-cols-3 gap-2 p-3 rounded-xl bg-slate-800/50 border border-slate-800 text-xs text-center">
                      <div>
                        <span className="text-slate-400 block text-[10px]">Xác suất Mô Hình</span>
                        <strong className="text-emerald-400 text-sm font-mono">
                          {Math.round(tip.model_prob * 100)}%
                        </strong>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px]">Thị Trường (De-vig)</span>
                        <strong className="text-slate-300 text-sm font-mono">
                          {Math.round(tip.fair_prob * 100)}%
                        </strong>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px]">Lợi thế & EV</span>
                        <strong className="text-emerald-400 text-sm font-mono">
                          +{Math.round(tip.ev * 1000) / 10}%
                        </strong>
                      </div>
                    </div>

                    {/* Kelly Sizing */}
                    <div className="flex items-center justify-between text-xs text-slate-300 bg-slate-800/30 px-3 py-2 rounded-xl border border-slate-800">
                      <span>Mức cược mô phỏng (1/4 Kelly):</span>
                      <strong className="text-emerald-400 font-mono">
                        {Math.round(tip.stake_suggestion * 1000) / 10}% Virtual Bankroll
                      </strong>
                    </div>

                    {/* Reasons list */}
                    <div className="space-y-1.5 pt-1">
                      <span className="text-xs text-slate-400 font-semibold block">Lý do định lượng:</span>
                      <ul className="space-y-1">
                        {tip.reasons.map((r, i) => (
                          <li key={i} className="text-xs text-slate-300 flex items-start space-x-1.5">
                            <span className="text-emerald-400 font-bold shrink-0">•</span>
                            <span>{r}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {tip.risk_warning && (
                      <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs text-amber-300 flex items-start space-x-2">
                        <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                        <span>{tip.risk_warning}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 text-center space-y-2">
                <p className="text-sm text-slate-300 font-semibold">NO BET / Trận Này Không Đủ Edge Để Phát Tip</p>
                <p className="text-xs text-slate-400">
                  Mô hình tuân thủ nguyên tắc trung thực: chỉ ra tip khi có bằng chứng thống kê vững chắc (+EV &gt; 3%).
                </p>
              </div>
            )}
          </div>

          {/* Markets Evaluated as NO-BET */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
            <h4 className="text-xs uppercase font-bold text-slate-400 tracking-wider">
              Danh Sách Kèo Đã Đánh Giá & Bị Loại (NO BET)
            </h4>
            <div className="space-y-2">
              {analysis.no_bet_evaluations.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-2.5 rounded-xl bg-slate-800/40 text-xs border border-slate-800/60">
                  <span className="font-semibold text-slate-300">{item.market}</span>
                  <span className="text-slate-400 italic">{item.reason}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Manual Odds Calculator for Corners / Cards */}
          <ManualOddsCalculator homeTeam={hTeam} awayTeam={aTeam} />

          {/* Quick Score Heatmap summary */}
          <ScoreHeatmap scoreData={analysis.score_matrix} homeTeam={hTeam} awayTeam={aTeam} />
        </div>
      )}

      {/* TAB CONTENT: MANUAL ODDS CALCULATOR */}
      {activeTab === "calculator" && (
        <ManualOddsCalculator homeTeam={hTeam} awayTeam={aTeam} />
      )}

      {/* TAB CONTENT 2: SCORE MATRIX */}
      {activeTab === "heatmap" && (
        <ScoreHeatmap scoreData={analysis.score_matrix} homeTeam={hTeam} awayTeam={aTeam} />
      )}

      {/* TAB CONTENT 3: RADAR CHART */}
      {activeTab === "radar" && (
        <RadarChartComponent data={analysis.radar_comparison} homeTeam={hTeam} awayTeam={aTeam} />
      )}

      {/* TAB CONTENT 4: FORM STATS */}
      {activeTab === "form" && (
        <FormChart homeForm={analysis.home_form} awayForm={analysis.away_form} />
      )}

      {/* TAB CONTENT 5: LINE MOVEMENT */}
      {activeTab === "line_movement" && (
        <LineMovementChart movements={analysis.line_movements} />
      )}

      {/* TAB CONTENT 6: ENSEMBLE MODELS & SHAP */}
      {activeTab === "models" && (
        <div className="space-y-6">
          {/* Models Breakdown Table */}
          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4">
            <div className="border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white">So Sánh Xác Suất Giữa Các Mô Hình</h3>
              <p className="text-xs text-slate-400">
                Đối chiếu kết quả giữa Maher Poisson, Dixon-Coles rho correlation, Elo/Pi và Stacking Ensemble.
              </p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-800/80 text-slate-300 font-semibold uppercase text-[10px]">
                  <tr>
                    <th className="p-3">Mô Hình</th>
                    <th className="p-3 text-center">{hTeam} Thắng (1)</th>
                    <th className="p-3 text-center">Hòa (X)</th>
                    <th className="p-3 text-center">{aTeam} Thắng (2)</th>
                    <th className="p-3 text-center">Tài 2.5</th>
                    <th className="p-3 text-center">Xỉu 2.5</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 font-mono">
                  {analysis.model_breakdown.map((m, i) => (
                    <tr key={i} className="hover:bg-slate-800/30">
                      <td className="p-3 font-sans font-semibold text-slate-200">{m.model_name}</td>
                      <td className="p-3 text-center text-emerald-400 font-bold">{m.home_win}%</td>
                      <td className="p-3 text-center text-amber-300">{m.draw}%</td>
                      <td className="p-3 text-center text-sky-400">{m.away_win}%</td>
                      <td className="p-3 text-center text-purple-400">{m.over_25}%</td>
                      <td className="p-3 text-center text-slate-300">{m.under_25}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* SHAP Feature Importance */}
          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4">
            <div className="border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white">Yếu Tố Trọng Yếu Tác Động Dự Đoán (SHAP / GBDT)</h3>
              <p className="text-xs text-slate-400">Mức độ đóng góp của từng thuộc tính vào dự đoán trận đấu.</p>
            </div>

            <div className="space-y-3">
              {analysis.shap_features.map((item, idx) => (
                <div key={idx} className="space-y-1 text-xs">
                  <div className="flex justify-between text-slate-300 font-medium">
                    <span>{item.feature}</span>
                    <span className="font-mono text-emerald-400">{Math.round(item.importance * 100)}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-800 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-emerald-600 to-teal-400 rounded-full"
                      style={{ width: `${item.importance * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT 7: BOOKMAKER ODDS COMPARISON */}
      {activeTab === "odds" && (
        <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4">
          <div className="border-b border-slate-800 pb-3">
            <h3 className="text-base font-bold text-white">Bảng So Sánh Odds & Tìm Best Price</h3>
            <p className="text-xs text-slate-400">
              Đối chiếu tỉ lệ giữa các nhà cái và đánh giá margin biên lợi nhuận.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-800/80 text-slate-300 font-semibold uppercase text-[10px]">
                <tr>
                  <th className="p-3">Nhà Cái</th>
                  <th className="p-3 text-center">{hTeam} (1)</th>
                  <th className="p-3 text-center">Hòa (X)</th>
                  <th className="p-3 text-center">{aTeam} (2)</th>
                  <th className="p-3 text-center">Margin (%)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 font-mono">
                {analysis.odds_comparison.map((b, i) => (
                  <tr key={i} className="hover:bg-slate-800/30">
                    <td className="p-3 font-sans font-semibold text-slate-200">{b.bookmaker}</td>
                    <td className={`p-3 text-center ${b.is_best_home ? "text-emerald-400 font-bold bg-emerald-950/20" : "text-slate-300"}`}>
                      {b.home}
                    </td>
                    <td className="p-3 text-center text-slate-300">{b.draw}</td>
                    <td className="p-3 text-center text-slate-300">{b.away}</td>
                    <td className="p-3 text-center text-slate-400">{b.margin_pct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
