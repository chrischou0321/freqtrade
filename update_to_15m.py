#!/usr/bin/env python3
"""
更新到15分鐘時間框架的完整指南
"""

def show_update_steps():
    print("🔄 更新到15分鐘時間框架")
    print("=" * 40)
    
    print("\n✅ 已完成:")
    print("1. 策略時間框架已更新: 3m → 15m")
    
    print("\n📋 需要執行的步驟:")
    
    print("\n1. 下載15分鐘歷史數據:")
    print("freqtrade download-data \\")
    print("  --config user_data/config_futures_btc.json \\")
    print("  --exchange binance \\")
    print("  --pairs BTC/USDT:USDT \\")
    print("  --timeframes 15m \\")
    print("  --days 360")
    
    print("\n2. 運行回測 (短期測試):")
    print("freqtrade backtesting \\")
    print("  --config user_data/config_futures_btc.json \\")
    print("  --strategy ConservativeTrendStrategy \\")
    print("  --timerange 20240101-20240331")
    
    print("\n3. 運行回測 (長期測試):")
    print("freqtrade backtesting \\")
    print("  --config user_data/config_futures_btc.json \\")
    print("  --strategy ConservativeTrendStrategy \\")
    print("  --timerange 20240101-20241231")
    
    print("\n📊 15分鐘時間框架的優勢:")
    print("✅ 大幅減少市場噪音")
    print("✅ 降低交易頻率 (預期每日 0.5-1.5 筆)")
    print("✅ 減少手續費負擔")
    print("✅ 更穩定的趨勢信號")
    print("✅ 更適合趨勢跟蹤策略")
    
    print("\n📈 預期改進:")
    print("• 交易次數: 每日 6+ 筆 → 0.5-1.5 筆")
    print("• 手續費負擔: 大幅降低 80%+")
    print("• 信號品質: 顯著提升")
    print("• 風險控制: 更好的風險回報比")
    
    print("\n⚠️  注意事項:")
    print("• 15分鐘級別信號較少，需要耐心等待")
    print("• 單筆持倉時間可能更長")
    print("• 需要確保止損和獲利目標合理")
    
    print("\n🎯 測試目標:")
    print("• 總交易數 < 200 筆 (3個月)")
    print("• 每日平均交易 < 2 筆")
    print("• 勝率 > 50%")
    print("• 最大回撤 < 20%")
    print("• 總收益 > 0%")

if __name__ == "__main__":
    show_update_steps()