# ⚽ KèoLab – Football Tip Analyzer

[![CI](https://github.com/keolab/keolab/actions/workflows/ci.yml/badge.svg)](https://github.com/keolab/keolab/actions)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14%20App%20Router-black.svg)](https://nextjs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **LƯU Ý PHÁP LÝ & ĐẠO ĐỨC (MANDATORY DISCLAIMER)**:  
> **KèoLab là sản phẩm DỰ ĐOÁN BÓNG ĐÁ ĐỂ GIẢI TRÍ VÀ NGHIÊN CỨU HỌC THUẬT.**  
> Hệ thống **KHÔNG nhận cược**, **KHÔNG có nạp/rút tiền**, **KHÔNG dẫn link tới bất kỳ nhà cái nào**, và **KHÔNG làm affiliate**. Cá cược thể thao có thể là hành vi bất hợp pháp tùy theo quốc gia và có nguy cơ gây nghiện cao. Không dành cho người dưới 18 tuổi.

---

## ⚡ Khởi Chạy Nhanh Trong 5 Lệnh (Quickstart in 5 Commands)

### Cách 1: Khởi Chạy Bằng Docker Compose (Khuyên dùng)
```bash
# 1. Clone repository
git clone https://github.com/your-username/Bot_Tip_FootBall.git keolab && cd keolab

# 2. Tạo file cấu hình môi trường
cp .env.example .env

# 3. Khởi chạy toàn bộ hệ thống API & Web qua Docker
docker-compose up --build
```
*Giao diện Web sẵn sàng tại: [http://localhost:3000](http://localhost:3000)*  
*FastAPI Swagger Docs tại: [http://localhost:8000/docs](http://localhost:8000/docs)*

---

### Cách 2: Khởi Chạy Cục Bộ (Local Development)

```bash
# 1. Cài đặt thư viện Backend
pip install -r backend/requirements.txt

# 2. Khởi tạo cơ sở dữ liệu mẫu & chạy Walk-Forward Backtest
python -m backend.app.data.seed_data

# 3. Khởi động Backend FastAPI Server
python -m uvicorn backend.app.main:app --reload --port 8000

# 4. Cài đặt thư viện Frontend
cd frontend && npm install

# 5. Khởi động Frontend Next.js Dev Server
npm run dev
```

---

## 🧪 Chạy Kiểm Thử Tự Động (Run Test Suite)

Hệ thống có bộ unit test và regression test toàn diện bao phủ toán học kèo chấp (quarter lines), de-vigging Shin, Dixon-Coles, Elo, Pi-ratings, tip engine và chống data leakage:

```bash
# Chạy toàn bộ 16 tests backend
python -m pytest backend/tests -v

# Tái hiện toàn bộ quy trình EDA và Walk-Forward Backtest
python notebooks/01_eda_and_walkforward_backtest.py
```

---

## 📐 Kiến Trúc Mô Hình & Nền Tảng Định Lượng

1. **Maher (1982) & Dixon-Coles (1997)**:
   - Mô hình Poisson độc lập kết hợp hiệu chỉnh tương quan $\rho$ cho tỉ số thấp (0-0, 1-1, 1-0, 0-1) và suy giảm trọng số theo thời gian $\xi$.
2. **Pi-Ratings (Constantinou & Fenton 2013)**:
   - Tách biệt năng lực sân nhà $R_H$ và sân khách $R_A$, phản ánh độ chênh lệch bàn thắng thực tế.
3. **De-Vigging Shin (1993)**:
   - Tách biên lợi nhuận nhà cái factoring xác suất người chơi nắm thông tin trước ($z$).
4. **Asian Handicap & Quarter Lines**:
   - Tính toán phân phối 5 trạng thái: Thắng trọn, Thắng nửa, Hoàn tiền (Push), Thua nửa, Thua trọn.
5. **Expected Value (+EV) & Fractional Kelly**:
   - Chỉ phát tip khi $\text{EV} \ge +3.0\%$ và $\text{Edge} \ge +2.5\%$.
   - Quản trị vốn ảo an toàn với Quarter-Kelly (1/4 Kelly, trần 2% bankroll ảo).
6. **Nguyên Tắc "NO BET"**:
   - Nếu thị trường đã hiệu quả và không có edge dương, hệ thống trung thực hiển thị nhãn **NO BET / Bỏ qua trận này**.

---

## 🗂️ Cấu Trúc Thư Mục Monorepo

```
d:/Bot_Tip_FootBall/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST endpoints
│   │   ├── core/            # Config & SQLAlchemy 2.0 DB setup
│   │   ├── data/            # Ingestion & team mapper (rapidfuzz)
│   │   ├── math/            # Dixon-Coles, Poisson, devig, ratings, Kelly, Asian Handicap
│   │   ├── backtest/        # Walk-forward chronological backtest engine
│   │   └── pipeline/        # APScheduler cron jobs
│   └── tests/               # Pytest suite
├── frontend/                # Next.js 14 App Router, TypeScript, TailwindCSS, Recharts
├── data/                    # Raw & cleaned datasets
├── notebooks/               # 01_eda_and_walkforward_backtest.py
├── docs/
│   ├── METHODOLOGY.md       # Phương pháp học thuật & công thức chi tiết
│   └── DATA_SOURCES.md      # Danh mục nguồn dữ liệu & API adapter
├── docker-compose.yml       # Docker compose orchestration
├── .env.example
└── README.md
```

---

## 🛡️ Chơi Có Trách Nhiệm (Responsible Play)
Nếu bạn hoặc người thân cảm thấy có dấu hiệu mất kiểm soát trong việc cá độ thể thao:
- **Tổng đài tư vấn tâm lý sức khỏe (Việt Nam)**: `1900 9095` hoặc `1800 1567` (Miễn phí 24/7)
- **Hỗ trợ quốc tế**: [BeGambleAware.org](https://www.begambleaware.org) • [GamCare.org.uk](https://www.gamcare.org.uk)
