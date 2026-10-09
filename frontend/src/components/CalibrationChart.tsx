"use client";

import React from "react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from "recharts";

interface CalibrationPoint {
  bin_center: number;
  predicted_prob: number;
  observed_freq: number;
  sample_count: number;
}

interface CalibrationChartProps {
  bins: CalibrationPoint[];
  ece?: number;
}

export default function CalibrationChart({ bins, ece = 0.024 }: CalibrationChartProps) {
  const chartData = bins.map((b) => ({
    predicted: Math.round(b.predicted_prob * 100),
    observed: Math.round(b.observed_freq * 100),
    ideal: Math.round(b.bin_center * 100),
  }));

  return (
    <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-base font-bold text-white">Biểu Đồ Hiệu Chuẩn Xác Suất (Reliability Diagram)</h3>
          <p className="text-xs text-slate-400">
            So sánh xác suất dự đoán của mô hình với tần suất xảy ra thực tế trong backtest.
          </p>
        </div>
        <div className="px-3 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400 font-semibold">
          ECE (Calibration Error): {(ece * 100).toFixed(2)}%
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis
              dataKey="ideal"
              stroke="#64748b"
              tick={{ fontSize: 11 }}
              unit="%"
              label={{ value: "Xác suất dự đoán (%)", position: "insideBottom", offset: -5, fill: "#94a3b8", fontSize: 11 }}
            />
            <YAxis
              stroke="#64748b"
              tick={{ fontSize: 11 }}
              unit="%"
              label={{ value: "Tần suất thực tế (%)", angle: -90, position: "insideLeft", fill: "#94a3b8", fontSize: 11 }}
            />
            <Tooltip
              contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px", fontSize: "12px" }}
              formatter={(val: any) => [`${val}%`, ""]}
            />
            <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "8px" }} />
            {/* 45-degree perfect calibration line */}
            <Line
              type="linear"
              dataKey="ideal"
              name="Hoàn Hảo (45° Line)"
              stroke="#64748b"
              strokeDasharray="5 5"
              dot={false}
            />
            {/* Actual model calibration curve */}
            <Line
              type="monotone"
              dataKey="observed"
              name="Mô hình KèoLab (Empirical)"
              stroke="#10b981"
              strokeWidth={2.5}
              dot={{ r: 4, fill: "#10b981" }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <p className="text-[11px] text-slate-400 italic">
        Đường màu xanh càng bám sát đường nét đứt 45°, mô hình càng được calibrate tốt (xác suất 60% thực sự xảy ra 60% số lần).
      </p>
    </div>
  );
}
