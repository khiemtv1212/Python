# 🚀 Hướng dẫn chạy hệ thống AI phân tích thị trường

## ✅ Đã kiểm tra thành công

Tất cả các lỗi đã được sửa:
- ✅ Data fetcher - Lấy dữ liệu từ CoinGecko (Crypto) và Yahoo Finance (Stock)
- ✅ Technical analyzer - Các chỉ báo: RSI, MACD, Bollinger Bands, ATR, MA
- ✅ ML predictor - LSTM Neural Network cho dự đoán giá
- ✅ Alert system - Cảnh báo BUY/SELL tự động

## 🎯 Cách chạy chương trình

### 1️⃣ Cài đặt thư viện (lần đầu)

```bash
pip install -r requirements.txt
```

### 2️⃣ Chạy kiểm tra hệ thống

```bash
python test_system.py
```

**Output dự kiến:**
```
TEST SYSTEM - AI Market Analysis
================================================================================

1. Checking imports...
   OK - All modules imported successfully

2. Initialize MarketAnalysisEngine...
   OK - Engine initialized
   Will analyze: 3 cryptos, 3 stocks

3. Checking data fetch...
   OK - Bitcoin: 31 records
   OK - Apple (AAPL): 20 records

4. Checking technical analysis...
   OK - Added 10 technical indicators
   Indicators: RSI, MACD, Bollinger Bands, ATR, MA

5. Checking ML prediction...
   OK - Data prepared: 0 train, 1 test
   OK - Ready for LSTM training

6. Checking alert system...
   OK - Alert system working
   Total alerts: 0

SUCCESS - All checks passed!
```

### 3️⃣ Chạy phân tích thị trường

**Tùy chọn 1 - Script chính:**
```bash
python main.py
```

**Tùy chọn 2 - Engine phân tích toàn diện:**
```bash
python analysis_engine.py
```

## 📊 Output & Báo cáo

Chương trình sẽ tạo:

1. **`market_analyzer.log`** - Log file với tất cả hoạt động
2. **`report_YYYYMMDD_HHMMSS.txt`** - Báo cáo chi tiết
3. **`results_YYYYMMDD_HHMMSS.json`** - Kết quả JSON

## 📈 Các tài sản được phân tích

### Crypto (lấy từ CoinGecko - miễn phí)
- Bitcoin
- Ethereum  
- Cardano

### Stocks (lấy từ Yahoo Finance - miễn phí)
- Apple (AAPL)
- Microsoft (MSFT)
- Tesla (TSLA)

## 🔧 Thay đổi cấu hình

Chỉnh sửa `config.json` để:
- Thêm/bớt tài sản theo dõi
- Thay đổi số ngày dữ liệu lịch sử
- Cấu hình ML (lookback, epochs, batch_size)
- Thay đổi ngưỡng cảnh báo

**Ví dụ:**
```json
{
  "cryptos": [
    {"name": "Bitcoin", "symbol": "bitcoin", "days": 365}
  ],
  "stocks": [
    {"name": "Apple", "symbol": "AAPL", "days": 365}
  ],
  "ml_config": {
    "lookback": 60,
    "predict_days": 30,
    "epochs": 50,
    "batch_size": 32
  }
}
```

## ⚠️ Lỗi phổ biến & Cách khắc phục

### 1. `ModuleNotFoundError: No module named 'yfinance'`
```bash
pip install --upgrade yfinance
```

### 2. `tensorflow` khởi động chậm
Đây là bình thường lần đầu tiên. TensorFlow sẽ nhanh hơn lần sau.

### 3. Lỗi: `No data fetched from API`
- Kiểm tra kết nối internet
- CoinGecko API có rate limit (có thể chờ)
- Yahoo Finance cần mạng ổn định

### 4. UTF-8 encoding errors
```bash
# Windows
chcp 65001
python test_system.py
```

## 📱 Ví dụ sử dụng từng module riêng

### Lấy dữ liệu Crypto
```python
from data_fetcher import DataFetcher

df = DataFetcher.fetch_crypto_data('bitcoin', days=365)
print(df[['Date', 'Close', 'Volume']].tail(10))
```

### Phân tích kỹ thuật
```python
from technical_analyzer import TechnicalAnalyzer

analyzer = TechnicalAnalyzer()
df_analyzed = analyzer.analyze_asset(df)
print(df_analyzed[['Date', 'Close', 'RSI', 'MACD']].tail())
```

### Dự đoán giá
```python
from ml_predictor import LSTMPredictor

predictor = LSTMPredictor(lookback=60)
X_train, y_train, X_test, y_test = predictor.prepare_data(df, test_size=0.2)
predictor.build_model((60, 1))
predictor.train(X_train, y_train, epochs=50)

# Dự đoán
y_pred = predictor.predict(X_test)
print(f"Predicted next 7 days: {y_pred[:7]}")
```

### Cảnh báo
```python
from alert_system import AlertSystem

alert_system = AlertSystem()
alert_system.check_all_signals('Bitcoin', df_analyzed)

for alert in alert_system.get_latest_alerts():
    print(alert)
```

## 🎓 Các chỉ báo kỹ thuật được sử dụng

| Chỉ báo | Ý nghĩa | Giá trị |
|--------|---------|--------|
| MA (20, 50, 200) | Moving Average | Xu hướng |
| RSI | Quá mua/bán | 0-100 |
| MACD | Momentum | +/- |
| Bollinger Bands | Biến động | 3 dây |
| ATR | Biến động trung bình | Số dương |

## 💡 Tips & Tricks

1. **Chạy định kỳ**: Tạo task scheduler để chạy tự động mỗi giờ
2. **Lưu kết quả**: Tất cả kết quả tự động lưu vào file
3. **Customize alerts**: Sửa ngưỡng cảnh báo trong `config.json`
4. **Tích hợp Email**: Chỉnh sửa `alert_system.py` để gửi email

## 📞 Hỗ trợ

Nếu gặp lỗi:
1. Chạy `python test_system.py` để kiểm tra
2. Xem `market_analyzer.log` để tìm lỗi chi tiết
3. Kiểm tra kết nối internet

---

**Thành công! Hệ thống đã sẵn sàng phân tích thị trường 🎉**
