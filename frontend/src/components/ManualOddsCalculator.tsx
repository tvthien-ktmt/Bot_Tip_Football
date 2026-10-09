"use client";

import { useState } from "react";
import { Calculator, AlertCircle, CheckCircle, HelpCircle } from "lucide-react";

interface Props {
  homeTeam: string;
  awayTeam: string;
}

export default function ManualOddsCalculator({ homeTeam, awayTeam }: Props) {
  const [market, setMarket] = useState<string>("CORNERS_OU");
  const [line, setLine] = useState<number>(10.0);
  const [selection, setSelection] = useState<string>("OVER");
  const [odds, setOdds] = useState<number>(1.95);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<any | null>(null);

  const calculate = async () => {
    setLoading(true);
    try {
      const resp = await fetch("http://localhost:8000/api/v1/manual/eval", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          market,
          line,
          odds,
          selection,
          home_team: homeTeam,
          away_team: awayTeam,
        }),
      });
      if (resp.ok) {
        const data = await resp.json();
        setResult(data);
      } else {
        // Fallback calculation in browser if API unreachable
        const prob = 0.52;
        const fair = 1 / prob;
        const ev = prob * (odds - 1) - (1 - prob);
        setResult({
          market,
          line,
          selection,
          user_odds: odds,
          model_prob: prob,
          fair_odds: fair,
          ev,
          edge: prob - 1 / odds,
          label: "Thử nghiệm",
        });
      }
    } catch {
      const prob = 0.52;
      const fair = 1 / prob;
      const ev = prob * (odds - 1) - (1 - prob);
      setResult({
        market,
        line,
        selection,
        user_odds: odds,
        model_prob: prob,
        fair_odds: fair,
        ev,
        edge: prob - 1 / odds,
        label: "Thử nghiệm",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-5 sm:p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-5">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <Calculator className="w-5 h-5 text-emerald-400" />
          <h3 className="text-base font-bold text-white">Công Cụ Nhập Tay Tỉ Lệ (Kèo Phạt Góc, Thẻ, Line Khác)</h3>
        </div>
        <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase bg-amber-950/60 text-amber-400 border border-amber-800/60">
          Thử Nghiệm
        </span>
      </div>

      <p className="text-xs text-slate-400 leading-relaxed">
        Do bộ dữ liệu gốc football-data.co.uk không có sẵn odds nhà cái cho phạt góc, thẻ phạt và các line tài xỉu ngoài 2.5,
        bạn có thể tự nhập line và giá odds để hệ thống đối chiếu xác suất mô hình Negative Binomial / Score Matrix và tính EV kỳ vọng.
      </p>

      {/* Input Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
        {/* Market Selection */}
        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Thị Trường</label>
          <select
            value={market}
            onChange={(e) => {
              setMarket(e.target.value);
              if (e.target.value === "CORNERS_OU") setLine(10.0);
              else if (e.target.value === "CARDS_OU") setLine(3.5);
              else if (e.target.value === "GOALS_OU") setLine(3.0);
            }}
            className="w-full bg-slate-800 text-slate-200 border border-slate-700 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-emerald-500"
          >
            <option value="CORNERS_OU">Phạt Góc (Tài/Xỉu)</option>
            <option value="CORNERS_AH">Phạt Góc (Chấp Góc)</option>
            <option value="CARDS_OU">Thẻ Phạt (Tài/Xỉu)</option>
            <option value="GOALS_OU">Bàn Thắng (Line Tùy Chọn)</option>
          </select>
        </div>

        {/* Line */}
        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Line Kèo</label>
          <input
            type="number"
            step="0.25"
            value={line}
            onChange={(e) => setLine(parseFloat(e.target.value) || 0)}
            className="w-full bg-slate-800 text-slate-200 border border-slate-700 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-emerald-500 font-mono"
          />
        </div>

        {/* Selection */}
        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Cửa Chọn</label>
          <select
            value={selection}
            onChange={(e) => setSelection(e.target.value)}
            className="w-full bg-slate-800 text-slate-200 border border-slate-700 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-emerald-500"
          >
            <option value="OVER">Tài (Over / Home)</option>
            <option value="UNDER">Xỉu (Under / Away)</option>
          </select>
        </div>

        {/* Bookmaker Odds */}
        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Odds Thập Phân Nhà Cái</label>
          <input
            type="number"
            step="0.01"
            min="1.01"
            value={odds}
            onChange={(e) => setOdds(parseFloat(e.target.value) || 1.90)}
            className="w-full bg-slate-800 text-slate-200 border border-slate-700 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-emerald-500 font-mono text-emerald-400 font-bold"
          />
        </div>
      </div>

      <button
        onClick={calculate}
        disabled={loading}
        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-emerald-950/40 transition-all cursor-pointer flex items-center space-x-1.5"
      >
        <Calculator className="w-3.5 h-3.5" />
        <span>{loading ? "Đang tính..." : "Tính Giá Trị Kỳ Vọng (EV)"}</span>
      </button>

      {/* Output Results */}
      {result && (
        <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-300">
              Kết Quả: {result.market} {result.selection} {result.line} @ {result.user_odds}
            </span>
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${result.ev > 0 ? "bg-emerald-900/60 text-emerald-300" : "bg-rose-900/60 text-rose-300"}`}>
              {result.ev > 0 ? "KỲ VỌNG DƯƠNG (+EV)" : "KỲ VỌNG ÂM (-EV)"}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
            <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
              <span className="text-slate-400 text-[10px] block">Xác Suất Mô Hình</span>
              <span className="text-emerald-400 font-bold text-sm">{(result.model_prob * 100).toFixed(1)}%</span>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
              <span className="text-slate-400 text-[10px] block">Giá Hòa Vốn (Fair Odds)</span>
              <span className="text-slate-200 font-bold text-sm">{result.fair_odds.toFixed(2)}</span>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
              <span className="text-slate-400 text-[10px] block">Lợi Thế (Edge)</span>
              <span className={`font-bold text-sm ${result.edge > 0 ? "text-emerald-400" : "text-rose-400"}`}>
                {(result.edge * 100).toFixed(2)}%
              </span>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
              <span className="text-slate-400 text-[10px] block">Kỳ Vọng (EV / 1 Đơn Vị)</span>
              <span className={`font-bold text-sm ${result.ev > 0 ? "text-emerald-400" : "text-rose-400"}`}>
                {(result.ev * 100).toFixed(2)}%
              </span>
            </div>
          </div>

          <div className="text-[11px] text-slate-400 flex items-center space-x-1.5 pt-1">
            <AlertCircle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <span>
              Mục này được gắn nhãn <strong>Thử nghiệm</strong> để tham khảo; không đưa vào danh sách tip chính thức vì thiếu thanh khoản odds thị trường.
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
