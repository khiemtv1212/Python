"""
Công cụ phân tích thị trường AI hoàn chỉnh
Kết hợp phân tích kỹ thuật + ML dự đoán + cảnh báo giao dịch
"""
import json
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('market_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ComprehensiveAnalyzer:
    """Công cụ phân tích thị trường toàn diện"""
    
    def __init__(self, config_file='config.json'):
        """
        Khởi tạo analyzer
        
        Args:
            config_file (str): Đường dẫn file config
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logger.info("✅ Đã tải config thành công")
        except FileNotFoundError:
            logger.error(f"❌ Không tìm thấy file {config_file}")
            self.config = self._default_config()
    
    @staticmethod
    def _default_config():
        """Cấu hình mặc định"""
        return {
            "cryptos": [
                {"name": "Bitcoin", "symbol": "bitcoin", "days": 365},
                {"name": "Ethereum", "symbol": "ethereum", "days": 365},
                {"name": "Cardano", "symbol": "cardano", "days": 365},
                {"name": "Solana", "symbol": "solana", "days": 365},
                {"name": "Ripple", "symbol": "ripple", "days": 365}
            ],
            "stocks": [
                {"name": "Apple", "symbol": "AAPL", "days": 365},
                {"name": "Microsoft", "symbol": "MSFT", "days": 365},
                {"name": "Google", "symbol": "GOOGL", "days": 365},
                {"name": "Tesla", "symbol": "TSLA", "days": 365},
                {"name": "Amazon", "symbol": "AMZN", "days": 365}
            ],
            "update_interval": 3600,  # 1 giờ
            "prediction_days": 30,
            "lookback_window": 60
        }
    
    def analyze_all(self) -> Dict:
        """
        Phân tích tất cả tài sản
        
        Returns:
            Dict: Kết quả phân tích cho tất cả tài sản
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'cryptos': {},
            'stocks': {}
        }
        
        # Phân tích crypto
        for crypto in self.config.get('cryptos', []):
            try:
                analysis = self.analyze_asset(
                    name=crypto['name'],
                    symbol=crypto['symbol'],
                    asset_type='crypto',
                    days=crypto.get('days', 365)
                )
                results['cryptos'][crypto['symbol']] = analysis
            except Exception as e:
                logger.error(f"❌ Lỗi khi phân tích {crypto['name']}: {e}")
        
        # Phân tích chứng khoán
        for stock in self.config.get('stocks', []):
            try:
                analysis = self.analyze_asset(
                    name=stock['name'],
                    symbol=stock['symbol'],
                    asset_type='stock',
                    days=stock.get('days', 365)
                )
                results['stocks'][stock['symbol']] = analysis
            except Exception as e:
                logger.error(f"❌ Lỗi khi phân tích {stock['name']}: {e}")
        
        return results
    
    def analyze_asset(self, name: str, symbol: str, asset_type: str, days: int = 365) -> Dict:
        """
        Phân tích một tài sản
        
        Args:
            name (str): Tên tài sản
            symbol (str): Mã tài sản
            asset_type (str): 'crypto' hoặc 'stock'
            days (int): Số ngày dữ liệu
            
        Returns:
            Dict: Kết quả phân tích
        """
        logger.info(f"🔍 Đang phân tích {name} ({symbol})...")
        
        try:
            # Lấy dữ liệu
            from data_fetcher import DataFetcher
            if asset_type == 'crypto':
                df = DataFetcher.fetch_crypto_data(symbol, days)
            else:
                df = DataFetcher.fetch_stock_data(symbol, days)
            
            if df is None or df.empty:
                return {'error': f'Không có dữ liệu cho {symbol}'}
            
            # Phân tích kỹ thuật
            from technical_analyzer import TechnicalAnalyzer
            analyzer = TechnicalAnalyzer()
            df = analyzer.analyze(df)
            
            # Dự đoán ML
            from ml_predictor import LSTMPredictor
            predictor = LSTMPredictor(lookback=self.config.get('lookback_window', 60))
            prediction_days = self.config.get('prediction_days', 30)
            
            try:
                future_prices = predictor.predict(df, days=prediction_days)
            except Exception as e:
                logger.warning(f"⚠️ Không thể dự đoán giá cho {symbol}: {e}")
                future_prices = None
            
            # Tạo cảnh báo
            from alert_system import AlertSystem
            alert_system = AlertSystem()
            alerts = alert_system.generate_alerts(name, df, future_prices)
            
            # Compile kết quả
            result = {
                'success': True,
                'symbol': symbol,
                'name': name,
                'type': asset_type,
                'last_update': datetime.now().isoformat(),
                'technical_indicators': self._extract_latest_indicators(df),
                'alerts': [str(a) for a in alerts],
                'prediction': {
                    'next_30_days': future_prices.tolist() if future_prices is not None else None,
                    'predicted_price_30d': float(future_prices[-1]) if future_prices is not None else None
                },
                'price_stats': {
                    'current_price': float(df['Close'].iloc[-1]),
                    'high_52w': float(df['Close'].max()),
                    'low_52w': float(df['Close'].min()),
                    'avg_price': float(df['Close'].mean()),
                    'volatility': float(df['Close'].pct_change().std())
                }
            }
            
            logger.info(f"✅ Hoàn tất phân tích {name}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Lỗi phân tích {name}: {e}")
            return {'error': str(e), 'symbol': symbol}
    
    @staticmethod
    def _extract_latest_indicators(df: pd.DataFrame) -> Dict:
        """Trích xuất các chỉ báo mới nhất"""
        latest = df.iloc[-1] if len(df) > 0 else None
        if latest is None:
            return {}
        
        indicators = {}
        
        # Moving Averages
        for col in df.columns:
            if 'MA_' in col or 'SMA_' in col:
                indicators[col] = float(latest[col]) if pd.notna(latest[col]) else None
        
        # RSI
        if 'RSI' in df.columns:
            indicators['RSI'] = float(latest['RSI']) if pd.notna(latest['RSI']) else None
        
        # MACD
        if 'MACD' in df.columns:
            indicators['MACD'] = float(latest['MACD']) if pd.notna(latest['MACD']) else None
            indicators['MACD_Signal'] = float(latest['MACD_Signal']) if 'MACD_Signal' in df.columns and pd.notna(latest['MACD_Signal']) else None
        
        # Bollinger Bands
        if 'BB_Upper' in df.columns:
            indicators['BB_Upper'] = float(latest['BB_Upper']) if pd.notna(latest['BB_Upper']) else None
            indicators['BB_Middle'] = float(latest['BB_Middle']) if 'BB_Middle' in df.columns and pd.notna(latest['BB_Middle']) else None
            indicators['BB_Lower'] = float(latest['BB_Lower']) if pd.notna(latest['BB_Lower']) else None
        
        # ATR
        if 'ATR' in df.columns:
            indicators['ATR'] = float(latest['ATR']) if pd.notna(latest['ATR']) else None
        
        return indicators
    
    def export_results(self, results: Dict, output_file='analysis_results.json'):
        """Xuất kết quả ra file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Đã xuất kết quả ra {output_file}")
        except Exception as e:
            logger.error(f"❌ Lỗi xuất kết quả: {e}")
    
    def print_summary(self, results: Dict):
        """In bản tóm tắt"""
        print("\n" + "="*80)
        print("📊 BÁO CÁO PHÂN TÍCH THỊ TRƯỜNG CRYPTO VÀ CHỨNG KHOÁN")
        print("="*80)
        print(f"⏰ Thời gian: {results['timestamp']}\n")
        
        # Crypto
        if results.get('cryptos'):
            print("🪙 CRYPTO\n" + "-"*80)
            for symbol, data in results['cryptos'].items():
                if data.get('success'):
                    print(f"\n{data['name']} ({symbol})")
                    print(f"  💰 Giá hiện tại: ${data['price_stats']['current_price']:.2f}")
                    print(f"  📈 Volatility: {data['price_stats']['volatility']:.4f}")
                    if data['prediction']['predicted_price_30d']:
                        print(f"  🔮 Dự đoán 30 ngày: ${data['prediction']['predicted_price_30d']:.2f}")
                    if data['alerts']:
                        print(f"  🚨 Cảnh báo: {', '.join(data['alerts'][:2])}")
        
        # Stocks
        if results.get('stocks'):
            print("\n\n📈 CHỨNG KHOÁN\n" + "-"*80)
            for symbol, data in results['stocks'].items():
                if data.get('success'):
                    print(f"\n{data['name']} ({symbol})")
                    print(f"  💰 Giá hiện tại: ${data['price_stats']['current_price']:.2f}")
                    print(f"  📈 Volatility: {data['price_stats']['volatility']:.4f}")
                    if data['prediction']['predicted_price_30d']:
                        print(f"  🔮 Dự đoán 30 ngày: ${data['prediction']['predicted_price_30d']:.2f}")
                    if data['alerts']:
                        print(f"  🚨 Cảnh báo: {', '.join(data['alerts'][:2])}")
        
        print("\n" + "="*80)


if __name__ == '__main__':
    analyzer = ComprehensiveAnalyzer()
    results = analyzer.analyze_all()
    analyzer.print_summary(results)
    analyzer.export_results(results)
