"use client";

import React from "react";
import { Radar, RadarChart as RechartsRadar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { RadarMetric } from "@/lib/types";

interface RadarChartProps {
  data: RadarMetric[];
  homeTeam: string;
  awayTeam: string;
}

export default function RadarChartComponent({ data, homeTeam, awayTeam }: RadarChartProps) {
  return (
    <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4">
      <div className="border-b border-slate-800 pb-3">
        <h3 className="text-base font-bold text-white">Radar So Sánh Thực Lực & Phong Cách</h3>
        <p className="text-xs text-slate-400">
          Chỉ số chuẩn hóa (0-100) theo tấn công, phòng ngự, xG, bóng chết, kỷ luật và Elo.
        </p>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <RechartsRadar data={data}>
            <PolarGrid stroke="#334155" />
            <PolarAngleAxis dataKey="metric" stroke="#94a3b8" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" tick={{ fill: "#64748b", fontSize: 10 }} />
            <Radar
              name={homeTeam}
              dataKey="home"
              stroke="#10b981"
              fill="#10b981"
              fillOpacity={0.4}
            />
            <Radar
              name={awayTeam}
              dataKey="away"
              stroke="#38bdf8"
              fill="#38bdf8"
              fillOpacity={0.3}
            />
            <Tooltip
              contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px", fontSize: "12px" }}
            />
            <Legend
              wrapperStyle={{ fontSize: "12px", paddingTop: "8px" }}
            />
          </RechartsRadar>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
