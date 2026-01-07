"""
Main script: Chạy hệ thống phân tích thị trường AI
"""
import json
import pandas as pd
import logging
from datetime import datetime
import os

from data_fetcher import DataFetcher
from technical_analyzer import TechnicalAnalyzer
from ml_predictor import LSTMPredictor
from alert_system import AlertSystem

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('market_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MarketAnalysisEngine:
    """Engine phân tích thị trường"""
    
    def __init__(self, config_file='config.json'):
        """
        Khởi tạo engine
        
        Args:
            config_file (str): Đường dẫn file config
        """
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.alert_system = AlertSystem()
        self.results = {}
    
    def analyze_asset(self, asset_name, asset_type, symbol):
        """
        Phân tích một tài sản
        
        Args:
            asset_name (str): Tên tài sản
            asset_type (str): 'crypto' hoặc 'stock'
            symbol (str): Mã tài sản
            
        Returns:
            dict: Kết quả phân tích
        """
        logger.info(f"Đang phân tích {asset_name}...")
        
        result = {
            'name': asset_name,
            'type': asset_type,
            'timestamp': datetime.now().isoformat(),
            'data': None,
            'technical_signal': None,
            'predictions': None,
            'alerts': []
        }
        
        try:
            # 1. Lấy dữ liệu
            if asset_type == 'crypto':
                df = DataFetcher.fetch_crypto_data(symbol, days=365)
            else:
                df = DataFetcher.fetch_stock_data(symbol, days=365)
            
            if df.empty:
                logger.error(f"✗ Không thể lấy dữ liệu cho {asset_name}")
                return result
            
            result['data'] = df
            
            # 2. Phân tích kỹ thuật
            df_analyzed = TechnicalAnalyzer.analyze_asset(df)
            technical_signal = TechnicalAnalyzer.generate_signal(df_analyzed)
            result['technical_signal'] = technical_signal
            
            logger.info(f"  📊 Tín hiệu: {technical_signal}")
            
            # 3. Dự đoán giá (ML)
            ml_config = self.config.get('ml_config', {})
            predictor = LSTMPredictor(lookback=ml_config.get('lookback', 60))
            
            try:
                predictions, metrics = predictor.train_and_predict(
                    df,
                    periods=ml_config.get('predict_days', 7)
                )
                result['predictions'] = {
                    'values': predictions,
                    'metrics': metrics
                }
                
                logger.info(f"  📈 Dự đoán 7 ngày: {[f'${p:.2f}' for p in predictions[:3]]}...")
            except Exception as e:
                logger.warning(f"  ⚠️  Lỗi dự đoán ML: {str(e)}")
            
            # 4. Tạo cảnh báo
            self.alert_system.check_all_signals(asset_name, df_analyzed)
            asset_alerts = [str(a) for a in self.alert_system.alerts]
            result['alerts'] = asset_alerts
            
            logger.info(f"✓ Phân tích {asset_name} hoàn tất")
            
        except Exception as e:
            logger.error(f"✗ Lỗi phân tích {asset_name}: {str(e)}")
        
        return result
    
    def run_analysis(self):
        """
        Chạy phân tích cho tất cả tài sản
        
        Returns:
            dict: Kết quả phân tích
        """
        logger.info("=" * 60)
        logger.info(f"Bắt đầu phân tích thị trường lúc {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # Phân tích crypto
        for crypto in self.config.get('cryptos', []):
            result = self.analyze_asset(
                crypto['name'],
                'crypto',
                crypto['symbol']
            )
            self.results[crypto['name']] = result
        
        # Phân tích chứng khoán
        for stock in self.config.get('stocks', []):
            result = self.analyze_asset(
                stock['name'],
                'stock',
                stock['symbol']
            )
            self.results[stock['name']] = result
        
        return self.results
    
    def generate_report(self):
        """
        Tạo báo cáo chi tiết
        
        Returns:
            str: Báo cáo dạng text
        """
        report = "\n" + "=" * 80 + "\n"
        report += "🤖 BÁO CÁO PHÂN TÍCH THỊ TRƯỜNG AI\n"
        report += f"📅 Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 80 + "\n\n"
        
        for asset_name, result in self.results.items():
            if not result.get('data') is None or result.get('data').empty:
                continue
            
            report += f"\n🏷️  {result['name']} ({result['type'].upper()})\n"
            report += "-" * 80 + "\n"
            
            # Giá hiện tại
            current_price = result['data']['Close'].iloc[-1]
            prev_price = result['data']['Close'].iloc[-2]
            change = ((current_price - prev_price) / prev_price) * 100
            
            report += f"  Giá hiện tại: ${current_price:.2f} ({change:+.2f}%)\n"
            
            # Tín hiệu
            signal = result.get('technical_signal', 'N/A')
            report += f"  Tín hiệu: {signal}\n"
            
            # Dự đoán
            if result.get('predictions'):
                predictions = result['predictions']['values']
                metrics = result['predictions']['metrics']
                
                report += f"\n  📈 Dự đoán 7 ngày tới:\n"
                for i, pred in enumerate(predictions[:3], 1):
                    change_pred = ((pred - current_price) / current_price) * 100
                    report += f"    Ngày {i}: ${pred:.2f} ({change_pred:+.2f}%)\n"
                
                if metrics:
                    report += f"\n  📊 Độ chính xác (R²): {metrics.get('R2', 0):.4f}\n"
            
            # Cảnh báo
            if result.get('alerts'):
                report += f"\n  🚨 Cảnh báo:\n"
                for alert in result['alerts'][-3:]:
                    report += f"    - {alert}\n"
            
            report += "\n"
        
        # Cảnh báo chung
        report += "\n" + "-" * 80 + "\n"
        report += "📢 CẢNH BÁO HỆ THỐNG\n"
        report += "-" * 80 + "\n"
        report += self.alert_system.generate_report()
        
        return report
    
    def save_report(self, filename=None):
        """
        Lưu báo cáo vào file
        
        Args:
            filename (str): Tên file
        """
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        report = self.generate_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"✓ Báo cáo được lưu: {filename}")
    
    def save_results_json(self, filename=None):
        """
        Lưu kết quả dạng JSON
        
        Args:
            filename (str): Tên file
        """
        if filename is None:
            filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Chuyển đổi DataFrame sang JSON
        json_results = {}
        for asset_name, result in self.results.items():
            json_results[asset_name] = {
                'name': result['name'],
                'type': result['type'],
                'timestamp': result['timestamp'],
                'technical_signal': result['technical_signal'],
                'predictions': result.get('predictions'),
                'alerts': result.get('alerts', [])
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Kết quả được lưu: {filename}")


def main():
    """
    Hàm main: Chạy toàn bộ hệ thống
    """
    try:
        # Khởi tạo engine
        engine = MarketAnalysisEngine('config.json')
        
        # Chạy phân tích
        results = engine.run_analysis()
        
        # In báo cáo
        print(engine.generate_report())
        
        # Lưu báo cáo
        engine.save_report()
        engine.save_results_json()
        
        logger.info("=" * 60)
        logger.info("✓ Phân tích hoàn tất!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"✗ Lỗi chạy hệ thống: {str(e)}")
        raise


if __name__ == "__main__":
    main()
