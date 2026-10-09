"use client";

import Link from "next/link";
import { MatchCard as MatchCardType } from "@/lib/types";
import { ChevronRight, ArrowUpRight, AlertTriangle, ShieldCheck, HelpCircle } from "lucide-react";

interface MatchCardProps {
  match: MatchCardType;
}

export default function MatchCard({ match }: MatchCardProps) {
  const matchDate = new Date(match.date);
  const timeFormatted = matchDate.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });
  const dateFormatted = matchDate.toLocaleDateString("vi-VN", { day: "2-digit", month: "2-digit" });

  const tip = match.top_tip;
  const isNoBet = match.is_no_bet || !tip;

  const getConfidenceBadge = (grade: string) => {
    switch (grade) {
      case "A":
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">Hạng A</span>;
      case "B":
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-sky-500/20 text-sky-400 border border-sky-500/40">Hạng B</span>;
      case "C":
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-amber-500/20 text-amber-400 border border-amber-500/40">Hạng C</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-slate-500/20 text-slate-400 border border-slate-500/40">Hạng D</span>;
    }
  };

  return (
    <div className="rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-slate-700/80 transition-all p-5 shadow-lg flex flex-col justify-between space-y-4">
      {/* Top Header */}
      <div className="flex items-center justify-between text-xs text-slate-400 border-b border-slate-800/80 pb-3">
        <div className="flex items-center space-x-2">
          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-semibold uppercase tracking-wider text-[11px]">
            {match.league.name}
          </span>
          <span>•</span>
          <span className="font-medium text-slate-300">{dateFormatted} {timeFormatted}</span>
        </div>
        <span className="text-[11px] text-slate-500 font-mono">ID #{match.id}</span>
      </div>

      {/* Teams Row */}
      <div className="grid grid-cols-2 gap-4 items-center">
        {/* Home */}
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded-full bg-emerald-950/60 border border-emerald-500/30 flex items-center justify-center text-xs font-bold text-emerald-400">
              {match.home_team.name.slice(0, 1)}
            </div>
            <div>
              <h4 className="font-bold text-white text-sm sm:text-base leading-tight">
                {match.home_team.name}
              </h4>
              <span className="text-[11px] text-slate-400">
                Elo {match.home_team.elo ? Math.round(match.home_team.elo) : 1500}
              </span>
            </div>
          </div>
        </div>

        {/* Away */}
        <div className="space-y-1 text-right">
          <div className="flex items-center justify-end space-x-2">
            <div>
              <h4 className="font-bold text-white text-sm sm:text-base leading-tight">
                {match.away_team.name}
              </h4>
              <span className="text-[11px] text-slate-400">
                Elo {match.away_team.elo ? Math.round(match.away_team.elo) : 1500}
              </span>
            </div>
            <div className="w-7 h-7 rounded-full bg-sky-950/60 border border-sky-500/30 flex items-center justify-center text-xs font-bold text-sky-400">
              {match.away_team.name.slice(0, 1)}
            </div>
          </div>
        </div>
      </div>

      {/* Market Odds Quick Bar */}
      <div className="grid grid-cols-3 gap-2 text-center text-xs py-2 px-3 rounded-xl bg-slate-800/40 border border-slate-800">
        <div>
          <span className="text-slate-500 block text-[10px]">Chủ (1)</span>
          <span className="font-mono font-semibold text-slate-300">{match.b365_home_odds || "—"}</span>
        </div>
        <div>
          <span className="text-slate-500 block text-[10px]">Hòa (X)</span>
          <span className="font-mono font-semibold text-slate-300">{match.b365_draw_odds || "—"}</span>
        </div>
        <div>
          <span className="text-slate-500 block text-[10px]">Khách (2)</span>
          <span className="font-mono font-semibold text-slate-300">{match.b365_away_odds || "—"}</span>
        </div>
      </div>

      {/* TIP OR NO-BET SECTION */}
      {isNoBet ? (
        <div className="p-3.5 rounded-xl bg-slate-800/30 border border-slate-800 text-center space-y-1.5">
          <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
            <span>NO BET / BỎ QUA TRẬN NÀY</span>
          </div>
          <p className="text-xs text-slate-400">
            {match.no_bet_reason || "Tỉ lệ nhà cái đã sát với phân phối xác suất. Không tìm thấy edge +EV."}
          </p>
        </div>
      ) : (
        <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/30 space-y-2.5">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold text-emerald-400 uppercase tracking-wide">
                Gợi Ý: {tip?.selection}
              </span>
              <span className="font-mono font-bold text-white text-xs px-2 py-0.5 bg-emerald-500/20 rounded">
                @{tip?.odds}
              </span>
            </div>
            {tip && getConfidenceBadge(tip.confidence_grade)}
          </div>

          <div className="grid grid-cols-3 gap-2 text-[11px] pt-1 border-t border-emerald-500/20">
            <div>
              <span className="text-slate-400 block text-[10px]">Mô hình vs TT</span>
              <span className="font-semibold text-emerald-300 font-mono">
                {Math.round((tip?.model_prob || 0) * 100)}% vs {Math.round((tip?.fair_prob || 0) * 100)}%
              </span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">Giá trị kỳ vọng</span>
              <span className="font-semibold text-emerald-400 font-mono">
                +{Math.round((tip?.ev || 0) * 1000) / 10}% EV
              </span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">Kelly 1/4 ảo</span>
              <span className="font-semibold text-slate-200 font-mono">
                {Math.round((tip?.stake_suggestion || 0) * 1000) / 10}%
              </span>
            </div>
          </div>

          {tip?.risk_warning && (
            <div className="flex items-center space-x-1.5 text-[11px] text-amber-300 bg-amber-500/10 p-1.5 rounded border border-amber-500/20">
              <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
              <span>{tip.risk_warning}</span>
            </div>
          )}
        </div>
      )}

      {/* Link to Match Center */}
      <Link
        href={`/match/${match.id}`}
        className="w-full py-2.5 px-4 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-emerald-600 text-slate-200 hover:text-white transition-all flex items-center justify-center space-x-1 group"
      >
        <span>Xem Toàn Bộ Phân Tích (Match Center)</span>
        <ChevronRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
      </Link>
    </div>
  );
}
