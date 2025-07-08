#!/usr/bin/env python3
"""
策略調試腳本 - 分析為什麼策略沒有產生交易信號
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime

def analyze_strategy_signals():
    """分析策略是否能產生交易信號"""
    
    print("🔍 策略信號分析")
    print("=" * 50)
    
    # 讀取數據
    try:
        with open('user_data/data/binance/futures/BTC_USDT_USDT-3m-futures.json', 'r') as f:
            raw_data = json.load(f)
        
        print(f"✅ 成功讀取 {len(raw_data):,} 根 K 線")
        
        # 轉換為 DataFrame
        df = pd.DataFrame(raw_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        # 選擇一個時間段進行分析 (2024年1月)
        start_date = '2024-01-01'
        end_date = '2024-01-31'
        df_sample = df[start_date:end_date].copy()
        
        print(f"📊 分析時間段: {start_date} 到 {end_date}")
        print(f"📈 樣本數據: {len(df_sample)} 根 K 線")
        
        if len(df_sample) < 100:
            print("❌ 樣本數據不足，無法分析")
            return
        
        # 計算指標
        print("\n🧮 計算技術指標...")
        
        # EMA
        df_sample['ema_fast'] = df_sample['close'].ewm(span=8).mean()
        df_sample['ema_slow'] = df_sample['close'].ewm(span=24).mean()
        
        # RSI
        def calculate_rsi(prices, period=14):
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        df_sample['rsi'] = calculate_rsi(df_sample['close'])
        
        # ADX (簡化版)
        df_sample['price_change'] = df_sample['close'].pct_change()
        df_sample['adx'] = abs(df_sample['price_change']).rolling(window=14).mean() * 100
        
        # 成交量平均
        df_sample['volume_mean'] = df_sample['volume'].rolling(window=10).mean()
        
        # 檢查指標計算結果
        print(f"   EMA Fast: {df_sample['ema_fast'].dropna().count()} 個有效值")
        print(f"   EMA Slow: {df_sample['ema_slow'].dropna().count()} 個有效值") 
        print(f"   RSI: {df_sample['rsi'].dropna().count()} 個有效值")
        print(f"   ADX: {df_sample['adx'].dropna().count()} 個有效值")
        
        # 分析條件
        print("\n📋 分析交易條件...")
        
        # 原始策略條件分析
        print("\n🎯 原始策略條件檢查:")
        
        # 做多條件
        trend_up = df_sample['ema_fast'] > df_sample['ema_slow']
        rsi_not_overbought = df_sample['rsi'] < 70
        rsi_above_oversold = df_sample['rsi'] > 30
        rsi_recovering = (df_sample['rsi'] > 30) & (df_sample['rsi'].shift(1) <= 30)
        adx_strong = df_sample['adx'] > 25
        positive_momentum = df_sample['price_change'] > 0
        volume_above_avg = df_sample['volume'] > df_sample['volume_mean']
        
        print(f"   趨勢向上 (EMA快>慢): {trend_up.sum():,} / {len(df_sample):,} ({trend_up.mean()*100:.1f}%)")
        print(f"   RSI 未超買 (<70): {rsi_not_overbought.sum():,} / {len(df_sample):,} ({rsi_not_overbought.mean()*100:.1f}%)")
        print(f"   RSI 超賣反彈條件: {rsi_recovering.sum():,} / {len(df_sample):,} ({rsi_recovering.mean()*100:.1f}%)")
        print(f"   ADX 趨勢強度 (>25): {adx_strong.sum():,} / {len(df_sample):,} ({adx_strong.mean()*100:.1f}%)")
        print(f"   正向動量: {positive_momentum.sum():,} / {len(df_sample):,} ({positive_momentum.mean()*100:.1f}%)")
        print(f"   成交量高於平均: {volume_above_avg.sum():,} / {len(df_sample):,} ({volume_above_avg.mean()*100:.1f}%)")
        
        # 組合條件 (原始策略 - 過於嚴格)
        original_long_condition = (trend_up & rsi_recovering & adx_strong & positive_momentum & volume_above_avg)
        print(f"\n❗ 原始做多條件同時滿足: {original_long_condition.sum():,} 次 ({original_long_condition.mean()*100:.2f}%)")
        
        # 簡化條件分析
        print("\n🔧 簡化策略條件檢查:")
        
        # 更寬鬆的做多條件
        simple_long_condition = (trend_up & rsi_not_overbought & volume_above_avg)
        print(f"   簡化做多條件: {simple_long_condition.sum():,} 次 ({simple_long_condition.mean()*100:.1f}%)")
        
        # EMA 交叉信號 (最簡單)
        ema_cross_up = (df_sample['ema_fast'] > df_sample['ema_slow']) & (df_sample['ema_fast'].shift(1) <= df_sample['ema_slow'].shift(1))
        ema_cross_down = (df_sample['ema_fast'] < df_sample['ema_slow']) & (df_sample['ema_fast'].shift(1) >= df_sample['ema_slow'].shift(1))
        
        print(f"   EMA 金叉信號: {ema_cross_up.sum():,} 次")
        print(f"   EMA 死叉信號: {ema_cross_down.sum():,} 次")
        
        # 數據統計
        print(f"\n📊 數據統計:")
        print(f"   價格範圍: ${df_sample['close'].min():,.0f} - ${df_sample['close'].max():,.0f}")
        print(f"   RSI 範圍: {df_sample['rsi'].min():.1f} - {df_sample['rsi'].max():.1f}")
        print(f"   ADX 平均: {df_sample['adx'].mean():.1f}")
        print(f"   成交量平均: {df_sample['volume'].mean():,.1f}")
        
        # 建議
        print(f"\n💡 建議:")
        if original_long_condition.sum() == 0:
            print("   ❌ 原始策略條件過於嚴格，建議：")
            print("   1. 放寬 RSI 條件，不要求精確的超賣反彈")
            print("   2. 降低 ADX 閾值 (25 -> 20)")
            print("   3. 使用更簡單的趨勢判斷")
        
        if ema_cross_up.sum() > 0:
            print(f"   ✅ EMA 交叉策略可行，有 {ema_cross_up.sum()} 次金叉信號")
            print("   建議先使用簡單的 EMA 交叉策略測試")
        
    except Exception as e:
        print(f"❌ 分析過程出錯: {e}")

def test_simple_strategy():
    """測試簡單策略的可行性"""
    
    print("\n🚀 簡單策略測試")
    print("=" * 30)
    
    strategies = [
        ("SimpleTestStrategy", "超簡單 EMA 交叉"),
        ("ShortTermTrendStrategy_v2", "改進版趨勢策略")
    ]
    
    for strategy_name, description in strategies:
        try:
            with open(f'user_data/strategies/{strategy_name}.py', 'r') as f:
                content = f.read()
            print(f"✅ {description} 檔案存在")
        except FileNotFoundError:
            print(f"❌ {description} 檔案不存在")

if __name__ == "__main__":
    analyze_strategy_signals()
    test_simple_strategy()
    
    print("\n🎯 下一步建議:")
    print("1. 使用 SimpleTestStrategy 進行回測:")
    print("   freqtrade backtesting --config user_data/config_futures_btc.json --strategy SimpleTestStrategy --timerange 20240101-20240131")
    print("\n2. 如果簡單策略有交易，再試用 ShortTermTrendStrategy_v2:")
    print("   freqtrade backtesting --config user_data/config_futures_btc.json --strategy ShortTermTrendStrategy_v2 --timerange 20240101-20240131")