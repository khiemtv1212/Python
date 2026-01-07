"""
Module dự đoán giá sử dụng LSTM Neural Network
"""
import numpy as np
import pandas as pd
import logging
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tensorflow as tf
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.callbacks import EarlyStopping
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class LSTMPredictor:
    """Mô hình LSTM dự đoán giá"""
    
    def __init__(self, lookback=60):
        """
        Khởi tạo predictor
        
        Args:
            lookback (int): Số ngày để xem xét
        """
        self.lookback = lookback
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.history = None
    
    def prepare_data(self, df, test_size=0.2):
        """
        Chuẩn bị dữ liệu cho mô hình
        
        Args:
            df (pd.DataFrame): DataFrame với cột Close
            test_size (float): Tỷ lệ test data
            
        Returns:
            tuple: (X_train, y_train, X_test, y_test)
        """
        # Lấy dữ liệu Close
        data = df['Close'].values.reshape(-1, 1)
        
        # Chuẩn hóa dữ liệu
        scaled_data = self.scaler.fit_transform(data)
        
        # Tạo sequence
        X, y = [], []
        for i in range(len(scaled_data) - self.lookback):
            X.append(scaled_data[i:i + self.lookback])
            y.append(scaled_data[i + self.lookback])
        
        X, y = np.array(X), np.array(y)
        
        # Chia train/test
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        logger.info(f"✓ Dữ liệu chuẩn bị: {len(X_train)} train, {len(X_test)} test")
        
        return X_train, y_train, X_test, y_test
    
    def build_model(self, input_shape):
        """
        Xây dựng mô hình LSTM
        
        Args:
            input_shape (tuple): Hình dạng input (lookback, 1)
        """
        self.model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(units=50, return_sequences=True),
            Dropout(0.2),
            LSTM(units=50),
            Dropout(0.2),
            Dense(units=25),
            Dense(units=1)
        ])
        
        self.model.compile(
            optimizer='adam',
            loss='mean_squared_error',
            metrics=['mae']
        )
        
        logger.info("✓ Mô hình LSTM được xây dựng")
    
    def train(self, X_train, y_train, epochs=50, batch_size=32, validation_split=0.2):
        """
        Huấn luyện mô hình
        
        Args:
            X_train (np.array): Dữ liệu train
            y_train (np.array): Target train
            epochs (int): Số epoch
            batch_size (int): Batch size
            validation_split (float): Tỷ lệ validation
        """
        if self.model is None:
            self.build_model((X_train.shape[1], X_train.shape[2]))
        
        early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
        
        self.history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=[early_stop],
            verbose=0
        )
        
        logger.info(f"✓ Mô hình được huấn luyện xong")
    
    def evaluate(self, X_test, y_test):
        """
        Đánh giá mô hình
        
        Args:
            X_test (np.array): Dữ liệu test
            y_test (np.array): Target test
            
        Returns:
            dict: Các metric đánh giá
        """
        if self.model is None:
            return {}
        
        y_pred = self.model.predict(X_test, verbose=0)
        
        # Denormalize
        y_test_actual = self.scaler.inverse_transform(y_test)
        y_pred_actual = self.scaler.inverse_transform(y_pred)
        
        # Tính metric
        mse = mean_squared_error(y_test_actual, y_pred_actual)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test_actual, y_pred_actual)
        r2 = r2_score(y_test_actual, y_pred_actual)
        
        metrics = {
            'MSE': mse,
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2
        }
        
        logger.info(f"✓ Đánh giá mô hình:")
        logger.info(f"  - RMSE: ${rmse:.2f}")
        logger.info(f"  - MAE: ${mae:.2f}")
        logger.info(f"  - R²: {r2:.4f}")
        
        return metrics
    
    def predict_next(self, df, periods=7):
        """
        Dự đoán giá cho các ngày tiếp theo
        
        Args:
            df (pd.DataFrame): DataFrame dữ liệu lịch sử
            periods (int): Số ngày dự đoán
            
        Returns:
            list: Giá dự đoán cho periods ngày
        """
        if self.model is None:
            logger.error("✗ Mô hình chưa được huấn luyện")
            return []
        
        # Lấy dữ liệu cuối cùng
        data = df['Close'].values.reshape(-1, 1)
        scaled_data = self.scaler.transform(data)
        
        # Bắt đầu từ dữ liệu cuối cùng
        last_sequence = scaled_data[-self.lookback:].copy()
        
        predictions = []
        
        for _ in range(periods):
            # Dự đoán
            next_pred = self.model.predict(
                last_sequence.reshape(1, self.lookback, 1),
                verbose=0
            )
            
            # Lưu dự đoán
            predictions.append(next_pred[0, 0])
            
            # Cập nhật sequence
            last_sequence = np.append(last_sequence[1:], next_pred)
        
        # Denormalize
        predictions = np.array(predictions).reshape(-1, 1)
        predictions_actual = self.scaler.inverse_transform(predictions)
        
        return predictions_actual.flatten().tolist()
    
    def train_and_predict(self, df, periods=7):
        """
        Huấn luyện mô hình và dự đoán
        
        Args:
            df (pd.DataFrame): DataFrame dữ liệu
            periods (int): Số ngày dự đoán
            
        Returns:
            tuple: (predictions, metrics)
        """
        # Chuẩn bị dữ liệu
        X_train, y_train, X_test, y_test = self.prepare_data(df)
        
        # Xây dựng và huấn luyện
        self.build_model((X_train.shape[1], X_train.shape[2]))
        self.train(X_train, y_train, epochs=50)
        
        # Đánh giá
        metrics = self.evaluate(X_test, y_test)
        
        # Dự đoán
        predictions = self.predict_next(df, periods)
        
        return predictions, metrics


if __name__ == "__main__":
    # Test
    from data_fetcher import DataFetcher
    
    print("=" * 50)
    print("TEST: Dự đoán giá Bitcoin")
    print("=" * 50)
    
    btc_data = DataFetcher.fetch_crypto_data("bitcoin", days=365)
    
    predictor = LSTMPredictor(lookback=60)
    predictions, metrics = predictor.train_and_predict(btc_data, periods=7)
    
    print(f"\n📈 Dự đoán giá Bitcoin 7 ngày tới:")
    current_price = btc_data['Close'].iloc[-1]
    for i, pred in enumerate(predictions, 1):
        change = ((pred - current_price) / current_price) * 100
        print(f"  Ngày {i}: ${pred:.2f} ({change:+.2f}%)")
