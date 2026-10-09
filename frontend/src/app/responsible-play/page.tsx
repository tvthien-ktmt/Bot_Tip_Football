"use client";

import React from "react";
import { HeartHandshake, AlertTriangle, PhoneCall, ShieldCheck, CheckCircle2, XCircle } from "lucide-react";

export default function ResponsiblePlayPage() {
  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Hero Header */}
      <div className="rounded-3xl bg-slate-900/90 border border-slate-800 p-6 sm:p-8 shadow-xl space-y-3">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
          <HeartHandshake className="w-3.5 h-3.5" />
          <span>Bảo Vệ Người Dùng & Chơi Có Trách Nhiệm</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Cam Kết Chơi Có Trách Nhiệm
        </h1>
        <p className="text-slate-300 text-xs sm:text-sm leading-relaxed">
          KèoLab là công cụ phân tích thống kê định lượng phục vụ nghiên cứu và giải trí. Cá cược thể thao có thể gây nghiện nghiêm trọng và dẫn đến thiệt hại tài chính nặng nề. Hãy luôn giữ tỉnh táo và đặt ra giới hạn an toàn.
        </p>
      </div>

      {/* Critical Principles */}
      <section className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          <span>Nguyên Tắc Cốt Lõi Tại KèoLab</span>
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-4 rounded-2xl bg-slate-800/40 border border-slate-800 space-y-2">
            <div className="flex items-center space-x-2 text-rose-400 font-bold text-xs uppercase">
              <XCircle className="w-4 h-4 shrink-0" />
              <span>Những Điều KèoLab KHÔNG Bao Giờ Làm</span>
            </div>
            <ul className="text-xs text-slate-300 space-y-1.5 list-disc list-inside">
              <li>Không nhận cược, không nạp/rút tiền</li>
              <li>Không liên kết, không dẫn link tới bất kỳ nhà cái nào</li>
              <li>Không dùng từ ngữ kích thích: "kèo thơm chắc ăn", "x10 vốn"</li>
              <li>Không ép ra tip cho mọi trận đấu</li>
            </ul>
          </div>

          <div className="p-4 rounded-2xl bg-slate-800/40 border border-slate-800 space-y-2">
            <div className="flex items-center space-x-2 text-emerald-400 font-bold text-xs uppercase">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>Những Điều KèoLab Cam Kết Thực Hiện</span>
            </div>
            <ul className="text-xs text-slate-300 space-y-1.5 list-disc list-inside">
              <li>Công khai toàn bộ lịch sử tip thắng, hòa và thua</li>
              <li>Hiển thị cảnh báo rủi ro khi mô hình lệch thị trường &gt; 12%</li>
              <li>Đề xuất quản lý vốn ảo hạn mức tối đa 2%</li>
              <li>Giáo dục toán học xác suất thay vì kích động may rủi</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Self-Assessment Checklist */}
      <section className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
        <h2 className="text-lg font-bold text-white">Dấu Hiệu Nhận Biết Vấn Đề Về Nghiện Cờ Bạc</h2>
        <p className="text-xs text-slate-400">
          Hãy tự trả lời các câu hỏi sau một cách trung thực. Nếu bạn trả lời "Có" cho từ 2 câu trở lên, bạn có thể đang gặp rủi ro mất kiểm soát:
        </p>

        <div className="space-y-2.5 text-xs text-slate-300">
          <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-800 flex items-start space-x-2.5">
            <span className="font-bold text-amber-400">1.</span>
            <span>Bạn có bao giờ cược với số tiền dành cho sinh hoạt phí, tiền học hay tiền thuê nhà không?</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-800 flex items-start space-x-2.5">
            <span className="font-bold text-amber-400">2.</span>
            <span>Sau khi thua, bạn có thôi thúc mãnh liệt phải cược lớn hơn ngay lập tức để "gỡ gạc" (chasing losses) không?</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-800 flex items-start space-x-2.5">
            <span className="font-bold text-amber-400">3.</span>
            <span>Bạn có nói dối gia đình, bạn bè về thời gian hoặc số tiền bạn dành cho việc cá cược không?</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-800 flex items-start space-x-2.5">
            <span className="font-bold text-amber-400">4.</span>
            <span>Việc theo dõi tỉ số trận đấu có gây xao nhãng công việc, học tập hoặc làm rạn nứt các mối quan hệ không?</span>
          </div>
        </div>
      </section>

      {/* Helplines and Support */}
      <section className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center space-x-2">
          <PhoneCall className="w-5 h-5 text-emerald-400" />
          <span>Kênh Hỗ Trợ & Đường Dây Nóng Tư Vấn Tâm Lý</span>
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-2xl bg-slate-800/40 border border-slate-700/60 space-y-1">
            <h4 className="font-bold text-white">Đường dây nóng hỗ trợ tâm lý (Việt Nam)</h4>
            <p className="text-slate-400">Tổng đài quốc gia tư vấn tâm lý sức khỏe:</p>
            <strong className="text-emerald-400 font-mono text-sm block">1900 9095</strong>
            <span className="text-slate-500 text-[11px]">Hỗ trợ 24/7 bảo mật thông tin</span>
          </div>

          <div className="p-4 rounded-2xl bg-slate-800/40 border border-slate-700/60 space-y-1">
            <h4 className="font-bold text-white">Tổ chức quốc tế về phòng chống nghiện</h4>
            <p className="text-slate-400">Hỗ trợ tự loại trừ và tư vấn online:</p>
            <div className="space-y-1 pt-1">
              <a href="https://www.begambleaware.org" target="_blank" rel="noopener noreferrer" className="text-emerald-400 hover:underline block font-mono">
                BeGambleAware.org
              </a>
              <a href="https://www.gamcare.org.uk" target="_blank" rel="noopener noreferrer" className="text-sky-400 hover:underline block font-mono">
                GamCare.org.uk
              </a>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
