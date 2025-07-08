#!/usr/bin/env python3
"""
簡單分析回測結果
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
            print('\n🔍 策略數據檢查:')
            
            # 檢查策略返回的所有數據
            for key, value in results.items():
                if key == 'trades':
                    continue
                    
                value_type = type(value)
                if isinstance(value, (list, dict)):
                    value_info = f'len={len(value)}'
                else:
                    value_info = str(value)[:50]  # 限制長度
                    
                print(f'   {key}: {value_type.__name__} - {value_info}')
                
        else:
            print(f'✅ 進行了 {len(trades)} 筆交易')
            
            # 簡單統計
            profits = [trade.get('profit_abs', 0) for trade in trades]
            total_profit = sum(profits)
            winning_trades = len([p for p in profits if p > 0])
            
            print(f'   總獲利: {total_profit:.2f} USDT')
            print(f'   獲利交易: {winning_trades}/{len(trades)} ({winning_trades/len(trades)*100:.1f}%)')
    
    # 檢查 metadata
    if 'metadata' in data:
        metadata = data['metadata']
        print(f'\n📋 回測設定:')
        print(f'   時間範圍: {metadata.get("backtest_start", "N/A")} - {metadata.get("backtest_end", "N/A")}')
        print(f'   初始資金: {metadata.get("dry_run_wallet", "N/A")} USDT')

if __name__ == "__main__":
    analyze_backtest_results()