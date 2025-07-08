# CLAUDE.md

本檔案為 Claude Code (claude.ai/code) 在此代碼庫中工作時提供指導。

# 項目指示
這是從 https://github.com/freqtrade/freqtrade fork 出來的repo
如果會動到非user_data的檔案請提前警告我並詳細說明原因，這理應不是我的程度可以處理的東西
沒有額外說明的話，預設同步目標branch都在 feat/chriscc下進行

## 關於 Freqtrade

Freqtrade 是一個使用 Python 編寫的免費開源加密貨幣交易機器人。它支援所有主要交易所，可通過 Telegram 或 WebUI 控制，並包括回測、繪圖、資金管理工具，以及通過機器學習 (FreqAI) 進行策略優化。

## 開發指令

### 環境設定
```bash
# 自動開發環境設定
./setup.sh

# 手動設定
pip install -r requirements-dev.txt
pip install -e .[all]
pre-commit install
```

### 程式碼品質檢查
```bash
ruff check .              # 程式碼檢查(Linting)
ruff format .             # 程式碼格式化  
mypy freqtrade           # 型別檢查
pytest                   # 執行所有測試
pytest tests/test_<file>.py              # 執行特定測試檔案
pytest tests/test_<file>.py::test_<method>  # 執行特定測試方法
pre-commit run -a        # 執行所有預提交勾子
```

### 交易機器人操作
```bash
# 開始交易
freqtrade trade --config config.json

# 回測 (使用歷史資料測試策略效果，不會實際交易)
freqtrade backtesting --config config.json --strategy SampleStrategy

# 超參數優化 (自動尋找最佳策略參數組合)
freqtrade hyperopt --config config.json --hyperopt-loss SharpeHyperOptLoss --strategy SampleStrategy

# 下載市場資料
freqtrade download-data --config config.json --exchange binance --pairs BTC/USDT ETH/USDT
```

## 架構概覽

### 核心入口點
- `freqtrade/main.py` - 主要機器人入口，含命令列參數解析
- `freqtrade/worker.py` - 主要交易工作器，協調機器人操作
- `freqtrade/freqtradebot.py` - 核心機器人邏輯和交易迴圈

### 主要模組結構
- **`commands/`** - CLI 命令實作 (交易、回測、超參數優化等)
- **`configuration/`** - 使用 JSON 架構的配置管理和驗證
- **`data/`** - 資料處理、轉換和回測分析
- **`exchange/`** - 交易所特定實作，整合 ccxt 函式庫
- **`freqai/`** - 機器學習模型和 AI 驅動的策略優化
- **`optimize/`** - 回測引擎和超參數優化
- **`persistence/`** - 使用 SQLAlchemy 的資料庫模型 (交易、配對、訂單)
- **`plugins/`** - 可擴展的配對清單和保護插件系統
- **`rpc/`** - 遠程程序調用實作 (Telegram、REST API、WebSocket)
- **`strategy/`** - 策略介面和輔助函數
- **`templates/`** - 用於策略和配置生成的 Jinja2 模板

### 交易所架構
- 使用 ccxt 函式庫進行交易所抽象化
- 交易所特定實作位於 `exchange/` 目錄
- 支援現貨交易 (直接買賣幣種) 和期貨交易 (槓桿交易，期貨功能為實驗性)
- 處理每個交易所的速率限制、重試和錯誤處理

### 策略系統
- 所有策略都繼承自 `IStrategy` 基礎類別
- 必要方法: `populate_indicators()` (計算技術指標), `populate_entry_trend()` (定義買入條件), `populate_exit_trend()` (定義賣出條件)
- 進階功能的選用方法: `custom_stoploss()` (自訂停損邏輯), `custom_exit()` (自訂出場邏輯), `confirm_trade_entry()` (交易前的最終確認)
- 策略參數可透過超參數優化 (hyperopt) 進行優化

### 資料管道
- 支援多種資料格式: JSON, Feather, Parquet
- 時間框架轉換和重新取樣
- 資料驗證和清理
- 回測資料分析，提供豐富的統計輸出

### FreqAI 整合
- 使用 scikit-learn, catboost, lightgbm, xgboost, pytorch 的機器學習策略優化
- 特徵工程管道
- 模型訓練和預測整合
- 支援強化學習的進階策略

## 開發標準

### 程式碼品質
- 最大行長度: 100 字元
- 所有公開方法需要型別提示
- 所有公開方法需要文件字串 (reST 格式)
- 合併前所有測試都必須通過

### 分支結構
- `develop` - 主要開發分支 (PR 的目標)
- `stable` - 最新穩定版本
- `feat/*` - 功能分支

### 測試
- 所有新功能需要單元測試
- 交易所相容性的整合測試
- 使用多個測試策略進行策略測試
- 線上測試需要 API 金鑰 (選用)

## 配置

### 使用者目錄結構
```
user_data/
├── backtest_results/     # 回測結果和分析
├── data/                # 歷史市場資料
├── freqaimodels/        # 已訓練的 FreqAI 模型
├── hyperopts/           # 超參數優化結果
├── logs/                # 機器人日誌
├── notebooks/           # 用於分析的 Jupyter notebook
└── strategies/          # 自訂策略
```

### 配置檔案
- `config_examples/` 包含交易所特定的配置模板
- 配置使用 JSON 格式，具有廣泛驗證
- 支援模擬模式 (dry-run) 以測試策略而不實際交易

## Docker 開發

### 建置
```bash
docker build -t freqtrade .
docker-compose up -d
```

### 重要環境變數
- `FREQTRADE_STRATEGY` - 要使用的策略 (預設: SampleStrategy)
- `FREQTRADE_CONFIG` - 配置檔案路徑
- 網頁介面暴露在 8080 連接埠

## 重要技術決策

### 非同步/同步架構
- 主機器人迴圈為同步以確保可靠性
- WebSocket 連線和 API 伺服器使用 async/await
- 交易所操作使用同步 ccxt 以保持一致性

### 錯誤處理
- 完整的例外階層
- 優雅處理交易所錯誤和網路問題
- 詳細的結構化輸出日誌

### 效能優化
- 昂貴操作的週期性快取
- 超參數優化的多進程支援
- 大型資料集的高效資料結構

### 插件系統
- 動態配對選擇的可擴展配對清單插件
- 風險管理的保護插件
- 自訂實作的清潔介面

## FreqAI 特定註記

### 模型類型
- 回歸模型：預測未來價格走勢
- 分類模型：判斷買入或賣出信號
- 強化學習：讓AI自動學習最佳交易策略

### 資料管道
- 使用技術指標進行特徵工程
- 資料正規化和縮放
- 具有適當時間基礎驗證的訓練/測試分割

### 模型管理
- 模型版本控制和儲存
- 基於效能的自動重新訓練
- 與回測整合以進行策略驗證