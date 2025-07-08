#!/usr/bin/env python3
"""
分析回測結果
"""

import zipfile
import json
import os

def analyze_backtest_results():
    os.chdir('user_data/backtest_results')
    
    # 解壓縮並讀取結果
    with zipfile.ZipFile('backtest-result-2025-07-06_20-33-45.zip', 'r') as zip_file:
        # 讀取主要結果檔案
        with zip_file.open('backtest-result-2025-07-06_20-33-45.json') as f:
            data = json.load(f)
    
    print('📊 回測結果分析')
    print('=' * 40)
    
    # 檢查策略結果
    for strategy_name, results in data.items():
        if strategy_name == 'metadata':
            continue
            
        print(f'\n🎯 策略: {strategy_name}')
        print('-' * 30)
        
        # 基本統計
        trades = results.get('trades', [])
        
        print(f'交易總數: {len(trades)}')
        
        if len(trades) == 0:
            print('❌ 沒有進行任何交易!')
            print('\n🔍 可能原因:')
            print('1. 進場條件過於嚴格')
            print('2. 策略邏輯有問題')
            print('3. 數據範圍不匹配')
            print('4. 指標計算異常')
            
            # 檢查策略配置
            print('\n📋 策略詳情檢查:')
            print(f'   結果鍵值: {list(results.keys())}')
            
            # 檢查是否有其他統計信息
            for key, value in results.items():
                if key != 'trades':
                    print(f'   {key}: {type(value)} - {value if not isinstance(value, (list, dict)) else f"len={len(value) if hasattr(value, '__len__') else 'N/A"}"}')
        else:
            print(f'✅ 進行了 {len(trades)} 筆交易')
            
            # 詳細分析前幾筆交易
            print('\n📈 交易詳情:')
            for i, trade in enumerate(trades[:5]):  # 只顯示前5筆
                open_rate = trade.get('open_rate', 0)
                close_rate = trade.get('close_rate', 0)
                profit_abs = trade.get('profit_abs', 0)
                profit_pct = trade.get('profit_ratio', 0) * 100
                
                print(f'   交易 {i+1}: 進場${open_rate:.2f} -> 出場${close_rate:.2f}, 獲利: {profit_abs:.2f} USDT ({profit_pct:.2f}%)')
    
    # 檢查 metadata
    if 'metadata' in data:
        metadata = data['metadata']
        print(f'\n📋 回測設定:')
        print(f'   開始時間: {metadata.get("backtest_start", "N/A")}')
        print(f'   結束時間: {metadata.get("backtest_end", "N/A")}')
        print(f'   初始資金: {metadata.get("dry_run_wallet", "N/A")} USDT')
        print(f'   最大倉位: {metadata.get("max_open_trades", "N/A")}')
        print(f'   時間框架: {metadata.get("timeframe", "N/A")}')

if __name__ == "__main__":
    analyze_backtest_results()