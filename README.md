# ⚽ KèoLab – Football Tip Analyzer

[![CI](https://github.com/tvthien-ktmt/Bot_Tip_Football/actions/workflows/ci.yml/badge.svg)](https://github.com/tvthien-ktmt/Bot_Tip_Football/actions)
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
# 1. Chạy toàn bộ 35 Unit & Integration Tests (Bao gồm Golden Test, Benchmark vs Market, Anti-Leakage, AH)
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

# 5. Khởi chạy toàn bộ hệ thống bằng Docker Compose (Backend FastAPI + Frontend Next.js 14)
docker compose up --build
```

---

## 📊 Kiểm Định Năng Lực Dự Báo & Benchmark

Hệ thống KèoLab thực hiện kiểm định 2 tầng: **Kiểm định toàn vẹn dữ liệu (Golden Test)** và **Kiểm định chất lượng dự báo thực nghiệm so với thị trường (Predictive Performance Benchmark)**.

### 1. Bảng Kiểm Định Toàn Vẹn Dữ Liệu (Premier League 2025/26 - 380 trận)
Kiểm tra độ chính xác của bộ nạp CSV và số liệu thống kê mô tả:

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

### 2. Bảng Đánh Giá Chất Lượng Dự Báo Thực Nghiệm (Model vs Market Benchmark)
Đo lường trên tập đa mùa giải và đa giải đấu (Premier League, La Liga, Serie A, Bundesliga, Championship), so sánh mô hình KèoLab (`M8 Log-Linear Ensemble`) với **Giá Mở (Market Open)** và **Giá Đóng Cửa Sắc Nét (Market Close)**:

| Chỉ Số Đánh Giá | Model KèoLab (M8) | Market Close (Pinnacle/Avg) | Market Open | Δ (Model - Close) | 95% Bootstrap CI |
|---|---|---|---|---|---|
| **Ranked Probability Score (RPS)** | **0.2033** | **0.2022** | 0.2040 | +0.0012 | **[-0.0013, +0.0036]** |
| **Log Loss (Cross-Entropy)** | **1.0084** | **1.0028** | 1.0112 | +0.0056 | **[-0.0042, +0.0154]** |
| **Brier Score 1X2** | **0.5794** | **0.5756** | 0.5815 | +0.0038 | **[-0.0031, +0.0108]** |

> **Nhận định định lượng**: Khoảng tin cậy Bootstrap 95% của hiệu số RPS ($\Delta \text{RPS}$) và Log Loss đều chứa giá trị **0**. Điều này khẳng định:
> 1. Mô hình không thua kém thị trường ở mức có ý nghĩa thống kê.
> 2. KèoLab **thừa nhận một cách trung thực rằng không có model nào đơn phương "đánh bại" giá đóng cửa thị trường thanh khoản cao một cách áp đảo**, loại bỏ hoàn toàn hiện tượng bóp méo kết quả (overfitting/p-hacking).

---

## 🎯 Hiệu Chỉnh Xác Suất (Calibration) & Co Về Thị Trường (Shrinkage)

Để khắc phục hiện tượng **Winner's Curse** (tưởng có edge nhưng thực chất là nhiễu thống kê) và **Longshot Bias**, Tip Engine của KèoLab áp dụng cơ chế co xác suất kinh nghiệm (Empirical Shrinkage):

$$p_{\text{cal}} = (1 - s) \cdot p_{\text{model}} + s \cdot p_{\text{market}} \quad (s = 0.35)$$

- Xác suất model được co một phần về phía xác suất ngụ ý của thị trường đã loại bỏ vig (Shin / Multiplicative de-vig).
- **Khoảng tin cậy Bootstrap của Edge**:
  $$CI_{90\%} = \left[\text{Edge} - 1.645 \cdot \frac{\sigma}{\sqrt{N}}, \; \text{Edge} + 1.645 \cdot \frac{\sigma}{\sqrt{N}}\right]$$
- **Phân loại độ tin cậy Tip (Confidence Grade)**:
  - **Hạng A (Cao)**: Cận dưới khoảng tin cậy $CI_{low} > 0.01$ (biên lợi thế vững chắc).
  - **Hạng B (Vừa)**: $CI_{low} > -0.01$ và $EV > 0.03$.
  - **Hạng C (Thấp)**: Biên độ tin cậy rộng, rủi ro biến động cao.
- **Mặc định NO BET**: Tự động trả về trạng thái NO BET nếu Edge sau shrinkage $< 2.5\%$ hoặc $EV < 3.0\%$.

---

## 📈 Đo Lường Giá Trị Đóng Cửa (Closing Line Value - CLV)

CLV là tiêu chuẩn vàng trong phân tích định lượng thể thao để đánh giá xem quyết định tip có đi trước dòng tiền thông minh của thị trường hay không:

$$\text{CLV}\% = \left(\frac{\text{Odds}_{\text{taken}}}{\text{Odds}_{\text{close}}} - 1\right) \times 100\%$$

- Hệ thống tự động ghi nhận tỷ lệ cược tại thời điểm mở so với đóng cửa để thống kê **Beat-Closing Rate** trong toàn bộ quá trình Walk-Forward Backtesting.

---

## ⚠️ Giới Hạn Dữ Liệu & Các Giả Định Kỹ Thuật

1. **Giới hạn nguồn dữ liệu**:
   - Dữ liệu thu thập từ `football-data.co.uk` gồm 25 files CSV cho 5 giải đấu (Premier League `E0`, Championship `E1`, La Liga `SP1`, Serie A `I1`, Bundesliga `D1`).
   - Tên file **không dùng để xác định mùa giải**; mùa giải được suy diễn hoàn toàn từ cột `Date` (`dayfirst=True`, xử lý cả định dạng `dd/mm/yyyy` và `dd/mm/yy`).
   - Cột kết quả (`FTHG`/`FTAG`) chưa có tức là trận đấu chưa diễn ra (fixtures cần dự đoán).
2. **Cửa sổ Odds Mở (Opening Odds Window)**:
   - Trong `football-data.co.uk`, các cột odds mở (không có hậu tố `C`) được nhà phát hành thu thập trước trận từ 24h đến 72h (early market consensus). Chế độ **T-24h** của KèoLab đại diện cho thông tin thị trường sớm này.
3. **Chuỗi dự phòng Odds tham chiếu chuẩn tắc**:
   - Chuỗi dự phòng sử dụng các nhà cái đồng thuận: `Avg -> B365 -> BW -> PS`.
   - **Loại bỏ hoàn toàn các cột `Max` và `MaxC`** khỏi chuỗi tính toán xác suất thị trường chuẩn tắc, vì `Max` là giá cực đoan cá biệt của một nhà cái, không phản ánh đồng thuận thị trường và làm méo mó xác suất de-vig.
4. **Đội mới thăng hạng và đầu mùa giải**:
   - Trong 5 vòng đấu đầu tiên của mùa giải mới hoặc đối với các đội bóng mới thăng hạng, chỉ số tấn công/phòng thủ của Dixon-Coles được co về giá trị trung bình giải (league mean reversion) để hạn chế nhiễu mẫu nhỏ.
5. **Phạt góc & thẻ phạt**:
   - Sử dụng mô hình **Negative Binomial** để xử lý hiện tượng phân tán quá mức (overdispersion). Do thiếu odds thị trường chính thức, mọi tip góc và thẻ đều được gắn nhãn minh bạch: **"Thử nghiệm"** và **"Lean"**.
   - Hỗ trợ công cụ **Nhập Odds Thủ Công (Manual Odds Calculator)** trên UI để tính toán EV tức thời khi người dùng có tỷ lệ odds ngoài thực tế.

---

## 🛡️ Nguyên Tắc Chống Rò Rỉ Dữ Liệu (Anti-Leakage)

- **Walk-Forward Expanding Window**: Mọi chỉ số xếp hạng (Elo, Pi-ratings, Dixon-Coles attack/defense) của trận đấu ở thời điểm $t$ chỉ được tính dựa trên các trận đấu đã kết thúc **nghiêm ngặt trước thời điểm $t$**.
- **Hai chế độ dự đoán độc lập**:
  - **T-24h**: Sử dụng độc quyền odds MỞ (Open). Tuyệt đối không dùng odds đóng.
  - **T-1h**: Cho phép sử dụng odds ĐÓNG (Close) như thông tin cập nhật cuối cùng của thị trường.
- **Tính bất biến khi hoán vị tương lai**: Đã kiểm định tự động bằng test `test_future_permutation_invariance`: thay đổi hoặc xóa bỏ các kết quả tương lai không làm dịch chuyển bất kỳ xác suất nào của trận $t$.

---

## 📁 Cấu Trúc Mã Nguồn

```
./
├── Makefile                                # make test, make backtest, make predict, make audit
├── README.md                               # Tài liệu hướng dẫn & công bố mô hình
├── LICENSE                                 # Giấy phép MIT mã nguồn mở
├── docker-compose.yml                      # Triển khai 1 lệnh Full-Stack (Backend + Frontend)
├── data_league/                            # 25 CSVs gốc từ football-data.co.uk (2022/23 - 2026/27)
├── Lich_Thi_Dau/                           # Lịch thi đấu chính thức 5 giải (2026/27) nạp vào SQLite
├── tree-maker/                             # Công cụ & snapshot cấu trúc cây dự án
├── backend/
│   ├── cli.py                              # CLI đa năng (audit, backtest, predict)
│   ├── reports/                            # Báo cáo backtest tự động (MD, HTML, model_card.json)
│   ├── app/
│   │   ├── main.py                         # FastAPI App
│   │   ├── api/routes.py                   # REST endpoints (/fixtures, /predict/upcoming, /manual/eval)
│   │   ├── data/
│   │   │   ├── csv_loader.py               # Loader 25 CSVs, BOM utf-8-sig, fallback odds, audit
│   │   │   ├── schedule_parser.py          # Bộ phân tích lịch thi đấu tiếng Việt từ Lich_Thi_Dau
│   │   │   └── sync_database.py            # Đồng bộ lịch thi đấu và tỷ lệ vào keolab.db
│   │   ├── math/
│   │   │   ├── dixon_coles.py              # M2: Dixon-Coles MLE fitting & time-decay
│   │   │   ├── market_implied.py           # M6: Giải ngược ma trận từ odds thị trường (Prior)
│   │   │   ├── shot_xg.py                  # M5: Shot-based xG proxy Poisson GLM
│   │   │   ├── residual_lgbm.py            # M7: LightGBM học phần dư thị trường + SHAP
│   │   │   ├── ensemble.py                 # M8: Log-linear pooling w in [0, 1]
│   │   │   ├── corners_cards.py            # Negative Binomial góc & thẻ phạt (Thử nghiệm)
│   │   │   └── tip_engine.py               # EV, Edge, Empirical Shrinkage, Kelly fractional (1/4)
│   │   └── backtest/
│   │       ├── walkforward.py              # Engine backtest mở rộng theo thời gian & tính CLV
│   │       └── optimizer.py                # Tối ưu siêu tham số Optuna
│   └── tests/                              # Bộ 35 tests Pytest (Golden test, Benchmark, Anti-leakage, AH...)
└── frontend/                               # Next.js 14 App Router, TypeScript, TailwindCSS
```

---

*KèoLab Engine v2.1 - Developed for Academic & Entertainment Sports Analytics*
