"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Activity, ShieldAlert, BarChart3, BookOpen, HeartHandshake, Globe } from "lucide-react";

export default function Navbar() {
  const pathname = usePathname();
  const [lang, setLang] = useState<"vi" | "en">("vi");

  const navLinks = [
    { href: "/", label: lang === "vi" ? "Bảng Điều Khiển" : "Dashboard", icon: Activity },
    { href: "/performance", label: lang === "vi" ? "Hiệu Suất Mô Hình" : "Performance", icon: BarChart3 },
    { href: "/methodology", label: lang === "vi" ? "Phương Pháp Học Thuật" : "Methodology", icon: BookOpen },
    { href: "/responsible-play", label: lang === "vi" ? "Chơi Có Trách Nhiệm" : "Responsible Play", icon: HeartHandshake },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800 bg-[#090d16]/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link href="/" className="flex items-center space-x-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20 group-hover:scale-105 transition-transform">
            <span className="text-white font-extrabold text-xl tracking-tight">K</span>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold tracking-tight text-white group-hover:text-emerald-400 transition-colors">
                Kèo<span className="text-emerald-400">Lab</span>
              </span>
              <span className="px-1.5 py-0.5 text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded">
                Quant Engine
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">Football Tip Analyzer • Học Thuật & Giải Trí</p>
          </div>
        </Link>

        {/* Nav Links */}
        <nav className="hidden md:flex items-center space-x-1 lg:space-x-2">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs lg:text-sm font-medium transition-all ${
                  isActive
                    ? "bg-slate-800 text-emerald-400 border border-slate-700 shadow-sm"
                    : "text-slate-300 hover:text-white hover:bg-slate-800/60"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-emerald-400" : "text-slate-400"}`} />
                <span>{link.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Right side tools */}
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setLang(lang === "vi" ? "en" : "vi")}
            className="flex items-center space-x-1.5 px-2.5 py-1.5 text-xs font-medium text-slate-300 bg-slate-800/80 hover:bg-slate-800 rounded-lg border border-slate-700 transition-colors"
            title="Đổi ngôn ngữ / Change language"
          >
            <Globe className="w-3.5 h-3.5 text-emerald-400" />
            <span className="uppercase font-semibold">{lang}</span>
          </button>

          <Link
            href="/responsible-play"
            className="hidden sm:flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold text-amber-400 bg-amber-400/10 border border-amber-400/20 hover:bg-amber-400/20 transition-colors"
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>18+ • Không Cá Cược</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
