import Link from "next/link";
import { ShieldCheck, AlertTriangle, BookOpen, ExternalLink, HeartHandshake } from "lucide-react";

export default function Footer() {
  return (
    <footer className="w-full border-t border-slate-800 bg-[#070b12] text-slate-400 text-xs mt-16">
      {/* Mandatory Disclaimer Highlight */}
      <div className="bg-slate-900/80 border-b border-slate-800 py-3.5 px-4 text-center">
        <div className="max-w-4xl mx-auto flex items-center justify-center space-x-2 text-amber-300 font-medium text-xs sm:text-sm">
          <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" />
          <span>
            Chỉ mang tính giải trí & tham khảo học thuật. Không đảm bảo lợi nhuận. Cá cược có thể bất hợp pháp và gây nghiện. Không dành cho người dưới 18 tuổi.
          </span>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 grid grid-cols-1 md:grid-cols-4 gap-8">
        {/* Brand & Principles */}
        <div className="md:col-span-2 space-y-3">
          <div className="flex items-center space-x-2 text-white font-bold text-base">
            <span className="text-emerald-400">KèoLab</span>
            <span>– Football Tip Analyzer</span>
          </div>
          <p className="text-slate-400 text-xs leading-relaxed max-w-md">
            Nền tảng toán học & định lượng phân tích xác suất bóng đá dựa trên mô hình Maher (1982), Dixon-Coles (1997), Pi-Ratings (Constantinou & Fenton), và De-vigging Shin (1993).
          </p>
          <div className="flex flex-wrap gap-2 pt-1 text-[11px]">
            <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
              ✓ Không nhận cược
            </span>
            <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
              ✓ Không nạp/rút tiền
            </span>
            <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
              ✓ Không liên kết nhà cái
            </span>
            <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
              ✓ Zero Affiliate
            </span>
          </div>
        </div>

        {/* Quick Links */}
        <div className="space-y-2">
          <h4 className="text-slate-200 font-semibold text-xs uppercase tracking-wider">Học Thuật & Dữ Liệu</h4>
          <ul className="space-y-1.5">
            <li>
              <Link href="/methodology" className="hover:text-emerald-400 transition-colors flex items-center space-x-1">
                <BookOpen className="w-3.5 h-3.5" />
                <span>Phương Pháp Định Lượng</span>
              </Link>
            </li>
            <li>
              <Link href="/performance" className="hover:text-emerald-400 transition-colors">
                Walk-Forward Backtest Audit
              </Link>
            </li>
            <li>
              <Link href="/methodology#calibration" className="hover:text-emerald-400 transition-colors">
                Brier Score & Calibration
              </Link>
            </li>
            <li>
              <Link href="/methodology#asian-handicap" className="hover:text-emerald-400 transition-colors">
                Toán Kèo Chấp & Quarter Lines
              </Link>
            </li>
          </ul>
        </div>

        {/* Responsible Gaming & Support */}
        <div className="space-y-2">
          <h4 className="text-slate-200 font-semibold text-xs uppercase tracking-wider">Chơi Có Trách Nhiệm</h4>
          <ul className="space-y-1.5 text-xs">
            <li>
              <Link href="/responsible-play" className="text-amber-400 hover:underline flex items-center space-x-1 font-medium">
                <HeartHandshake className="w-3.5 h-3.5" />
                <span>Trung Tâm Trợ Giúp Nghiện Cờ Bạc</span>
              </Link>
            </li>
            <li className="text-slate-400">
              Đường dây nóng hỗ trợ tâm lý: <strong className="text-slate-300">1900 9095</strong> hoặc <strong className="text-slate-300">1800 1567</strong>
            </li>
            <li>
              <a href="https://www.begambleaware.org" target="_blank" rel="noopener noreferrer" className="hover:text-slate-300 flex items-center space-x-1">
                <span>BeGambleAware.org</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div className="border-t border-slate-800/80 max-w-7xl mx-auto px-4 py-4 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-500">
        <p>© 2025-2026 KèoLab Analytics. Mọi quyền được bảo lưu. Thiết kế phục vụ nghiên cứu khoa học dữ liệu.</p>
        <p className="mt-2 sm:mt-0">Phiên bản v1.0.0 (Walk-Forward Calibrated)</p>
      </div>
    </footer>
  );
}
