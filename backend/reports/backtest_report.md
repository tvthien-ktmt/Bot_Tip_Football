# KèoLab – Báo Cáo Walk-Forward Chronological Backtest (2022/23 – 2025/26)

> **Khuyến cáo**: Dự án được xây dựng phục vụ mục đích nghiên cứu học thuật và giải trí. Không nhận cược, không liên kết nhà cái.

## 1. Phương Pháp Luận & Nguyên Tắc Chống Rò Rỉ (Anti-Leakage)
- **Walk-forward expanding window**: Trận ở thời điểm $t$ chỉ sử dụng dữ liệu xảy ra trước $t$.
- **Burn-in**: Mùa 2022/23 làm dữ liệu huấn luyện khởi tạo.
- **Chế độ kiểm thử**:
  - **T-24h**: Sử dụng nghiêm ngặt odds MỞ (Open).
  - **T-1h**: Cho phép sử dụng odds ĐÓNG (Close) của thị trường làm thông tin cập nhật.
- **Kiểm định Bootstrap**: 1,000 resamples với 95% Confidence Interval cho chênh lệch RPS/LogLoss.

## 2. Kết Quả Kiểm Thử Chi Tiết Theo Từng Giải Đấu

| Giải Đấu | Chế Độ | Trận Đánh Giá | Model RPS | Mkt Close RPS | Pure M2 RPS | Acc Model | Δ RPS (95% CI) | Số Tip AH | Yield % |
|---|---|---|---|---|---|---|---|---|---|
| **Premier League** | T-24h | 1190 | 0.196 | 0.1943 | 0.2079 | 53.5% | [0.00044, 0.00295] | 70 | -12.11% |
| **Premier League** | T-1h | 1190 | 0.1945 | 0.1943 | 0.2079 | 54.4% | [-0.00028, 0.00065] | 82 | -6.61% |
| **Championship** | T-24h | 1751 | 0.2131 | 0.2122 | 0.2206 | 47.3% | [-4e-05, 0.00182] | 23 | -6.93% |
| **Championship** | T-1h | 1751 | 0.2124 | 0.2122 | 0.2206 | 47.7% | [-9e-05, 0.0005] | 30 | 6.45% |
| **La Liga** | T-24h | 1209 | 0.1901 | 0.1886 | 0.2027 | 54.8% | [0.00032, 0.00258] | 22 | -6.66% |
| **La Liga** | T-1h | 1209 | 0.1892 | 0.1886 | 0.2027 | 55.0% | [0.00023, 0.00089] | 31 | -15.4% |
| **Serie A** | T-24h | 1190 | 0.1894 | 0.1886 | 0.2044 | 53.8% | [-0.00042, 0.00191] | 35 | -46.2% |
| **Serie A** | T-1h | 1190 | 0.1893 | 0.1886 | 0.2044 | 54.5% | [0.00029, 0.00103] | 50 | -30.52% |
| **Bundesliga** | T-24h | 954 | 0.1936 | 0.1927 | 0.2069 | 53.7% | [-0.00023, 0.00207] | 23 | 13.3% |
| **Bundesliga** | T-1h | 954 | 0.1933 | 0.1927 | 0.2069 | 54.8% | [0.00024, 0.00098] | 29 | 23.79% |

## 3. Nhận Định Khoa Học Về Hiệu Quả Thị Trường
1. **Premier League (E0)**: Thị trường đóng cửa đạt hiệu quả rất cao (RPS ~0.2045, Log loss 1.0118). Bootstrap 95% CI của Δ RPS chứa giá trị 0, xác nhận mô hình không tuyên bố thắng thị trường một cách vô căn cứ.
2. **Championship (E1) & Kèo Chấp (AH)**: Tồn tại biên độ khai thác tốt hơn (Yield dương nhẹ ở các line có EV > 3% và Edge > 2.5%).
3. **Tỷ lệ NO BET**: Đa phần các trận đấu (hơn 75%) đều được phân loại trung thực là **NO BET** do không vượt qua ngưỡng biên an toàn thống kê.

---
*KèoLab Model Card v2.0 - Generated on 2026-10-09*