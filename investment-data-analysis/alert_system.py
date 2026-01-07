"""
Module cảnh báo giao dịch
"""
import pandas as pd
import logging
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Mức độ cảnh báo"""
    CRITICAL = "🔴 NGUY HIỂM"
    HIGH = "🟠 CAO"
    MEDIUM = "🟡 TRUNG BÌNH"
    LOW = "🟢 THẤP"


class Alert:
    """Lớp cảnh báo"""
    
    def __init__(self, asset_name, alert_type, level, message, price=None, timestamp=None):
        self.asset_name = asset_name
        self.alert_type = alert_type  # 'BUY', 'SELL', 'PRICE_LEVEL', 'VOLATILITY'
        self.level = level
        self.message = message
        self.price = price
        self.timestamp = timestamp or datetime.now()
    
    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.level.value} {self.asset_name}: {self.message}"


class AlertSystem:
    """Hệ thống cảnh báo giao dịch"""
    
    def __init__(self):
        self.alerts = []
        self.thresholds = {
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'price_change_percent': 5,  # % thay đổi giá
            'volatility_threshold': 0.5,  # ATR threshold
        }
    
    def check_buy_signals(self, asset_name, df):
        """
        Kiểm tra tín hiệu mua
        
        Args:
            asset_name (str): Tên tài sản
            df (pd.DataFrame): DataFrame phân tích
        """
        if df.empty or len(df) < 50:
            return
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Kiểm tra RSI oversold
        if latest['RSI'] < self.thresholds['rsi_oversold'] and prev['RSI'] >= self.thresholds['rsi_oversold']:
            self.add_alert(
                asset_name,
                'BUY',
                AlertLevel.MEDIUM,
                f"RSI vào vùng Oversold ({latest['RSI']:.1f})",
                latest['Close']
            )
        
        # Kiểm tra MA crossover (20 > 50)
        if (latest['MA_20'] > latest['MA_50'] and 
            prev['MA_20'] <= prev['MA_50']):
            self.add_alert(
                asset_name,
                'BUY',
                AlertLevel.MEDIUM,
                "MA20 vượt lên MA50 (Golden Cross)",
                latest['Close']
            )
        
        # Kiểm tra MACD bullish crossover
        if (latest['MACD'] > latest['Signal_Line'] and 
            prev['MACD'] <= prev['Signal_Line']):
            self.add_alert(
                asset_name,
                'BUY',
                AlertLevel.LOW,
                "MACD vượt lên Signal Line (Bullish)",
                latest['Close']
            )
        
        # Kiểm tra giá chạm Bollinger Bands dưới
        if (latest['Close'] < latest['BB_Lower'] and 
            prev['Close'] >= prev['BB_Lower']):
            self.add_alert(
                asset_name,
                'BUY',
                AlertLevel.MEDIUM,
                f"Giá chạm dây Bollinger dưới (${latest['Close']:.2f})",
                latest['Close']
            )
    
    def check_sell_signals(self, asset_name, df):
        """
        Kiểm tra tín hiệu bán
        
        Args:
            asset_name (str): Tên tài sản
            df (pd.DataFrame): DataFrame phân tích
        """
        if df.empty or len(df) < 50:
            return
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Kiểm tra RSI overbought
        if latest['RSI'] > self.thresholds['rsi_overbought'] and prev['RSI'] <= self.thresholds['rsi_overbought']:
            self.add_alert(
                asset_name,
                'SELL',
                AlertLevel.MEDIUM,
                f"RSI vào vùng Overbought ({latest['RSI']:.1f})",
                latest['Close']
            )
        
        # Kiểm tra MA crossover (20 < 50)
        if (latest['MA_20'] < latest['MA_50'] and 
            prev['MA_20'] >= prev['MA_50']):
            self.add_alert(
                asset_name,
                'SELL',
                AlertLevel.MEDIUM,
                "MA20 rơi dưới MA50 (Death Cross)",
                latest['Close']
            )
        
        # Kiểm tra MACD bearish crossover
        if (latest['MACD'] < latest['Signal_Line'] and 
            prev['MACD'] >= prev['Signal_Line']):
            self.add_alert(
                asset_name,
                'SELL',
                AlertLevel.LOW,
                "MACD rơi xuống Signal Line (Bearish)",
                latest['Close']
            )
        
        # Kiểm tra giá chạm Bollinger Bands trên
        if (latest['Close'] > latest['BB_Upper'] and 
            prev['Close'] <= prev['BB_Upper']):
            self.add_alert(
                asset_name,
                'SELL',
                AlertLevel.MEDIUM,
                f"Giá chạm dây Bollinger trên (${latest['Close']:.2f})",
                latest['Close']
            )
    
    def check_price_levels(self, asset_name, df, support_resistance=None):
        """
        Kiểm tra mức hỗ trợ/kháng cự
        
        Args:
            asset_name (str): Tên tài sản
            df (pd.DataFrame): DataFrame
            support_resistance (dict): Dict với key 'support', 'resistance'
        """
        if df.empty:
            return
        
        latest = df.iloc[-1]
        current_price = latest['Close']
        
        # Tính hỗ trợ/kháng cự từ dữ liệu nếu không có
        if support_resistance is None:
            resistance = df['High'].tail(50).max()
            support = df['Low'].tail(50).min()
        else:
            resistance = support_resistance.get('resistance')
            support = support_resistance.get('support')
        
        # Kiểm tra gần resistance
        if support and resistance:
            distance_to_resistance = resistance - current_price
            distance_to_support = current_price - support
            
            if distance_to_resistance > 0 and distance_to_resistance < (resistance - support) * 0.1:
                self.add_alert(
                    asset_name,
                    'PRICE_LEVEL',
                    AlertLevel.HIGH,
                    f"Giá gần mức kháng cự (${resistance:.2f})",
                    current_price
                )
            
            if distance_to_support > 0 and distance_to_support < (resistance - support) * 0.1:
                self.add_alert(
                    asset_name,
                    'PRICE_LEVEL',
                    AlertLevel.HIGH,
                    f"Giá gần mức hỗ trợ (${support:.2f})",
                    current_price
                )
    
    def check_volatility(self, asset_name, df):
        """
        Kiểm tra biến động giá
        
        Args:
            asset_name (str): Tên tài sản
            df (pd.DataFrame): DataFrame
        """
        if df.empty or 'ATR' not in df.columns:
            return
        
        latest = df.iloc[-1]
        
        # Tính volatility ratio (ATR/Close)
        volatility_ratio = latest['ATR'] / latest['Close'] if latest['Close'] > 0 else 0
        
        if volatility_ratio > self.thresholds['volatility_threshold']:
            self.add_alert(
                asset_name,
                'VOLATILITY',
                AlertLevel.CRITICAL,
                f"Biến động cao (ATR: ${latest['ATR']:.2f})",
                latest['Close']
            )
    
    def add_alert(self, asset_name, alert_type, level, message, price=None):
        """
        Thêm cảnh báo
        
        Args:
            asset_name (str): Tên tài sản
            alert_type (str): Loại cảnh báo
            level (AlertLevel): Mức độ
            message (str): Nội dung
            price (float): Giá hiện tại
        """
        alert = Alert(asset_name, alert_type, level, message, price)
        self.alerts.append(alert)
        logger.info(str(alert))
    
    def check_all_signals(self, asset_name, df):
        """
        Kiểm tra tất cả tín hiệu
        
        Args:
            asset_name (str): Tên tài sản
            df (pd.DataFrame): DataFrame phân tích
        """
        self.check_buy_signals(asset_name, df)
        self.check_sell_signals(asset_name, df)
        self.check_price_levels(asset_name, df)
        self.check_volatility(asset_name, df)
    
    def get_latest_alerts(self, limit=10):
        """
        Lấy các cảnh báo gần đây
        
        Args:
            limit (int): Số cảnh báo
            
        Returns:
            list: Danh sách cảnh báo
        """
        return self.alerts[-limit:]
    
    def clear_old_alerts(self, hours=24):
        """
        Xóa các cảnh báo cũ
        
        Args:
            hours (int): Giữ cảnh báo trong bao nhiêu giờ
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff_time]
    
    def generate_report(self):
        """
        Tạo báo cáo cảnh báo
        
        Returns:
            str: Báo cáo dạng text
        """
        if not self.alerts:
            return "Không có cảnh báo nào"
        
        report = "=" * 60 + "\n"
        report += "📊 BÁO CÁO CẢNH BÁO GIAO DỊCH\n"
        report += "=" * 60 + "\n\n"
        
        # Nhóm theo tài sản
        by_asset = {}
        for alert in self.alerts:
            if alert.asset_name not in by_asset:
                by_asset[alert.asset_name] = []
            by_asset[alert.asset_name].append(alert)
        
        for asset_name, asset_alerts in by_asset.items():
            report += f"\n🏷️  {asset_name}\n"
            report += "-" * 60 + "\n"
            
            for alert in asset_alerts[-5:]:  # Show last 5
                report += f"  {alert}\n"
                if alert.price:
                    report += f"     Giá: ${alert.price:.2f}\n"
        
        return report


if __name__ == "__main__":
    # Test
    from data_fetcher import DataFetcher
    from technical_analyzer import TechnicalAnalyzer
    
    print("=" * 50)
    print("TEST: Hệ thống cảnh báo")
    print("=" * 50)
    
    btc_data = DataFetcher.fetch_crypto_data("bitcoin", days=365)
    btc_analyzed = TechnicalAnalyzer.analyze_asset(btc_data)
    
    alert_system = AlertSystem()
    alert_system.check_all_signals("Bitcoin", btc_analyzed)
    
    print(alert_system.generate_report())
