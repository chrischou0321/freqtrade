#!/usr/bin/env python3

"""
樣本外測試 - 驗證參數是否過度優化
"""

import json
import os
from datetime import datetime, timedelta

def analyze_optimization_results():
    """分析優化結果並提供樣本外測試建議"""
    
    print("📊 **樣本外測試分析**")
    print("=" * 60)
    
    # 讀取當前最佳參數
    try:
        with open("user_data/strategies/Conservative15mStrategy.json", "r") as f:
            params = json.load(f)
        
        print("🎯 **當前最佳參數組合:**")
        print("-" * 30)
        buy_params = params.get("params", {}).get("buy", {})
        for key, value in buy_params.items():
            print(f"  {key}: {value}")
        
        print(f"\n⏰ **參數優化時間:** {params.get('export_time', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ 無法讀取參數文件: {e}")
        return
    
    print("\n🔍 **過度優化風險分析:**")
    print("-" * 40)
    
    # 分析參數合理性
    risks = []
    
    # 檢查ADX閾值
    adx_threshold = buy_params.get("adx_threshold", 25)
    if adx_threshold > 30:
        risks.append(f"ADX閾值過高 ({adx_threshold}) - 可能過度限制交易")
    
    # 檢查EMA參數
    ema_fast = buy_params.get("ema_fast_period", 12)
    ema_slow = buy_params.get("ema_slow_period", 28)
    if ema_slow / ema_fast > 3:
        risks.append(f"EMA比例過大 ({ema_slow}/{ema_fast}) - 可能過度平滑")
    
    # 檢查RSI參數
    rsi_oversold = buy_params.get("rsi_oversold", 32)
    if rsi_oversold < 30:
        risks.append(f"RSI超賣閾值過低 ({rsi_oversold}) - 可能過度限制")
    
    # 檢查成交量因子
    volume_factor = buy_params.get("volume_factor", 1.3)
    if volume_factor > 1.5:
        risks.append(f"成交量因子過高 ({volume_factor}) - 可能過度限制")
    
    if risks:
        print("⚠️  **潛在過度優化風險:**")
        for risk in risks:
            print(f"  - {risk}")
    else:
        print("✅ 參數組合看起來合理")
    
    print("\n🧪 **樣本外測試建議:**")
    print("-" * 40)
    
    test_suggestions = [
        "1. **時間切分測試**",
        "   - 訓練期: 2024年1月-10月",
        "   - 測試期: 2024年11月-12月",
        "",
        "2. **不同市場條件測試**",
        "   - 牛市期間: 2024年1-3月",
        "   - 震盪期間: 2024年4-6月",
        "   - 調整期間: 2024年7-9月",
        "",
        "3. **不同幣種測試**",
        "   - ETH/USDT:USDT",
        "   - BNB/USDT:USDT",
        "   - SOL/USDT:USDT",
        "",
        "4. **參數穩定性測試**",
        "   - 將最佳參數±10%進行測試",
        "   - 檢查性能是否急劇下降",
        "",
        "5. **4H趨勢過濾效果測試**",
        "   - 對比有/無4H過濾的回測結果",
        "   - 重點關注勝率提升幅度",
    ]
    
    for suggestion in test_suggestions:
        print(suggestion)
    
    print("\n🎯 **關鍵性能指標監控:**")
    print("-" * 40)
    
    kpis = [
        "勝率 (Win Rate) - 目標 > 55%",
        "夏普比率 (Sharpe Ratio) - 目標 > 1.0",
        "最大回撤 (Max Drawdown) - 目標 < 15%",
        "盈虧比 (Profit/Loss Ratio) - 目標 > 1.2",
        "平均交易時長 - 目標 < 4小時",
        "月度勝率穩定性 - 標準差 < 15%",
    ]
    
    for kpi in kpis:
        print(f"  📈 {kpi}")
    
    print("\n⚡ **立即行動建議:**")
    print("-" * 40)
    print("1. 先用當前參數進行2024年11-12月回測")
    print("2. 如果性能下降超過20%，則存在過度優化")
    print("3. 重點驗證4H趨勢過濾是否真的提高勝率")
    print("4. 考慮放寬部分參數範圍，提高策略穩定性")

if __name__ == "__main__":
    analyze_optimization_results()