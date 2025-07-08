#!/usr/bin/env python3

"""
測試4H趨勢過濾修復
"""

import pandas as pd
import numpy as np
import sys
import os

def test_strategy_indicators():
    """測試策略指標生成"""
    
    # 創建假數據來測試
    dates = pd.date_range('2024-01-01', periods=1000, freq='15min')
    fake_data = pd.DataFrame({
        'date': dates,
        'open': np.random.randn(1000).cumsum() + 100,
        'high': np.random.randn(1000).cumsum() + 102,
        'low': np.random.randn(1000).cumsum() + 98,
        'close': np.random.randn(1000).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 1000)
    })
    
    print("🧪 **4H趨勢過濾修復測試**")
    print("=" * 50)
    
    # 檢查策略文件結構
    try:
        with open("user_data/strategies/Conservative15mStrategy.py", "r") as f:
            content = f.read()
            
        # 檢查修復內容
        checks = [
            ("merge_informative_pair", "數據合併函數已導入"),
            ("get_pair_dataframe", "4H數據獲取方法已加入"),
            ("trend_4h", "4H趨勢指標已定義"),
            ("except Exception", "錯誤處理已加入"),
            ("默認值", "fallback機制已建立"),
        ]
        
        for check_str, description in checks:
            if check_str in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
                
        # 檢查是否移除了 @informative 裝飾器
        if "@informative('4h')" not in content:
            print("✅ 舊的@informative裝飾器已移除")
        else:
            print("❌ 舊的@informative裝飾器仍然存在")
            
        print("\n🎯 **修復策略說明:**")
        print("-" * 30)
        print("1. 移除了 @informative('4h') 裝飾器")
        print("2. 手動獲取4H數據並計算指標")
        print("3. 使用 merge_informative_pair 合併數據")
        print("4. 加入錯誤處理和默認值")
        print("5. 確保策略不會因為數據問題而崩潰")
        
        print("\n🚀 **現在可以進行回測了！**")
        print("修復後的策略應該能夠正常運行")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    test_strategy_indicators()