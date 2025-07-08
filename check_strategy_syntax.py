#!/usr/bin/env python3
"""
檢查策略語法的簡單腳本
"""
import ast
import sys

def check_strategy_syntax(file_path):
    """檢查策略文件語法"""
    print(f"🔍 檢查策略語法: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 語法檢查
        ast.parse(content)
        print("✅ 語法檢查通過")
        
        # 檢查關鍵類和方法
        tree = ast.parse(content)
        
        class_found = False
        required_methods = ['populate_indicators', 'populate_entry_trend', 'populate_exit_trend']
        found_methods = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if 'Strategy' in node.name:
                    class_found = True
                    print(f"✅ 找到策略類: {node.name}")
            
            if isinstance(node, ast.FunctionDef):
                if node.name in required_methods:
                    found_methods.append(node.name)
        
        if class_found:
            print("✅ 策略類結構正確")
        else:
            print("❌ 未找到策略類")
            return False
        
        missing_methods = set(required_methods) - set(found_methods)
        if missing_methods:
            print(f"❌ 缺少必要方法: {missing_methods}")
            return False
        else:
            print("✅ 所有必要方法都存在")
        
        print("✅ 策略結構檢查通過")
        return True
        
    except SyntaxError as e:
        print(f"❌ 語法錯誤: {e}")
        return False
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        return False

def check_imports(file_path):
    """檢查導入語句"""
    print("\n📦 檢查導入語句...")
    
    required_imports = [
        'numpy', 'pandas', 'freqtrade.strategy', 'talib'
    ]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        found_imports = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                for imp in required_imports:
                    if imp in line:
                        found_imports.append(imp)
        
        found_imports = list(set(found_imports))
        missing_imports = set(required_imports) - set(found_imports)
        
        if missing_imports:
            print(f"⚠️  可能缺少導入: {missing_imports}")
        else:
            print("✅ 所有必要的導入都存在")
        
        return len(missing_imports) == 0
        
    except Exception as e:
        print(f"❌ 導入檢查失敗: {e}")
        return False

def main():
    """主函數"""
    strategy_file = "user_data/strategies/AdaptiveCryptoStrategy.py"
    
    print("🚀 AdaptiveCryptoStrategy 語法檢查")
    print("=" * 50)
    
    # 檢查文件是否存在
    try:
        with open(strategy_file, 'r') as f:
            pass
    except FileNotFoundError:
        print(f"❌ 策略文件不存在: {strategy_file}")
        return False
    
    # 執行檢查
    syntax_ok = check_strategy_syntax(strategy_file)
    imports_ok = check_imports(strategy_file)
    
    print("\n" + "=" * 50)
    if syntax_ok and imports_ok:
        print("🎉 策略語法檢查全部通過！")
        print("\n📝 下一步建議:")
        print("1. 下載市場數據進行回測")
        print("2. 調整策略參數")
        print("3. 分析回測結果")
        
        # 輸出freqtrade命令示例
        print("\n🔧 Freqtrade 回測命令示例:")
        print("freqtrade backtesting --config user_data/config_futures_btc.json --strategy AdaptiveCryptoStrategy --timerange 20240601-20240701")
        
        return True
    else:
        print("❌ 策略檢查發現問題，請修正後重新檢查")
        return False

if __name__ == "__main__":
    main()