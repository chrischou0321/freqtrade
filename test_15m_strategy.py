#!/usr/bin/env python3
"""
15分鐘策略測試指南
"""

def show_testing_guide():
    print("🕐 15分鐘策略測試指南")
    print("=" * 40)
    
    print("✅ 已完成的更新:")
    print("1. ✅ ConservativeTrendStrategy: 3m → 15m")
    print("2. ✅ 新建 Conservative15mStrategy (專門優化)")
    print("3. ✅ 配置文件已更新")
    
    print("\n📥 第一步：下載15分鐘數據")
    print("freqtrade download-data \\")
    print("  --config user_data/config_futures_btc.json \\")
    print("  --exchange binance \\")
    print("  --pairs BTC/USDT:USDT \\")
    print("  --timeframes 15m \\")
    print("  --days 360")
    
    print("\n🧪 第二步：快速測試 (1個月)")
    print("freqtrade backtesting \\")
    print("  --config user_data/config_futures_btc.json \\")
    print("  --strategy Conservative15mStrategy \\")
    print("  --timerange 20240301-20240331")
    
    print("\n📊 第三步：中期測試 (3個月)")
    print("freqtrade backtesting \\")
    print("  --config user_data/config_futures_btc.json \\")
    print("  --strategy Conservative15mStrategy \\")
    print("  --timerange 20240101-20240331")
    
    print("\n📈 第四步：長期測試 (6個月)")
    print("freqtrade backtesting \\")
    print("  --config user_data/config_futures_btc.json \\")
    print("  --strategy Conservative15mStrategy \\")
    print("  --timerange 20240101-20240630")
    
    print("\n🎯 15分鐘策略期望指標:")
    print("📊 交易頻率:")
    print("  • 每日交易: 0.5-1.5 筆 (極大改善)")
    print("  • 3個月總交易: 50-150 筆")
    print("  • 手續費負擔: <50% (vs 之前674%)")
    
    print("\n💰 獲利目標:")
    print("  • 最小獲利: 2.5% (vs 0.8%)")
    print("  • 止損: 3% (vs 1.2%)")
    print("  • 風險回報比: 1.2:1 (合理)")
    
    print("\n📉 風險控制:")
    print("  • 最大回撤: <15% (vs 90%)")
    print("  • 勝率: >50% (vs 44%)")
    print("  • 夏普比率: >1.0")
    
    print("\n🔍 關鍵改進點:")
    print("✅ 大幅減少噪音交易")
    print("✅ 10個嚴格條件同時滿足才進場")
    print("✅ 多重趨勢和動量確認")
    print("✅ 波動率和成交量過濾")
    print("✅ 布林帶位置控制")
    print("✅ 多期間動量檢查")
    
    print("\n⚠️  注意事項:")
    print("• 15分鐘信號較少，這是正常的")
    print("• 每筆交易持倉時間更長")
    print("• 需要更大的耐心等待信號")
    print("• 品質勝過數量")
    
    print("\n📋 成功標準:")
    print("🎯 基本要求:")
    print("  • 總收益 > 0%")
    print("  • 最大回撤 < 25%")
    print("  • 每日交易 < 2 筆")
    
    print("\n🏆 理想目標:")
    print("  • 總收益 > 15%")
    print("  • 最大回撤 < 15%")
    print("  • 勝率 > 55%")
    print("  • 夏普比率 > 1.5")
    
    print("\n🚀 如果測試成功，下一步:")
    print("1. 參數優化 (hyperopt)")
    print("2. 不同市場環境測試")
    print("3. 風險管理優化")
    print("4. 實盤模擬測試")

if __name__ == "__main__":
    show_testing_guide()