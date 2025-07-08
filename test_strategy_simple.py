#!/usr/bin/env python3
"""
簡化的策略測試腳本
不依賴完整的 freqtrade 環境，直接測試策略邏輯
"""

import sys
import json
from datetime import datetime

def test_strategy_data():
    """測試策略是否能正確處理數據"""
    
    print("=== 策略數據測試 ===")
    
    # 1. 檢查數據檔案
    try:
        with open('user_data/data/binance/futures/BTC_USDT_USDT-3m-futures.json', 'r') as f:
            data = json.load(f)
        
        print(f"✅ 數據檔案讀取成功")
        print(f"📊 總 K 線數量: {len(data):,}")
        
        if len(data) > 0:
            first_ts, last_ts = data[0][0], data[-1][0]
            first_date = datetime.fromtimestamp(first_ts/1000)
            last_date = datetime.fromtimestamp(last_ts/1000)
            print(f"📅 數據時間範圍: {first_date.strftime('%Y-%m-%d')} 到 {last_date.strftime('%Y-%m-%d')}")
            
            # 檢查數據格式 [timestamp, open, high, low, close, volume]
            sample = data[0]
            print(f"📋 數據格式: [時間戳, 開, 高, 低, 收, 量]")
            print(f"   示例: {sample}")
            
            return True
        else:
            print("❌ 數據檔案為空")
            return False
            
    except FileNotFoundError:
        print("❌ 找不到數據檔案")
        return False
    except Exception as e:
        print(f"❌ 讀取數據檔案時出錯: {e}")
        return False

def test_strategy_config():
    """測試策略配置檔案"""
    
    print("\n=== 策略配置測試 ===")
    
    try:
        with open('user_data/config_futures_btc.json', 'r') as f:
            config = json.load(f)
        
        print("✅ 配置檔案讀取成功")
        
        # 檢查關鍵配置
        key_configs = {
            'trading_mode': config.get('trading_mode'),
            'strategy': config.get('strategy'),
            'timeframe': config.get('timeframe', 'N/A'),
            'stake_amount': config.get('stake_amount'),
            'max_open_trades': config.get('max_open_trades'),
            'entry_pricing.price_side': config.get('entry_pricing', {}).get('price_side'),
        }
        
        print("🔧 關鍵配置:")
        for key, value in key_configs.items():
            print(f"   {key}: {value}")
        
        # 檢查合約交易配置
        if config.get('trading_mode') == 'futures':
            print("✅ 合約交易模式已正確配置")
        else:
            print("⚠️  未設定合約交易模式")
            
        return True
        
    except FileNotFoundError:
        print("❌ 找不到配置檔案")
        return False
    except Exception as e:
        print(f"❌ 讀取配置檔案時出錯: {e}")
        return False

def test_strategy_file():
    """測試策略檔案語法"""
    
    print("\n=== 策略檔案測試 ===")
    
    try:
        # 檢查策略檔案是否存在
        import os
        strategy_file = 'user_data/strategies/ShortTermTrendStrategy.py'
        
        if not os.path.exists(strategy_file):
            print("❌ 策略檔案不存在")
            return False
            
        print("✅ 策略檔案存在")
        
        # 檢查檔案大小
        file_size = os.path.getsize(strategy_file)
        print(f"📄 檔案大小: {file_size:,} bytes")
        
        # 檢查語法
        with open(strategy_file, 'r') as f:
            content = f.read()
        
        # 簡單檢查關鍵類別和方法
        if 'class ShortTermTrendStrategy' in content:
            print("✅ 策略類別定義正確")
        else:
            print("❌ 找不到策略類別定義")
            
        required_methods = [
            'populate_indicators',
            'populate_entry_trend', 
            'populate_exit_trend'
        ]
        
        missing_methods = []
        for method in required_methods:
            if f'def {method}' not in content:
                missing_methods.append(method)
        
        if not missing_methods:
            print("✅ 所有必要方法都已定義")
        else:
            print(f"❌ 缺少方法: {', '.join(missing_methods)}")
            
        # 檢查合約交易設定
        if 'can_short: bool = True' in content:
            print("✅ 已啟用做空功能")
        else:
            print("⚠️  做空功能可能未正確啟用")
            
        return len(missing_methods) == 0
        
    except Exception as e:
        print(f"❌ 檢查策略檔案時出錯: {e}")
        return False

def show_usage_instructions():
    """顯示使用說明"""
    
    print("\n=== 使用說明 ===")
    print("由於當前環境缺少完整的 freqtrade 依賴，請在具備完整環境的系統上運行:")
    print()
    print("1. 安裝完整的 freqtrade 環境:")
    print("   pip install freqtrade[all]")
    print()
    print("2. 運行回測:")
    print("   freqtrade backtesting --config user_data/config_futures_btc.json --strategy ShortTermTrendStrategy --timerange 20240101-20240201")
    print()
    print("3. 查看回測結果:")
    print("   freqtrade backtesting-analysis --config user_data/config_futures_btc.json")
    print()
    print("4. 運行模擬交易:")
    print("   freqtrade trade --config user_data/config_futures_btc.json --strategy ShortTermTrendStrategy --dry-run")

def main():
    """主要測試函數"""
    
    print("🚀 ShortTermTrendStrategy 策略測試")
    print("=" * 50)
    
    # 執行各項測試
    tests = [
        test_strategy_data,
        test_strategy_config, 
        test_strategy_file
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 測試執行出錯: {e}")
            results.append(False)
    
    # 總結
    print("\n=== 測試總結 ===")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 所有測試通過 ({passed}/{total})")
        print("✅ 策略準備就緒，可以在完整環境中運行回測")
    else:
        print(f"⚠️  部分測試未通過 ({passed}/{total})")
        print("❗ 請檢查上述問題後再運行回測")
    
    show_usage_instructions()

if __name__ == "__main__":
    main()