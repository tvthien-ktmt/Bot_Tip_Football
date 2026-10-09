"use client";

import React, { useState } from "react";
import { ScoreMatrixData } from "@/lib/types";

interface ScoreHeatmapProps {
  scoreData: ScoreMatrixData;
  homeTeam: string;
  awayTeam: string;
}

export default function ScoreHeatmap({ scoreData, homeTeam, awayTeam }: ScoreHeatmapProps) {
  const [hoveredCell, setHoveredCell] = useState<{ h: number; a: number; p: number } | null>(null);

  const matrix = scoreData.matrix || [];
  const maxP = Math.max(...matrix.flat(), 0.001);

  // Helper for background color intensity
  const getCellColor = (prob: number) => {
    const ratio = prob / maxP;
    if (ratio < 0.05) return "bg-slate-900 text-slate-500";
    if (ratio < 0.2) return "bg-teal-950/60 text-teal-300";
    if (ratio < 0.45) return "bg-teal-900/80 text-teal-200";
    if (ratio < 0.75) return "bg-emerald-800 text-emerald-100 font-semibold";
    return "bg-emerald-600 text-white font-bold ring-2 ring-emerald-400";
  };

  return (
    <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <span>Ma Trận Xác Suất Tỉ Số (Dixon-Coles & Poisson)</span>
          </h3>
          <p className="text-xs text-slate-400">
            Trục tung: <span className="text-emerald-400 font-semibold">{homeTeam}</span> • Trục hoành: <span className="text-sky-400 font-semibold">{awayTeam}</span>
          </p>
        </div>
        <div className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-400 flex items-center space-x-2">
          <span>Tỉ số dễ xảy ra nhất:</span>
          <strong className="text-white text-sm">{scoreData.max_score}</strong>
          <span className="text-[11px] opacity-80">({scoreData.max_prob}%)</span>
        </div>
      </div>

      {/* Matrix Grid */}
      <div className="overflow-x-auto pb-2">
        <div className="min-w-[420px] max-w-[540px] mx-auto">
          {/* Away goals header label */}
          <div className="text-center text-xs text-sky-400 font-semibold mb-1">
            Bàn thắng của {awayTeam} →
          </div>

          <div className="grid grid-cols-8 gap-1.5 text-center text-xs">
            {/* Top-left corner */}
            <div className="h-8 flex items-center justify-center font-bold text-slate-500">
              H \ A
            </div>
            {[0, 1, 2, 3, 4, 5, 6].map((col) => (
              <div key={`col-${col}`} className="h-8 flex items-center justify-center font-bold text-slate-300 bg-slate-800/60 rounded">
                {col}
              </div>
            ))}

            {/* Matrix rows */}
            {matrix.map((row, h) => (
              <React.Fragment key={`row-${h}`}>
                <div className="h-9 flex items-center justify-center font-bold text-emerald-400 bg-slate-800/60 rounded">
                  {h}
                </div>
                {row.map((prob, a) => {
                  const probPct = (prob * 100).toFixed(1);
                  const isMax = `${h} - ${a}` === scoreData.max_score;
                  return (
                    <div
                      key={`cell-${h}-${a}`}
                      onMouseEnter={() => setHoveredCell({ h, a, p: prob })}
                      onMouseLeave={() => setHoveredCell(null)}
                      className={`h-9 rounded flex flex-col items-center justify-center cursor-pointer heatmap-cell transition-all ${getCellColor(prob)}`}
                      title={`${homeTeam} ${h} - ${a} ${awayTeam}: ${probPct}%`}
                    >
                      <span className="text-[11px] leading-tight">{probPct}%</span>
                      {isMax && <span className="w-1 h-1 rounded-full bg-white mt-0.5"></span>}
                    </div>
                  );
                })}
              </React.Fragment>
            ))}
          </div>

          <div className="text-left text-xs text-emerald-400 font-semibold mt-1">
            ↑ Bàn thắng của {homeTeam}
          </div>
        </div>
      </div>

      {/* Hover Status */}
      {hoveredCell && (
        <div className="text-center py-1.5 px-3 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-200">
          Tỉ số: <strong className="text-emerald-400">{homeTeam} {hoveredCell.h}</strong> - <strong className="text-sky-400">{hoveredCell.a} {awayTeam}</strong>: Xác suất <span className="font-bold text-white">{(hoveredCell.p * 100).toFixed(2)}%</span>
        </div>
      )}

      {/* Derived Market Summary Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-800">
        <div className="p-2.5 rounded-xl bg-slate-800/60 border border-slate-800 text-center">
          <span className="text-[11px] text-slate-400 block">Chủ Nhà Thắng (1)</span>
          <strong className="text-sm text-emerald-400">{scoreData.p_home_win}%</strong>
        </div>
        <div className="p-2.5 rounded-xl bg-slate-800/60 border border-slate-800 text-center">
          <span className="text-[11px] text-slate-400 block">Hòa (X)</span>
          <strong className="text-sm text-amber-300">{scoreData.p_draw}%</strong>
        </div>
        <div className="p-2.5 rounded-xl bg-slate-800/60 border border-slate-800 text-center">
          <span className="text-[11px] text-slate-400 block">Khách Thắng (2)</span>
          <strong className="text-sm text-sky-400">{scoreData.p_away_win}%</strong>
        </div>
        <div className="p-2.5 rounded-xl bg-slate-800/60 border border-slate-800 text-center">
          <span className="text-[11px] text-slate-400 block">Tài 2.5 (Over)</span>
          <strong className="text-sm text-purple-400">{scoreData.p_over_25}%</strong>
        </div>
      </div>
    </div>
  );
}
