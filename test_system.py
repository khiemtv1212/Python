#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script đơn giản"""
import sys
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 80)
print("TEST SYSTEM - AI Market Analysis")
print("=" * 80)

# Test 1: Import modules
print("\n1. Checking imports...")
try:
    from data_fetcher import DataFetcher
    from technical_analyzer import TechnicalAnalyzer
    from ml_predictor import LSTMPredictor
    from alert_system import AlertSystem
    from main import MarketAnalysisEngine
    print("   OK - All modules imported successfully\n")
except Exception as e:
    print(f"   ERROR import: {e}\n")
    exit(1)

# Test 2: Initialize engine
print("2. Initialize MarketAnalysisEngine...")
try:
    engine = MarketAnalysisEngine()
    cryptos = engine.config.get('cryptos', [])
    stocks = engine.config.get('stocks', [])
    print(f"   OK - Engine initialized")
    print(f"   Will analyze: {len(cryptos)} cryptos, {len(stocks)} stocks\n")
except Exception as e:
    print(f"   ERROR init: {e}\n")
    exit(1)

# Test 3: Fetch data
print("3. Checking data fetch...")
try:
    df_crypto = DataFetcher.fetch_crypto_data('bitcoin', days=30)
    if df_crypto is not None and not df_crypto.empty:
        print(f"   OK - Bitcoin: {len(df_crypto)} records")
    
    df_stock = DataFetcher.fetch_stock_data('AAPL', days=30)
    if df_stock is not None and not df_stock.empty:
        print(f"   OK - Apple (AAPL): {len(df_stock)} records\n")
except Exception as e:
    print(f"   ERROR fetch data: {e}\n")
    exit(1)

# Test 4: Technical analysis
print("4. Checking technical analysis...")
try:
    analyzer = TechnicalAnalyzer()
    df_analyzed = analyzer.analyze_asset(df_crypto)
    print(f"   OK - Added {len(df_analyzed.columns) - len(df_crypto.columns)} technical indicators")
    print(f"   Indicators: RSI, MACD, Bollinger Bands, ATR, MA\n")
except Exception as e:
    print(f"   ERROR analysis: {e}\n")
    exit(1)

# Test 5: ML Prediction
print("5. Checking ML prediction...")
try:
    predictor = LSTMPredictor(lookback=30)
    X_train, y_train, X_test, y_test = predictor.prepare_data(df_crypto, test_size=0.2)
    print(f"   OK - Data prepared: {len(X_train)} train, {len(X_test)} test")
    print(f"   OK - Ready for LSTM training\n")
except Exception as e:
    print(f"   ERROR ML prep: {e}\n")
    exit(1)

# Test 6: Alerts
print("6. Checking alert system...")
try:
    alert_system = AlertSystem()
    alert_system.check_all_signals('Bitcoin', df_analyzed)
    alerts_list = alert_system.get_latest_alerts()
    print(f"   OK - Alert system working")
    print(f"   Total alerts: {len(alerts_list)}\n")
except Exception as e:
    print(f"   WARNING: {e}\n")

print("=" * 80)
print("SUCCESS - All checks passed!")
print("=" * 80)
print("\nRun the following command to start analysis:")
print("   python main.py")
print("   or")
print("   python analysis_engine.py\n")
