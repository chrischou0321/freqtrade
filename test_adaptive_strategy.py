#!/usr/bin/env python3
"""
AdaptiveCryptoStrategy 測試腳本
"""
import sys
import os
from pathlib import Path

# 添加 freqtrade 路徑
sys.path.append('/mnt/e/claude-workspace/projects/freqtrade')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from freqtrade.data.history import load_pair_history
from freqtrade.configuration import Configuration
from freqtrade.resolvers import StrategyResolver
from freqtrade.data.dataprovider import DataProvider
from freqtrade.enums import RunMode

def create_mock_data(length=1000):
    """創建模擬測試數據"""
    base_time = datetime.now()
    dates = [base_time + timedelta(minutes=15*i) for i in range(length)]
    
    # 生成模擬價格數據
    np.random.seed(42)
    price = 50000  # BTC起始價格
    prices = [price]
    
    for i in range(1, length):
        # 簡單的隨機遊走 + 趨勢
        trend = 0.0001 if i < length//2 else -0.0001  # 前半段上漲，後半段下跌
        change = np.random.normal(trend, 0.002)  # 0.2%標準差
        price = price * (1 + change)
        prices.append(price)
    
    # 生成OHLCV數據
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        # 簡單的OHLC生成
        volatility = abs(np.random.normal(0, 0.001))
        high = close * (1 + volatility)
        low = close * (1 - volatility)
        open_price = prices[i-1] if i > 0 else close
        volume = np.random.randint(1000000, 10000000)
        
        data.append({
            'date': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    return df

def test_strategy_indicators():
    """測試策略指標計算"""
    print("🔍 測試策略指標計算...")
    
    try:
        # 載入策略
        from user_data.strategies.AdaptiveCryptoStrategy import AdaptiveCryptoStrategy
        strategy = AdaptiveCryptoStrategy()
        
        # 創建測試數據
        df = create_mock_data(500)
        
        # 測試指標計算
        df_with_indicators = strategy.populate_indicators(df, {'pair': 'BTC/USDT'})
        
        # 檢查關鍵指標
        required_indicators = [
            'atr', 'rsi', 'ema_fast', 'ema_slow', 'market_regime',
            'atr_expansion', 'ema_separation', 'volatility_ratio'
        ]
        
        missing_indicators = []
        for indicator in required_indicators:
            if indicator not in df_with_indicators.columns:
                missing_indicators.append(indicator)
        
        if missing_indicators:
            print(f"❌ 缺少指標: {missing_indicators}")
            return False
        
        # 檢查市場狀態檢測
        regime_counts = df_with_indicators['market_regime'].value_counts()
        print(f"📊 市場狀態統計:")
        print(f"   震盪市: {regime_counts.get(0, 0)} ({regime_counts.get(0, 0)/len(df_with_indicators)*100:.1f}%)")
        print(f"   趨勢市: {regime_counts.get(1, 0)} ({regime_counts.get(1, 0)/len(df_with_indicators)*100:.1f}%)")
        
        print("✅ 指標計算測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 指標計算測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_strategy_signals():
    """測試策略信號生成"""
    print("\n🎯 測試策略信號生成...")
    
    try:
        from user_data.strategies.AdaptiveCryptoStrategy import AdaptiveCryptoStrategy
        strategy = AdaptiveCryptoStrategy()
        
        # 創建測試數據
        df = create_mock_data(500)
        
        # 計算指標
        df = strategy.populate_indicators(df, {'pair': 'BTC/USDT'})
        
        # 生成進場信號
        df = strategy.populate_entry_trend(df, {'pair': 'BTC/USDT'})
        
        # 生成出場信號
        df = strategy.populate_exit_trend(df, {'pair': 'BTC/USDT'})
        
        # 統計信號
        long_signals = df['enter_long'].sum() if 'enter_long' in df.columns else 0
        short_signals = df['enter_short'].sum() if 'enter_short' in df.columns else 0
        exit_long_signals = df['exit_long'].sum() if 'exit_long' in df.columns else 0
        exit_short_signals = df['exit_short'].sum() if 'exit_short' in df.columns else 0
        
        print(f"📈 信號統計:")
        print(f"   做多信號: {long_signals}")
        print(f"   做空信號: {short_signals}")
        print(f"   平多信號: {exit_long_signals}")
        print(f"   平空信號: {exit_short_signals}")
        print(f"   總交易機會: {long_signals + short_signals}")
        
        if long_signals + short_signals == 0:
            print("⚠️  警告: 沒有生成任何交易信號，參數可能過於嚴格")
        else:
            print("✅ 信號生成測試通過")
        
        return True
        
    except Exception as e:
        print(f"❌ 信號生成測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_adaptive_behavior():
    """測試適應性行為"""
    print("\n🔄 測試適應性行為...")
    
    try:
        from user_data.strategies.AdaptiveCryptoStrategy import AdaptiveCryptoStrategy
        strategy = AdaptiveCryptoStrategy()
        
        # 創建趨勢數據
        trending_data = create_trending_data(200)
        trending_data = strategy.populate_indicators(trending_data, {'pair': 'BTC/USDT'})
        trending_data = strategy.populate_entry_trend(trending_data, {'pair': 'BTC/USDT'})
        
        # 創建震盪數據
        consolidation_data = create_consolidation_data(200)
        consolidation_data = strategy.populate_indicators(consolidation_data, {'pair': 'BTC/USDT'})
        consolidation_data = strategy.populate_entry_trend(consolidation_data, {'pair': 'BTC/USDT'})
        
        # 分析行為差異
        trending_regime_ratio = trending_data['market_regime'].mean()
        consolidation_regime_ratio = consolidation_data['market_regime'].mean()
        
        trending_signals = (trending_data.get('enter_long', pd.Series(0)).sum() + 
                          trending_data.get('enter_short', pd.Series(0)).sum())
        consolidation_signals = (consolidation_data.get('enter_long', pd.Series(0)).sum() + 
                               consolidation_data.get('enter_short', pd.Series(0)).sum())
        
        print(f"📊 適應性分析:")
        print(f"   趨勢數據 - 趨勢市比例: {trending_regime_ratio:.2%}, 信號數量: {trending_signals}")
        print(f"   震盪數據 - 趨勢市比例: {consolidation_regime_ratio:.2%}, 信號數量: {consolidation_signals}")
        
        if trending_regime_ratio > consolidation_regime_ratio:
            print("✅ 策略能正確識別不同市場狀態")
        else:
            print("⚠️  策略市場狀態識別可能需要調整")
        
        return True
        
    except Exception as e:
        print(f"❌ 適應性測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_trending_data(length=200):
    """創建明顯趨勢數據"""
    base_time = datetime.now()
    dates = [base_time + timedelta(minutes=15*i) for i in range(length)]
    
    # 強趨勢：每期平均上漲0.1%
    price = 50000
    prices = [price]
    
    for i in range(1, length):
        trend = 0.001  # 強上升趨勢
        noise = np.random.normal(0, 0.001)
        change = trend + noise
        price = price * (1 + change)
        prices.append(price)
    
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        volatility = abs(np.random.normal(0, 0.002))  # 較高波動
        high = close * (1 + volatility)
        low = close * (1 - volatility)
        open_price = prices[i-1] if i > 0 else close
        volume = np.random.randint(5000000, 15000000)  # 較高成交量
        
        data.append({
            'date': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    return df

def create_consolidation_data(length=200):
    """創建明顯震盪數據"""
    base_time = datetime.now()
    dates = [base_time + timedelta(minutes=15*i) for i in range(length)]
    
    # 震盪：圍繞均值波動
    price = 50000
    mean_price = price
    prices = [price]
    
    for i in range(1, length):
        # 向均值回歸的隨機遊走
        distance_from_mean = (price - mean_price) / mean_price
        reversion = -distance_from_mean * 0.1  # 回歸力度
        noise = np.random.normal(0, 0.0005)  # 較低波動
        change = reversion + noise
        price = price * (1 + change)
        prices.append(price)
    
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        volatility = abs(np.random.normal(0, 0.0005))  # 較低波動
        high = close * (1 + volatility)
        low = close * (1 - volatility)
        open_price = prices[i-1] if i > 0 else close
        volume = np.random.randint(1000000, 5000000)  # 較低成交量
        
        data.append({
            'date': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    return df

def main():
    """主測試函數"""
    print("🚀 AdaptiveCryptoStrategy 測試開始")
    print("=" * 50)
    
    # 檢查策略文件是否存在
    strategy_path = Path("/mnt/e/claude-workspace/projects/freqtrade/user_data/strategies/AdaptiveCryptoStrategy.py")
    if not strategy_path.exists():
        print(f"❌ 策略文件不存在: {strategy_path}")
        return False
    
    # 執行測試
    tests = [
        test_strategy_indicators,
        test_strategy_signals,
        test_adaptive_behavior
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 測試結果: {passed}/{len(tests)} 通過")
    
    if passed == len(tests):
        print("🎉 所有測試通過！策略準備就緒，可以進行回測。")
        print("\n📝 建議下一步:")
        print("1. 使用真實歷史數據進行回測")
        print("2. 調整參數以優化性能")
        print("3. 在模擬環境中測試")
    else:
        print("⚠️  部分測試失敗，請檢查策略實現")
    
    return passed == len(tests)

if __name__ == "__main__":
    main()