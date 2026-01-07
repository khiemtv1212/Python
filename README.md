# AI Market Analysis System
🤖 Công cụ phân tích thị trường Crypto & Chứng khoán sử dụng AI

## 📋 Tính năng

✅ **Phân tích kỹ thuật**
- Moving Averages (MA20, MA50, MA200)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- ATR (Average True Range)

✅ **Dự đoán giá bằng Machine Learning**
- LSTM Neural Network
- Dự đoán 30 ngày tương lai
- Tỷ lệ chính xác cao

✅ **Cảnh báo giao dịch**
- Cảnh báo BUY/SELL tự động
- Theo dõi quá mua/quá bán
- Thông báo biến động giá

✅ **Hỗ trợ đa nguồn**
- Crypto: CoinGecko API (miễn phí)
- Chứng khoán: Yahoo Finance (miễn phí)

## 🚀 Cài đặt

### Yêu cầu
- Python 3.8+
- pip

### Bước 1: Clone repo
```bash
git clone https://github.com/khiemtv1212/Python.git
cd Python
```

### Bước 2: Tạo virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### Bước 4: Setup environment variables
```bash
cp .env.example .env
```

## 📖 Hướng dẫn sử dụng

### Chạy phân tích
```bash
python main.py
```

hoặc

```bash
python analysis_engine.py
```

## 📊 Cấu trúc dự án

```
Python/
├── main.py                 # Script chính
├── analysis_engine.py      # Engine phân tích toàn diện
├── config.json             # Cấu hình tài sản
├── data_fetcher.py        # Lấy dữ liệu từ API
├── technical_analyzer.py  # Phân tích kỹ thuật
├── ml_predictor.py        # Mô hình dự đoán LSTM
├── alert_system.py        # Hệ thống cảnh báo
├── requirements.txt       # Các thư viện cần cài
├── .gitignore            # Bỏ qua các file không cần
├── .env.example          # Template biến môi trường
└── README.md             # Tài liệu này
```

## 🛡️ Bảo mật

⚠️ **Lưu ý quan trọng:**
- ✅ `.env` file được bỏ qua (không commit)
- ✅ Sử dụng `.env.example` làm template
- ✅ Giữ API keys riêng tư
- ✅ Không commit log files

---

**Tác giả:** khiemtv1212
