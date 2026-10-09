"use client";

import { useState, useEffect } from "react";
import MatchCard from "@/components/MatchCard";
import DemoBanner from "@/components/DemoBanner";
import { MatchCard as MatchCardType } from "@/lib/types";
import { fetchFixtures, getIsDemoData } from "@/lib/api";
import { Search, Filter, ShieldCheck, Activity, Award, CheckCircle2, AlertCircle } from "lucide-react";

export default function DashboardPage() {
  const [fixtures, setFixtures] = useState<MatchCardType[]>([]);
  const [isDemo, setIsDemo] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selectedLeague, setSelectedLeague] = useState<string>("ALL");
  const [tipFilter, setTipFilter] = useState<"ALL" | "TIPS_ONLY" | "NO_BET">("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const data = await fetchFixtures(selectedLeague);
        setFixtures(data);
        setIsDemo(getIsDemoData());
      } catch (err) {
        console.error("Error loading fixtures:", err);
        setIsDemo(true);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [selectedLeague]);

  // Client-side filtering
  const filteredMatches = fixtures.filter((m) => {
    // Search query
    const matchSearch =
      m.home_team.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.away_team.name.toLowerCase().includes(searchQuery.toLowerCase());
    if (!matchSearch) return false;

    // Tip status filter
    if (tipFilter === "TIPS_ONLY") {
      return !m.is_no_bet && m.top_tip !== null;
    }
    if (tipFilter === "NO_BET") {
      return m.is_no_bet || m.top_tip === null;
    }
    return true;
  });

  const totalMatches = fixtures.length;
  const tipCount = fixtures.filter((f) => !f.is_no_bet && f.top_tip !== null).length;
  const noBetCount = totalMatches - tipCount;

  return (
    <div className="space-y-8">
      <DemoBanner show={isDemo} />
      {/* Top Banner & Philosophy */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-slate-800 to-emerald-950/40 border border-slate-800 p-6 sm:p-8 shadow-2xl">
        <div className="relative z-10 max-w-3xl space-y-3">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Walk-Forward Backtested • De-Vigged Odds • Kelly Risk Sizing</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            Kèo<span className="text-emerald-400">Lab</span> – Football Tip Analyzer
          </h1>
          <p className="text-slate-300 text-xs sm:text-sm leading-relaxed">
            Hệ thống phân tích định lượng xác suất thể thao phục vụ giải trí và nghiên cứu học thuật. Chỉ gợi ý khi mô hình tìm thấy <strong>Lợi thế toán học (+EV &gt; 3%)</strong> sau khi loại bỏ margin nhà cái. Tuyệt đối không ép tip cho mọi trận.
          </p>
        </div>
      </div>

      {/* Summary Stat Counters */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center text-slate-300">
            <Activity className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <span className="text-[11px] text-slate-400 block">Tổng Trận Sắp Đá</span>
            <strong className="text-xl font-bold text-white">{totalMatches}</strong>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-950/60 flex items-center justify-center text-emerald-400 border border-emerald-500/20">
            <Award className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] text-slate-400 block">Cơ Hội Có Edge (+EV)</span>
            <strong className="text-xl font-bold text-emerald-400">{tipCount}</strong>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-slate-800/80 flex items-center justify-center text-slate-400">
            <AlertCircle className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <span className="text-[11px] text-slate-400 block">Trận Bỏ Qua (NO BET)</span>
            <strong className="text-xl font-bold text-slate-300">{noBetCount}</strong>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center text-purple-400">
            <ShieldCheck className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <span className="text-[11px] text-slate-400 block">Brier Score Backtest</span>
            <strong className="text-xl font-bold text-purple-300 font-mono">0.338</strong>
          </div>
        </div>
      </div>

      {/* Filters and Search Bar */}
      <div className="p-4 rounded-2xl bg-slate-900/70 border border-slate-800 flex flex-col md:flex-row gap-4 justify-between items-stretch md:items-center">
        {/* League Selector */}
        <div className="flex flex-wrap gap-1.5">
          {[
            { code: "ALL", label: "Tất cả giải" },
            { code: "E0", label: "Premier League" },
            { code: "E1", label: "Championship" },
            { code: "SP1", label: "La Liga" },
            { code: "I1", label: "Serie A" },
            { code: "D1", label: "Bundesliga" },
          ].map((lg) => (
            <button
              key={lg.code}
              onClick={() => setSelectedLeague(lg.code)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                selectedLeague === lg.code
                  ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/30"
                  : "bg-slate-800/80 text-slate-300 hover:bg-slate-800 hover:text-white"
              }`}
            >
              {lg.label}
            </button>
          ))}
        </div>

        {/* Tip status filter & Search */}
        <div className="flex flex-col sm:flex-row gap-2">
          {/* Tip Status Filter */}
          <div className="inline-flex rounded-xl bg-slate-800/80 p-1 border border-slate-700">
            <button
              onClick={() => setTipFilter("ALL")}
              className={`px-2.5 py-1 text-xs rounded-lg font-medium transition-colors ${
                tipFilter === "ALL" ? "bg-slate-700 text-white" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Tất cả
            </button>
            <button
              onClick={() => setTipFilter("TIPS_ONLY")}
              className={`px-2.5 py-1 text-xs rounded-lg font-medium transition-colors ${
                tipFilter === "TIPS_ONLY" ? "bg-emerald-600 text-white" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Có Tip (+EV)
            </button>
            <button
              onClick={() => setTipFilter("NO_BET")}
              className={`px-2.5 py-1 text-xs rounded-lg font-medium transition-colors ${
                tipFilter === "NO_BET" ? "bg-slate-700 text-white" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              NO BET
            </button>
          </div>

          {/* Search Input */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tìm theo tên đội..."
              className="w-full sm:w-48 pl-9 pr-3 py-1.5 rounded-xl bg-slate-800/90 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>
        </div>
      </div>

      {/* Match Cards Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-64 rounded-2xl bg-slate-900/60 animate-pulse border border-slate-800" />
          ))}
        </div>
      ) : filteredMatches.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredMatches.map((m) => (
            <MatchCard key={m.id} match={m} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 bg-slate-900/40 rounded-3xl border border-slate-800 space-y-2">
          <p className="text-slate-400 text-sm">Không tìm thấy trận đấu nào phù hợp với bộ lọc hiện tại.</p>
          <button
            onClick={() => {
              setSelectedLeague("ALL");
              setTipFilter("ALL");
              setSearchQuery("");
            }}
            className="text-xs text-emerald-400 hover:underline font-semibold"
          >
            Đặt lại bộ lọc
          </button>
        </div>
      )}
    </div>
  );
}
