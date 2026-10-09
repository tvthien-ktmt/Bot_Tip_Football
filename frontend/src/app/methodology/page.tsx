"use client";

import React from "react";
import { BookOpen, ShieldCheck, CheckCircle2, FileText, Code2, Layers } from "lucide-react";

export default function MethodologyPage() {
  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Hero Header */}
      <div className="rounded-3xl bg-slate-900/90 border border-slate-800 p-6 sm:p-8 shadow-xl space-y-3">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <BookOpen className="w-3.5 h-3.5" />
          <span>Phương Pháp Khoa Học Dữ Liệu & Học Thuật</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Nền Tảng Định Lượng Của KèoLab
        </h1>
        <p className="text-slate-300 text-xs sm:text-sm leading-relaxed">
          Tài liệu mô tả chi tiết các mô hình xác suất thống kê, phương pháp loại bỏ biên lợi nhuận (de-vigging), toán học kèo chấp châu Á (Asian Handicap) và nguyên tắc quản trị rủi ro được áp dụng trong hệ thống.
        </p>
      </div>

      {/* Section 1: Poisson & Dixon-Coles */}
      <section className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center space-x-2">
          <span className="w-6 h-6 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs font-bold">1</span>
          <span>Mô Hình Maher (1982) & Dixon-Coles (1997)</span>
        </h2>
        <p className="text-xs text-slate-300 leading-relaxed">
          Mô hình cơ sở giả định số bàn thắng của đội nhà (<span className="text-emerald-400 font-mono">X</span>) và đội khách (<span className="text-sky-400 font-mono">Y</span>) tuân theo phân phối Poisson độc lập được tham số hóa theo sức tấn công (<span className="font-mono">α</span>), phòng ngự (<span className="font-mono">β</span>), và lợi thế sân nhà (<span className="font-mono">γ</span>):
        </p>

        <div className="p-4 rounded-xl bg-slate-950 font-mono text-xs text-emerald-400 overflow-x-auto border border-slate-800">
          P(X = x, Y = y) = [ (λ^x * e^-λ) / x! ] * [ (μ^y * e^-μ) / y! ]
        </div>

        <p className="text-xs text-slate-300 leading-relaxed">
          Tuy nhiên, phân phối Poisson độc lập có xu hướng đánh giá thấp các tỉ số ít bàn thắng (0-0, 1-1). Dixon & Coles (1997) đưa vào hệ số hiệu chỉnh tương quan <span className="text-amber-400 font-mono">ρ</span> cho 4 tỉ số thấp:
        </p>

        <div className="p-4 rounded-xl bg-slate-950 font-mono text-xs text-slate-300 overflow-x-auto border border-slate-800 space-y-1">
          <div>τ(0, 0) = 1 - λ * μ * ρ</div>
          <div>τ(1, 0) = 1 + λ * ρ</div>
          <div>τ(0, 1) = 1 + μ * ρ</div>
          <div>τ(1, 1) = 1 - ρ</div>
          <div className="text-slate-500">// Các tỉ số khác: τ(x, y) = 1.0</div>
        </div>
      </section>

      {/* Section 2: Pi-ratings */}
      <section className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center space-x-2">
          <span className="w-6 h-6 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs font-bold">2</span>
          <span>Hệ Thống Đánh Giá Pi-Ratings (Constantinou & Fenton 2013)</span>
        </h2>
        <p className="text-xs text-slate-300 leading-relaxed">
          Khác với Elo chỉ có 1 chỉ số duy nhất, Pi-ratings chia tách khả năng của mỗi câu lạc bộ thành năng lực sân nhà (<span className="text-emerald-400 font-mono">R_H</span>) và năng lực sân khách (<span className="text-sky-400 font-mono">R_A</span>). Độ chênh lệch bàn thắng kỳ vọng được tính bằng:
        </p>

        <div className="p-4 rounded-xl bg-slate-950 font-mono text-xs text-emerald-400 overflow-x-auto border border-slate-800">
          e_H = c * (R_H(home) - R_A(away))
        </div>

        <p className="text-xs text-slate-300 leading-relaxed">
          Độ chênh lệch bàn thắng thực tế được biến đổi phi tuyến <span className="font-mono">ψ(GD) = sign(GD) * ln(1 + |GD|)</span> để giảm ảnh hưởng của các trận thắng đậm bất thường.
        </p>
      </section>

      {/* Section 3: De-vigging Shin */}
      <section className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center space-x-2">
          <span className="w-6 h-6 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs font-bold">3</span>
          <span>Loại Bỏ Margin Nhà Cái (De-Vigging Shin 1993)</span>
        </h2>
        <p className="text-xs text-slate-300 leading-relaxed">
          Tỉ lệ cược của nhà cái luôn có biên lợi nhuận (vig/margin 3-6%). Phương pháp thông thường chỉ chuẩn hóa tỉ lệ chia tổng, nhưng mô hình Shin (1993) giả định thị trường có tỉ lệ người chơi nội bộ (<span className="text-amber-400 font-mono">z</span>) nắm thông tin trước. Xác suất thực <span className="font-mono">π_i</span> giải phương trình:
        </p>

        <div className="p-4 rounded-xl bg-slate-950 font-mono text-xs text-emerald-400 overflow-x-auto border border-slate-800">
          π_i = [ sqrt(z^2 + 4 * (1 - z) * (q_i^2 / S)) - z ] / [ 2 * (1 - z) ]
        </div>
      </section>

      {/* Section 4: Asian Handicap Quarter Lines */}
      <section className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center space-x-2">
          <span className="w-6 h-6 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs font-bold">4</span>
          <span>Toán Kèo Chấp Châu Á & Line Phần Tư (Quarter Lines)</span>
        </h2>
        <p className="text-xs text-slate-300 leading-relaxed">
          Kèo chấp phần tư (ví dụ <span className="font-mono">-0.25, -0.75</span>) chia 50% tiền cược vào hai line liền kề. Kết quả gồm 5 trạng thái: Thắng trọn, Thắng nửa, Hoàn tiền (Push), Thua nửa, và Thua trọn.
        </p>

        <div className="p-4 rounded-xl bg-slate-950 font-mono text-xs text-slate-300 overflow-x-auto border border-slate-800 space-y-1">
          <div>EV = P(Thắng) * (Odds - 1) + P(Thắng Nửa) * (Odds - 1) * 0.5</div>
          <div className="pl-6">- P(Thua Nửa) * 0.5 - P(Thua Trọn) * 1.0</div>
        </div>
      </section>

      {/* Section 5: Fractional Kelly */}
      <section className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center space-x-2">
          <span className="w-6 h-6 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs font-bold">5</span>
          <span>Quản Trị Vốn Ảo Fractional Kelly (1/4 Kelly)</span>
        </h2>
        <p className="text-xs text-slate-300 leading-relaxed">
          Nhằm tránh rủi ro phá sản (ruin) và hạn chế biến động, hệ thống sử dụng <strong>Quarter-Kelly (1/4 Kelly)</strong> và giới hạn tối đa <strong>2% bankroll ảo</strong> cho mỗi tip:
        </p>

        <div className="p-4 rounded-xl bg-slate-950 font-mono text-xs text-emerald-400 overflow-x-auto border border-slate-800">
          f* = (p * (Odds - 1) - (1 - p)) / (Odds - 1)
          <br />
          Stake_Virtual = min(2.0%, max(0.5%, 0.25 * f*))
        </div>
      </section>

      {/* Bibliography */}
      <section className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-3">
        <h3 className="text-base font-bold text-white">Tài Liệu Tham Khảo Học Thuật</h3>
        <ul className="text-xs text-slate-400 space-y-1.5 list-disc list-inside">
          <li>Maher, M. J. (1982). <em>Modelling association football scores</em>. Statistica Neerlandica.</li>
          <li>Dixon, M. J., & Coles, S. G. (1997). <em>Modelling association football scores and inefficiencies in the football betting market</em>. Applied Statistics.</li>
          <li>Constantinou, A. C., & Fenton, N. E. (2013). <em>Determining the level of ability of football teams by dynamic ratings based on the relative discrepancies in scores</em>. Journal of Quantitative Analysis in Sports.</li>
          <li>Shin, H. S. (1993). <em>Measuring the incidence of insider trading in a bookmaker's market</em>. Economic Journal.</li>
          <li>Constantinou, A. C. (2020). <em>Investigating the efficiency of the Asian handicap football betting market with ratings and Bayesian networks</em>. arXiv:2003.09384.</li>
        </ul>
      </section>
    </div>
  );
}
