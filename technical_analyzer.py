"""
Module phân tích kỹ thuật: tính toán các chỉ báo kỹ thuật
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """Tính toán các chỉ báo kỹ thuật"""
    
    @staticmethod
    def add_moving_averages(df, windows=[20, 50, 200]):
        """
        Thêm Moving Average (MA)
        
        Args:
            df (pd.DataFrame): DataFrame với cột Close
            windows (list): Các cửa sổ MA
            
        Returns:
            pd.DataFrame: DataFrame có thêm các cột MA
        """
        for window in windows:
            df[f'MA_{window}'] = df['Close'].rolling(window=window).mean()
        return df
    
    @staticmethod
    def add_rsi(df, period=14):
        """
        Thêm Relative Strength Index (RSI)
        
        RSI > 70: Quá mua (Overbought)
        RSI < 30: Quá bán (Oversold)
        """
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        return df
    
    @staticmethod
    def add_macd(df, fast=12, slow=26, signal=9):
        """
        Thêm MACD (Moving Average Convergence Divergence)
        """
        df['EMA_fast'] = df['Close'].ewm(span=fast).mean()
        df['EMA_slow'] = df['Close'].ewm(span=slow).mean()
        df['MACD'] = df['EMA_fast'] - df['EMA_slow']
        df['Signal_Line'] = df['MACD'].ewm(span=signal).mean()
        df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']
        
        # Xóa cột trung gian
        df = df.drop(['EMA_fast', 'EMA_slow'], axis=1)
        return df
    
    @staticmethod
    def add_bollinger_bands(df, period=20, std_dev=2):
        """
        Thêm Bollinger Bands
        """
        df['BB_MA'] = df['Close'].rolling(window=period).mean()
        bb_std = df['Close'].rolling(window=period).std()
        df['BB_Upper'] = df['BB_MA'] + (bb_std * std_dev)
        df['BB_Lower'] = df['BB_MA'] - (bb_std * std_dev)
        
        # Xóa cột trung gian
        df = df.drop(['BB_MA'], axis=1)
        return df
    
    @staticmethod
    def add_atr(df, period=14):
        """
        Thêm Average True Range (ATR) - đo biến động
        """
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = true_range.rolling(window=period).mean()
        return df
    
    @staticmethod
    def analyze_asset(df):
        """
        Phân tích tài sản: thêm tất cả chỉ báo
        
        Args:
            df (pd.DataFrame): DataFrame giá
            
        Returns:
            pd.DataFrame: DataFrame với tất cả chỉ báo
        """
        df = df.copy()
        
        try:
            df = TechnicalAnalyzer.add_moving_averages(df, [20, 50, 200])
            df = TechnicalAnalyzer.add_rsi(df, period=14)
            df = TechnicalAnalyzer.add_macd(df, fast=12, slow=26, signal=9)
            df = TechnicalAnalyzer.add_bollinger_bands(df, period=20)
            df = TechnicalAnalyzer.add_atr(df, period=14)
            
            logger.info("✓ Phân tích kỹ thuật hoàn tất")
        except Exception as e:
            logger.error(f"✗ Lỗi phân tích kỹ thuật: {str(e)}")
        
        return df
    
    @staticmethod
    def generate_signal(df):
        """
        Tạo tín hiệu giao dịch từ các chỉ báo
        
        Returns:
            str: 'BUY', 'SELL', hoặc 'HOLD'
        """
        if df.empty or len(df) < 50:
            return 'HOLD'
        
        latest = df.iloc[-1]
        
        signals = []
        
        # Tín hiệu từ MA
        if latest['Close'] > latest['MA_50'] > latest['MA_200']:
            signals.append('BUY')  # Uptrend
        elif latest['Close'] < latest['MA_50'] < latest['MA_200']:
            signals.append('SELL')  # Downtrend
        
        # Tín hiệu từ RSI
        if latest['RSI'] < 30:
            signals.append('BUY')  # Oversold
        elif latest['RSI'] > 70:
            signals.append('SELL')  # Overbought
        
        # Tín hiệu từ MACD
        if latest['MACD'] > latest['Signal_Line'] and df.iloc[-2]['MACD'] <= df.iloc[-2]['Signal_Line']:
            signals.append('BUY')  # Bullish crossover
        elif latest['MACD'] < latest['Signal_Line'] and df.iloc[-2]['MACD'] >= df.iloc[-2]['Signal_Line']:
            signals.append('SELL')  # Bearish crossover
        
        # Tín hiệu từ Bollinger Bands
        if latest['Close'] < latest['BB_Lower']:
            signals.append('BUY')  # Giá chạm dây dưới
        elif latest['Close'] > latest['BB_Upper']:
            signals.append('SELL')  # Giá chạm dây trên
        
        # Xác định tín hiệu cuối cùng
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        
        if buy_count > sell_count:
            return 'BUY'
        elif sell_count > buy_count:
            return 'SELL'
        else:
            return 'HOLD'


if __name__ == "__main__":
    # Test
    from data_fetcher import DataFetcher
    
    print("=" * 50)
    print("TEST: Phân tích kỹ thuật Bitcoin")
    print("=" * 50)
    
    btc_data = DataFetcher.fetch_crypto_data("bitcoin", days=365)
    btc_analyzed = TechnicalAnalyzer.analyze_asset(btc_data)
    
    print(btc_analyzed[['Date', 'Close', 'MA_20', 'MA_50', 'RSI', 'MACD']].tail())
    
    signal = TechnicalAnalyzer.generate_signal(btc_analyzed)
    print(f"\n📊 Tín hiệu hiện tại: {signal}")
