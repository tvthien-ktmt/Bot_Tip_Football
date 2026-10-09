"use client";

import React from "react";
import { LineMovementPoint } from "@/lib/types";
import { TrendingUp, Flame, AlertCircle } from "lucide-react";

interface LineMovementProps {
  movements: LineMovementPoint[];
}

export default function LineMovementChart({ movements }: LineMovementProps) {
  if (!movements || movements.length === 0) {
    return (
      <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 text-center text-slate-500 text-xs">
        Chưa có dữ liệu biến động kèo theo thời gian cho trận đấu này.
      </div>
    );
  }

  return (
    <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            <span>Biến Động Kèo & Dòng Tiền (Line Movement)</span>
          </h3>
          <p className="text-xs text-slate-400">
            Theo dõi xu hướng điều chỉnh giá từ lúc mở kèo đến hiện tại.
          </p>
        </div>
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 text-xs">
          <Flame className="w-3.5 h-3.5 text-amber-400" />
          <span>Steam Move Detection</span>
        </div>
      </div>

      <div className="space-y-2">
        {movements.map((m, idx) => (
          <div
            key={idx}
            className="flex items-center justify-between p-3 rounded-xl bg-slate-800/40 border border-slate-800 text-xs hover:border-slate-700 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <span className="text-slate-500 font-mono w-16">{m.timestamp}</span>
              <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-medium">
                {m.bookmaker}
              </span>
              <span className="text-white font-semibold">
                {m.selection} {m.line !== undefined && m.line !== null ? `(${m.line > 0 ? "+" + m.line : m.line})` : ""}
              </span>
            </div>

            <div className="flex items-center space-x-3">
              {m.movement_type === "steam" && (
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center space-x-1">
                  <Flame className="w-3 h-3" />
                  <span>Dòng Tiền Đổ Mạnh</span>
                </span>
              )}
              <span className="font-mono text-sm font-bold text-emerald-400">
                @{m.odds.toFixed(2)}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="flex items-start space-x-2 p-2.5 rounded-xl bg-slate-800/20 text-[11px] text-slate-400">
        <AlertCircle className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
        <span>
          Lưu ý: Nếu không có dữ liệu khối lượng tiền thật từ sàn betting exchange, phân tích chỉ dựa trên độ dịch chuyển giá mở cửa so với giá hiện tại.
        </span>
      </div>
    </div>
  );
}
