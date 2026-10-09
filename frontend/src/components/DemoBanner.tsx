"use client";

import { AlertTriangle } from "lucide-react";

interface DemoBannerProps {
  show?: boolean;
}

export default function DemoBanner({ show = false }: DemoBannerProps) {
  if (!show) return null;

  return (
    <div className="w-full bg-amber-500 text-slate-950 px-4 py-3 font-semibold text-sm shadow-lg border-b-2 border-amber-600 flex items-center justify-center space-x-3 sticky top-0 z-50 animate-pulse">
      <AlertTriangle className="w-5 h-5 flex-shrink-0 text-slate-950" />
      <span className="text-center">
        ⚠️ <strong>ĐANG HIỂN THỊ DỮ LIỆU DEMO</strong> — Backend không phản hồi. Các trận đấu và kết quả dưới đây là dữ liệu giả lập (Demo United, Synthetic City...). Khởi chạy backend FastAPI tại <code className="bg-amber-600/30 px-1 py-0.5 rounded text-xs font-mono">http://localhost:8000</code> để xem dữ liệu thật.
      </span>
    </div>
  );
}
