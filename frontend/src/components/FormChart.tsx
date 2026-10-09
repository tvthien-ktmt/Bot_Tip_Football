"use client";

import React from "react";
import { TeamFormStats } from "@/lib/types";

interface FormChartProps {
  homeForm: TeamFormStats;
  awayForm: TeamFormStats;
}

export default function FormChart({ homeForm, awayForm }: FormChartProps) {
  const renderBadge = (res: "W" | "D" | "L") => {
    if (res === "W") return <span className="w-5 h-5 rounded flex items-center justify-center text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">W</span>;
    if (res === "D") return <span className="w-5 h-5 rounded flex items-center justify-center text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/40">D</span>;
    return <span className="w-5 h-5 rounded flex items-center justify-center text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/40">L</span>;
  };

  return (
    <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-5">
      <div className="border-b border-slate-800 pb-3">
        <h3 className="text-base font-bold text-white">Phong Độ & Số Liệu 10 Trận Gần Nhất</h3>
        <p className="text-xs text-slate-400">So sánh hiệu suất bàn thắng, phạt góc, thẻ phạt và chuỗi kết quả.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Home Team Form */}
        <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="font-bold text-emerald-400 text-sm">{homeForm.team_name}</h4>
            <div className="flex space-x-1">
              {homeForm.last_10_matches.slice(0, 5).map((m, i) => (
                <span key={i} title={`${m.date} vs ${m.opponent} (${m.score})`}>
                  {renderBadge(m.result)}
                </span>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2 text-center text-xs">
            <div className="p-2 rounded bg-slate-800/80">
              <span className="text-slate-400 block text-[10px]">Bàn ghi/trận</span>
              <strong className="text-white text-sm">{homeForm.avg_goals_scored}</strong>
            </div>
            <div className="p-2 rounded bg-slate-800/80">
              <span className="text-slate-400 block text-[10px]">Bàn lọt/trận</span>
              <strong className="text-white text-sm">{homeForm.avg_goals_conceded}</strong>
            </div>
            <div className="p-2 rounded bg-slate-800/80">
              <span className="text-slate-400 block text-[10px]">Góc trung bình</span>
              <strong className="text-white text-sm">{homeForm.avg_corners}</strong>
            </div>
          </div>

          <div className="flex justify-between text-xs text-slate-400 pt-1">
            <span>Giữ sạch lưới: <strong className="text-emerald-400">{homeForm.clean_sheet_rate}%</strong></span>
            <span>Tịt ngòi: <strong className="text-rose-400">{homeForm.failed_to_score_rate}%</strong></span>
          </div>
        </div>

        {/* Away Team Form */}
        <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="font-bold text-sky-400 text-sm">{awayForm.team_name}</h4>
            <div className="flex space-x-1">
              {awayForm.last_10_matches.slice(0, 5).map((m, i) => (
                <span key={i} title={`${m.date} vs ${m.opponent} (${m.score})`}>
                  {renderBadge(m.result)}
                </span>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2 text-center text-xs">
            <div className="p-2 rounded bg-slate-800/80">
              <span className="text-slate-400 block text-[10px]">Bàn ghi/trận</span>
              <strong className="text-white text-sm">{awayForm.avg_goals_scored}</strong>
            </div>
            <div className="p-2 rounded bg-slate-800/80">
              <span className="text-slate-400 block text-[10px]">Bàn lọt/trận</span>
              <strong className="text-white text-sm">{awayForm.avg_goals_conceded}</strong>
            </div>
            <div className="p-2 rounded bg-slate-800/80">
              <span className="text-slate-400 block text-[10px]">Góc trung bình</span>
              <strong className="text-white text-sm">{awayForm.avg_corners}</strong>
            </div>
          </div>

          <div className="flex justify-between text-xs text-slate-400 pt-1">
            <span>Giữ sạch lưới: <strong className="text-emerald-400">{awayForm.clean_sheet_rate}%</strong></span>
            <span>Tịt ngòi: <strong className="text-rose-400">{awayForm.failed_to_score_rate}%</strong></span>
          </div>
        </div>
      </div>
    </div>
  );
}
