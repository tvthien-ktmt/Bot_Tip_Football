# ⚽ KèoLab – Football Tip Analyzer

[![CI](https://github.com/keolab/keolab/actions/workflows/ci.yml/badge.svg)](https://github.com/keolab/keolab/actions)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14%20App%20Router-black.svg)](https://nextjs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **LƯU Ý PHÁP LÝ & ĐẠO ĐỨC (MANDATORY ETHICAL DISCLAIMER)**:  
> **KèoLab là sản phẩm DỰ ĐOÁN BÓNG ĐÁ ĐỂ GIẢI TRÍ VÀ NGHIÊN CỨU HỌC THUẬT.**  
> Hệ thống **KHÔNG nhận cược**, **KHÔNG có nạp/rút tiền**, **KHÔNG dẫn link tới bất kỳ nhà cái nào**, và **KHÔNG làm affiliate**. Cá cược thể thao có thể là hành vi bất hợp pháp tùy theo quốc gia và có nguy cơ gây nghiện cao. Không sử dụng ngôn từ kích động "chắc ăn" hay "kèo thơm". Tuyệt đối không dành cho người dưới 18 tuổi.

---

## ⚡ Các Lệnh Thực Thi Chính (Makefile & CLI)

Hệ thống hỗ trợ các lệnh tiện ích nhanh thông qua Makefile hoặc Python CLI trực tiếp:

```bash
# 1. Chạy toàn bộ 24 Unit & Integration Tests (Bao gồm Golden Test và Anti-Leakage)
make test
# hoặc: python -m pytest backend/tests -v

# 2. Chạy Walk-Forward Chronological Backtest trên cả 5 giải đấu (1,000 bootstrap resamples)
make backtest
# hoặc: python -m backend.cli backtest --mode T-24h

# 3. Xuất dự đoán và Tip cho các trận sắp đá của mùa giải đang diễn ra (2026/27)
make predict
# hoặc: python -m backend.cli predict --mode T-24h --div ALL

# 4. Kiểm tra toàn vẹn và thẩm định bộ 25 tập tin CSV dữ liệu
make audit
# hoặc: python -m backend.cli audit
```

---

## 📊 Golden Test Benchmark (Premier League 2025/26)

Hệ thống được kiểm định chuẩn xác tuyệt đối (khớp đến 3-4 chữ số thập phân) trên tập dữ liệu chuẩn **Premier League 2025/26** (`Season 20252026.csv`):

| Chỉ Số Thống Kê | Giá Trị Thực Tế Bộ Dữ Liệu | Kết Quả Module KèoLab | Trạng Thái Kiểm Định |
|---|---|---|---|
| **Số trận đấu** | 380 | 380 | ✅ KHỚP CHÍNH XÁC |
| **Số đội / Trọng tài** | 20 đội / 23 trọng tài | 20 đội / 23 trọng tài | ✅ KHỚP CHÍNH XÁC |
| **Tỉ lệ H / D / A** | 42.6% / 27.4% / 30.0% | 42.6% / 27.4% / 30.0% | ✅ KHỚP CHÍNH XÁC |
| **Bàn thắng TB (Nhà / Khách / Tổng)** | 1.53 / 1.22 / 2.75 | 1.53 / 1.22 / 2.75 | ✅ KHỚP CHÍNH XÁC |
| **Tài 2.5 / BTTS** | 55.0% / 56.1% | 55.0% / 56.1% | ✅ KHỚP CHÍNH XÁC |
| **Phạt góc TB / std** | 10.00 / 3.27 | 10.00 / 3.27 | ✅ KHỚP CHÍNH XÁC |
| **Thẻ vàng TB / trận** | 3.75 | 3.75 | ✅ KHỚP CHÍNH XÁC |
| **Overround Avg đóng cửa** | 1.057 | 1.057 | ✅ KHỚP CHÍNH XÁC |
| **Market Benchmark Close (RPS)** | 0.2045 | 0.2045 | ✅ KHỚP CHÍNH XÁC |
| **Market Benchmark Close (Log loss)** | 1.0118 | 1.0118 | ✅ KHỚP CHÍNH XÁC |
| **Market Benchmark Close (Acc)** | 49.5% | 49.5% | ✅ KHỚP CHÍNH XÁC |
| **Market Benchmark Open (RPS)** | 0.2053 | 0.2053 | ✅ KHỚP CHÍNH XÁC |

---

## ⚠️ Giới Hạn Dữ Liệu & Các Giả Định Kỹ Thuật

1. **Giới hạn nguồn dữ liệu**:
   - Dữ liệu thu thập từ `football-data.co.uk` gồm 25 files CSV cho 5 giải đấu (Premier League `E0`, Championship `E1`, La Liga `SP1`, Serie A `I1`, Bundesliga `D1`).
   - Tên file **không dùng để xác định mùa giải**; mùa giải được suy diễn hoàn toàn từ cột `Date` (`dayfirst=True`, xử lý cả định dạng `dd/mm/yyyy` và `dd/mm/yy`).
   - Cột kết quả (`FTHG`/`FTAG`) chưa có tức là trận đấu chưa diễn ra (fixtures cần dự đoán).
2. **Không có xG chính thức**:
   - Dữ liệu gốc không có số liệu xG (Expected Goals) từ Opta/StatsBomb.
   - Hệ thống giải quyết bằng mô hình **M5: Shot-based xG proxy** (hồi quy Poisson dựa trên `HST` - sút trúng đích, `HS - HST` - sút ra ngoài, kết hợp EMA trọng số chất lượng dứt điểm) để lọc bớt may rủi.
3. **Không có đội hình ra sân / chấn thương**:
   - Mô hình không tự ý bịa số liệu chấn thương hay cầu thủ.
4. **Không có odds nhà cái cho phạt góc, thẻ phạt, hay line tài xỉu ngoài 2.5**:
   - Hệ thống cung cấp công cụ **Nhập Odds Thủ Công (Manual Odds Calculator)** trên Match Center để người dùng tự nhập line và giá odds thập phân, từ đó hệ thống giải thuật phân phối Negative Binomial (kiểm định overdispersion góc: TB 10.00, std 3.27, var 10.69) và tính ra EV.
   - Mọi dự báo góc và thẻ phạt đều được gắn nhãn minh bạch: **"Thử nghiệm"** và **"Lean"**.
5. **Chuỗi dự phòng Odds tham chiếu**:
   - Do Pinnacle (`PS*`) thiếu tới ~45% và một số hãng khác thiếu 25-32%, hệ thống tuân thủ chuỗi dự phòng: `Avg -> B365 -> BW -> Max`.

---

## 🛡️ Nguyên Tắc Chống Rò Rỉ Dữ Liệu (Anti-Leakage)

- **Walk-Forward Expanding Window**: Mọi chỉ số xếp hạng (Elo, Pi-ratings, Dixon-Coles attack/defense) của trận đấu ở thời điểm $t$ chỉ được tính dựa trên các trận đấu đã kết thúc **nghiêm ngặt trước thời điểm $t$**.
- **Hai chế độ dự đoán độc lập**:
  - **T-24h**: Sử dụng độc quyền odds MỞ (Open). Tuyệt đối không dùng odds đóng.
  - **T-1h**: Cho phép sử dụng odds ĐÓNG (Close) như thông tin cập nhật cuối cùng của thị trường.
- **Tính bất biến khi hoán vị tương lai**: Đã kiểm định tự động bằng test `test_future_permutation_invariance`: thay đổi hoặc xóa bỏ các kết quả tương lai không làm dịch chuyển bất kỳ xác suất nào của trận $t$.

---

## 🎯 Nhận Định Về Hiệu Quả Thị Trường & Tỷ Lệ "NO BET"

- Tại giải đấu có tính thanh khoản cực cao như **Premier League**, tỷ lệ odds đóng cửa của thị trường đạt độ chính xác rất cao (RPS ~0.2045, Log loss 1.0118).
- Kiểm định Bootstrap 95% Confidence Interval chứng minh rằng sự khác biệt giữa mô hình và giá đóng cửa của thị trường chứa giá trị 0. **KèoLab tuyệt đối không tuyên bố "đánh bại thị trường" khi không có bằng chứng thống kê vững chắc.**
- Do đó, tỷ lệ **NO BET** trong hệ thống chiếm đa số (trên 75-80% số trận). Đây là tính năng bảo vệ người dùng có chủ đích: **Không ép kèo khi thị trường không tồn tại lợi thế (+EV).**

---

## 📁 Cấu Trúc Mã Nguồn

```
d:/Bot_Tip_FootBall/
├── Makefile                                # make test, make backtest, make predict, make audit
├── README.md                               # Tài liệu hướng dẫn & công bố mô hình
├── data_league/                            # 25 CSVs gốc từ football-data.co.uk
├── backend/
│   ├── cli.py                              # CLI đa năng (audit, backtest, predict)
│   ├── reports/                            # Báo cáo backtest tự động (MD, HTML, model_card.json)
│   ├── app/
│   │   ├── main.py                         # FastAPI App
│   │   ├── api/routes.py                   # REST endpoints (/fixtures, /predict/upcoming, /manual/eval)
│   │   ├── data/
│   │   │   ├── csv_loader.py               # Loader 25 CSVs, BOM utf-8-sig, fallback odds, audit
│   │   │   └── fixtures_client.py          # Bộ nạp lịch thi đấu 2026/27 tự động
│   │   ├── math/
│   │   │   ├── dixon_coles.py              # M2: Dixon-Coles MLE fitting & time-decay
│   │   │   ├── market_implied.py           # M6: Giải ngược ma trận từ odds thị trường (Prior)
│   │   │   ├── shot_xg.py                  # M5: Shot-based xG proxy Poisson GLM
│   │   │   ├── residual_lgbm.py            # M7: LightGBM học phần dư thị trường + SHAP
│   │   │   ├── ensemble.py                 # M8: Log-linear pooling w in [0, 1]
│   │   │   ├── corners_cards.py            # Negative Binomial góc & thẻ phạt
│   │   │   └── tip_engine.py               # EV, Edge, Kelly fractional (1/4), lý do định lượng
│   │   └── backtest/
│   │       ├── walkforward.py              # Engine backtest mở rộng theo thời gian
│   │       └── optimizer.py                # Tối ưu siêu tham số Optuna
│   └── tests/                              # Bộ 24 tests Pytest (Golden test, Anti-leakage, AH...)
└── frontend/                               # Next.js 14 App Router, TypeScript, TailwindCSS
```

---

*KèoLab Engine v2.0 - Developed for Academic & Entertainment Sports Analytics*
