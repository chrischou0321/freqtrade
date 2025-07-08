#!/usr/bin/env python3
"""
分析為什麼策略沒有交易的簡化版本
"""

import json
from datetime import datetime

def analyze_strategy_conditions():
    """分析策略條件的問題"""
    
    print("🔍 分析策略沒有交易的原因")
    print("=" * 40)
    
    # 讀取數據
    try:
        with open('user_data/data/binance/futures/BTC_USDT_USDT-3m-futures.json', 'r') as f:
            data = json.load(f)
        
        print(f"✅ 數據量: {len(data):,} 根 K 線")
        
        # 分析一個月的數據 (2024年1月)
        jan_2024_start = 1704067200000  # 2024-01-01 00:00:00 UTC
        jan_2024_end = 1706745600000    # 2024-02-01 00:00:00 UTC
        
        jan_data = [candle for candle in data if jan_2024_start <= candle[0] <= jan_2024_end]
        print(f"📊 2024年1月數據: {len(jan_data)} 根 K 線")
        
        if len(jan_data) < 100:
            print("❌ 分析數據不足")
            return
        
        # 分析價格趨勢
        prices = [candle[4] for candle in jan_data]  # 收盤價
        volumes = [candle[5] for candle in jan_data]  # 成交量
        
        # 計算簡單移動平均 (模擬 EMA)
        def simple_moving_average(data, period):
            if len(data) < period:
                return []
            result = []
            for i in range(period-1, len(data)):
                avg = sum(data[i-period+1:i+1]) / period
                result.append(avg)
            return result
        
        # 計算快慢均線
        ema_fast = simple_moving_average(prices, 8)
        ema_slow = simple_moving_average(prices, 24)
        
        print(f"\n📈 價格分析:")
        print(f"   價格範圍: ${min(prices):,.0f} - ${max(prices):,.0f}")
        print(f"   平均成交量: {sum(volumes)/len(volumes):,.0f}")
        
        # 分析趨勢條件
        if len(ema_fast) > 0 and len(ema_slow) > 0:
            # 對齊數據長度
            min_len = min(len(ema_fast), len(ema_slow))
            ema_fast = ema_fast[-min_len:]
            ema_slow = ema_slow[-min_len:]
            
            # 計算趨勢向上的比例
            trend_up_count = sum(1 for i in range(len(ema_fast)) if ema_fast[i] > ema_slow[i])
            trend_up_pct = trend_up_count / len(ema_fast) * 100
            
            print(f"\n📊 趨勢分析:")
            print(f"   上升趨勢時間: {trend_up_pct:.1f}%")
            print(f"   下降趨勢時間: {100-trend_up_pct:.1f}%")
            
            # 查找 EMA 交叉點
            crossover_up = 0
            crossover_down = 0
            
            for i in range(1, len(ema_fast)):
                # 金叉：快線從下方穿越慢線
                if ema_fast[i] > ema_slow[i] and ema_fast[i-1] <= ema_slow[i-1]:
                    crossover_up += 1
                # 死叉：快線從上方穿越慢線  
                elif ema_fast[i] < ema_slow[i] and ema_fast[i-1] >= ema_slow[i-1]:
                    crossover_down += 1
            
            print(f"\n🔄 EMA 交叉信號:")
            print(f"   金叉 (買入信號): {crossover_up} 次")
            print(f"   死叉 (賣出信號): {crossover_down} 次")
            
            # 計算簡單 RSI
            def calculate_simple_rsi(prices, period=14):
                if len(prices) < period + 1:
                    return []
                
                gains = []
                losses = []
                
                for i in range(1, len(prices)):
                    change = prices[i] - prices[i-1]
                    if change > 0:
                        gains.append(change)
                        losses.append(0)
                    else:
                        gains.append(0)
                        losses.append(abs(change))
                
                rsi_values = []
                for i in range(period-1, len(gains)):
                    avg_gain = sum(gains[i-period+1:i+1]) / period
                    avg_loss = sum(losses[i-period+1:i+1]) / period
                    
                    if avg_loss == 0:
                        rsi = 100
                    else:
                        rs = avg_gain / avg_loss
                        rsi = 100 - (100 / (1 + rs))
                    
                    rsi_values.append(rsi)
                
                return rsi_values
            
            rsi_values = calculate_simple_rsi(prices)
            
            if rsi_values:
                rsi_min = min(rsi_values)
                rsi_max = max(rsi_values)
                rsi_avg = sum(rsi_values) / len(rsi_values)
                
                # RSI 條件分析
                oversold_count = sum(1 for rsi in rsi_values if rsi < 30)
                overbought_count = sum(1 for rsi in rsi_values if rsi > 70)
                
                print(f"\n📊 RSI 分析:")
                print(f"   RSI 範圍: {rsi_min:.1f} - {rsi_max:.1f}")
                print(f"   RSI 平均: {rsi_avg:.1f}")
                print(f"   超賣 (<30): {oversold_count} 次 ({oversold_count/len(rsi_values)*100:.1f}%)")
                print(f"   超買 (>70): {overbought_count} 次 ({overbought_count/len(rsi_values)*100:.1f}%)")
            
        # 問題診斷
        print(f"\n🔍 問題診斷:")
        
        if crossover_up == 0:
            print("❌ 沒有 EMA 金叉信號 - 可能原因:")
            print("   - EMA 參數設定過於接近")
            print("   - 市場橫盤整理，缺乏明顯趨勢")
        else:
            print(f"✅ 有 {crossover_up} 次 EMA 金叉信號")
            
        if 'rsi_values' in locals() and rsi_values:
            if oversold_count == 0:
                print("❌ 沒有 RSI 超賣信號")
            else:
                print(f"✅ 有 {oversold_count} 次 RSI 超賣信號")
        
        print(f"\n💡 解決建議:")
        print("1. 使用更簡單的策略:")
        print("   - 僅基於 EMA 交叉的 SimpleTestStrategy")
        print("   - 降低 ADX 要求或移除複雜條件")
        
        print("\n2. 調整參數:")
        print("   - 降低 RSI 閾值 (30 -> 35, 70 -> 65)")
        print("   - 降低 ADX 閾值 (25 -> 20)")
        print("   - 放寬成交量條件")
        
        print("\n3. 測試命令:")
        print("   freqtrade backtesting --config user_data/config_futures_btc.json --strategy SimpleTestStrategy --timerange 20240101-20240131")
        
    except Exception as e:
        print(f"❌ 分析出錯: {e}")

if __name__ == "__main__":
    analyze_strategy_conditions()