"""
Module để lấy dữ liệu giá từ các API (CoinGecko, Yahoo Finance)
"""
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """Lấy dữ liệu giá từ các nguồn khác nhau"""

    COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
    
    @staticmethod
    def fetch_crypto_data(symbol, days=365):
        """
        Lấy dữ liệu giá crypto từ CoinGecko
        
        Args:
            symbol (str): Tên crypto (bitcoin, ethereum, cardano, ...)
            days (int): Số ngày dữ liệu lịch sử
            
        Returns:
            pd.DataFrame: DataFrame với cột (Date, Open, High, Low, Close, Volume)
        """
        try:
            logger.info(f"Đang lấy dữ liệu crypto: {symbol}")
            
            # Gọi API CoinGecko
            url = f"{DataFetcher.COINGECKO_API_URL}/coins/{symbol}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Xử lý dữ liệu
            prices = data['prices']
            volumes = data['total_volumes']
            
            df = pd.DataFrame({
                'Date': [datetime.fromtimestamp(p[0]/1000) for p in prices],
                'Close': [p[1] for p in prices],
                'Volume': [v[1] for v in volumes]
            })
            
            # Tính Open, High, Low (làm tròn từ Close)
            df['Open'] = df['Close'].shift(1).fillna(df['Close'].iloc[0])
            df['High'] = df['Close'].rolling(window=1).max()
            df['Low'] = df['Close'].rolling(window=1).min()
            
            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            df = df.sort_values('Date').reset_index(drop=True)
            
            logger.info(f"✓ Lấy dữ liệu {symbol} thành công: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"✗ Lỗi lấy dữ liệu crypto {symbol}: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def fetch_stock_data(symbol, days=365):
        """
        Lấy dữ liệu giá chứng khoán từ Yahoo Finance
        
        Args:
            symbol (str): Mã chứng khoán (AAPL, GOOGL, 0001.HK, ...)
            days (int): Số ngày dữ liệu lịch sử
            
        Returns:
            pd.DataFrame: DataFrame với cột (Date, Open, High, Low, Close, Volume)
        """
        try:
            logger.info(f"Đang lấy dữ liệu chứng khoán: {symbol}")
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            df = yf.download(
                symbol,
                start=start_date,
                end=end_date,
                progress=False,
                timeout=10
            )
            
            df = df.reset_index()
            
            # Xử lý tên cột động
            if 'Adj Close' in df.columns:
                df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
                df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
                df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            else:
                df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
                df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            
            df = df.sort_values('Date').reset_index(drop=True)
            
            logger.info(f"✓ Lấy dữ liệu {symbol} thành công: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"✗ Lỗi lấy dữ liệu chứng khoán {symbol}: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def fetch_multiple_assets(assets_config):
        """
        Lấy dữ liệu cho nhiều tài sản cùng lúc
        
        Args:
            assets_config (dict): Config từ config.json
            
        Returns:
            dict: Từ điển {asset_name: DataFrame}
        """
        data = {}
        
        # Lấy crypto
        for crypto in assets_config.get('cryptos', []):
            df = DataFetcher.fetch_crypto_data(
                crypto['symbol'],
                crypto.get('days', 365)
            )
            if not df.empty:
                data[f"{crypto['name']} (Crypto)"] = df
        
        # Lấy chứng khoán
        for stock in assets_config.get('stocks', []):
            df = DataFetcher.fetch_stock_data(
                stock['symbol'],
                stock.get('days', 365)
            )
            if not df.empty:
                data[f"{stock['name']} (Stock)"] = df
        
        return data


if __name__ == "__main__":
    # Test
    print("=" * 50)
    print("TEST: Lấy dữ liệu Bitcoin")
    print("=" * 50)
    btc = DataFetcher.fetch_crypto_data("bitcoin", days=90)
    print(btc.tail())
    
    print("\n" + "=" * 50)
    print("TEST: Lấy dữ liệu Apple Stock")
    print("=" * 50)
    aapl = DataFetcher.fetch_stock_data("AAPL", days=90)
    print(aapl.tail())
