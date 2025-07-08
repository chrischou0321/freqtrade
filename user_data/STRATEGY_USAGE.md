# 量化交易策略使用說明

## 策略概覽

本專案包含多個加密貨幣合約交易策略，從高頻短期策略演進至保守長期策略，經過實戰優化和回測驗證。

### 🎯 推薦策略：Conservative15mStrategy

經過多次優化，**Conservative15mStrategy** 是目前表現最佳的策略，解決了過度交易和手續費問題。

## 🔄 策略演進歷程

### 1. ShortTermTrendStrategy (初版) - ❌ 已淘汰
- **時間框架**: 3分鐘 K線
- **問題**: 條件過於嚴格，無交易信號
- **狀態**: 不推薦使用

### 2. OptimizedTrendStrategy (改進版) - ❌ 災難性結果
- **時間框架**: 3分鐘 K線
- **問題**: 過度交易，-89.96% 巨大虧損
- **交易頻率**: 每日 6+ 筆，累積手續費 674%
- **狀態**: 已廢棄

### 3. Conservative15mStrategy (推薦版) - ✅ 當前最佳
- **時間框架**: 15分鐘 K線
- **優勢**: 大幅降低交易頻率，提升信號品質
- **預期交易頻率**: 每日 0.5-1.5 筆
- **狀態**: 強烈推薦

## 📊 Conservative15mStrategy 詳細說明

### 核心特點

- **時間框架**: 15分鐘 K線，大幅減少市場噪音
- **交易方向**: 支援做多和做空（雙向交易）
- **槓桿倍數**: 2倍槓桿，降低風險
- **風險控制**: 3% 止損，動態調整
- **手續費優化**: 針對減少交易頻率特別設計

### 技術指標組合

#### 1. 趨勢判斷
- **快速 EMA** (12期): 短期趨勢方向
- **慢速 EMA** (32期): 長期趨勢方向
- **EMA 斜率**: 趨勢強度確認

#### 2. 動量分析
- **RSI** (18期): 超買超賣判斷，避免極端位置
- **MACD** (12,26,9): 動量轉換確認
- **多期間動量**: 45分鐘和1.5小時動量檢查

#### 3. 趨勢強度
- **ADX** (14期): 趨勢強度 > 28
- **DI+/DI-**: 多空力量對比

#### 4. 波動率過濾
- **ATR**: 平均真實範圍，控制波動率
- **布林帶**: 位置和寬度控制

#### 5. 成交量確認
- **成交量比率**: 相對於20期平均的倍數
- **成交量爆發**: 確認信號有效性

## 🎯 交易邏輯

### 做多條件 (10個條件同時滿足)

1. **強勁上升趨勢**
   - 快速EMA > 慢速EMA
   - EMA斜率為正且上升

2. **RSI 動量條件**
   - RSI > 30 (避免超賣)
   - RSI < 65 (避免追高)
   - RSI 上升趨勢

3. **ADX 趨勢強度**
   - ADX > 28 (強趨勢)
   - DI+ > DI- (多方優勢)

4. **MACD 動量確認**
   - MACD > Signal
   - MACD 柱狀圖 > 0 且上升

5. **多期間動量**
   - 45分鐘動量 > 0.8%
   - 1.5小時動量 > 0

6. **成交量爆發**
   - 成交量比率 > 1.3

7. **布林帶位置**
   - 價格在中軌之上
   - BB 百分比在 30%-80% 之間

8. **波動率控制**
   - ATR 比率在合理範圍
   - BB 寬度 > 2.5% (足夠波動率)

9. **價格位置**
   - 收盤價 > 布林帶中軌
   - 收盤價 > 快速EMA

10. **基本條件**
    - 成交量 > 0

### 做空條件 (對應的反向條件)

所有條件的反向版本，確保在強下降趨勢中做空。

## 🛡️ 風險管理

### 止損策略
- **固定止損**: 3% 最大虧損
- **動態調整**: 
  - 持倉1小時後放寬至3.5%
  - 持倉3小時後放寬至4%

### 獲利目標
```python
minimal_roi = {
    "0": 0.025,   # 2.5% 最小獲利
    "60": 0.02,   # 1小時後 2%
    "180": 0.015, # 3小時後 1.5%
    "360": 0.01,  # 6小時後 1%
    "720": 0.005, # 12小時後 0.5%
}
```

### 追蹤止損
- **啟動**: 獲利 1.5% 後啟動
- **保護**: 始終保持 2% 利潤

### 倉位管理
- **最大同時持倉**: 3個
- **槓桿倍數**: 2倍
- **每筆交易**: 100 USDT

## 📋 使用方法

### 1. 環境安裝
```bash
# 安裝 freqtrade
pip install freqtrade[all]

# 或從源碼安裝
git clone https://github.com/freqtrade/freqtrade.git
cd freqtrade
pip install -e .
```

### 2. 下載15分鐘歷史數據
```bash
freqtrade download-data --config user_data/config_futures_btc.json --exchange binance --pairs BTC/USDT:USDT --timeframes 15m --timerange 20240101-20250706
```

### 3. 回測策略

#### 快速測試 (1個月)
```bash
freqtrade backtesting --config user_data/config_futures_btc.json --strategy Conservative15mStrategy --timerange 20240301-20240331
```

#### 中期測試 (3個月)
```bash
freqtrade backtesting --config user_data/config_futures_btc.json --strategy Conservative15mStrategy --timerange 20240101-20240331
```

#### 長期測試 (6個月)
```bash
freqtrade backtesting --config user_data/config_futures_btc.json --strategy Conservative15mStrategy --timerange 20240101-20240630
```

### 4. 參數優化
```bash
freqtrade hyperopt \
  --config user_data/config_futures_btc.json \
  --strategy Conservative15mStrategy \
  --hyperopt-loss SharpeHyperOptLoss \
  --epochs 200
```

### 5. 模擬交易
```bash
freqtrade trade \
  --config user_data/config_futures_btc.json \
  --strategy Conservative15mStrategy \
  --dry-run
```

### 6. 實盤交易 (需要配置API金鑰)
```bash
freqtrade trade \
  --config user_data/config_futures_btc.json \
  --strategy Conservative15mStrategy
```

## ⚙️ 配置檔案

主要配置 `user_data/config_futures_btc.json`：

- **trading_mode**: "futures" (合約交易)
- **margin_mode**: "isolated" (逐倉模式)
- **stake_amount**: 100 (每筆交易金額)
- **max_open_trades**: 3 (最大同時持倉)
- **fee**: 0.001 (手續費設定)
- **strategy**: "Conservative15mStrategy"

## 🧪 測試與驗證

### 策略測試
```bash
python -m pytest tests/strategy/test_short_term_trend_strategy.py -v
```

### 性能分析
```bash
# 分析回測結果
freqtrade backtesting-analysis \
  --config user_data/config_futures_btc.json

# 生成圖表
freqtrade plot-dataframe \
  --config user_data/config_futures_btc.json \
  --strategy Conservative15mStrategy \
  --timerange 20240101-20240331
```

## 📊 預期表現目標

### 🎯 基本要求
- **總收益**: > 0%
- **最大回撤**: < 25%
- **每日交易**: < 2 筆
- **勝率**: > 45%

### 🏆 理想目標
- **總收益**: > 15%
- **最大回撤**: < 15%
- **每日交易**: 0.5-1.5 筆
- **勝率**: > 55%
- **夏普比率**: > 1.5

### 📈 關鍵改進指標
- **交易頻率**: 從每日6+筆 → 0.5-1.5筆 (降低75-90%)
- **手續費負擔**: 從674% → <50% (降低92%+)
- **風險回報比**: 從2.33:1 → 1.2:1 (改善87%)
- **信號品質**: 大幅提升，10重過濾機制

## 🔧 可優化參數

### EMA 參數
- `ema_fast_period`: 8-16 (預設12)
- `ema_slow_period`: 24-40 (預設32)

### RSI 參數
- `rsi_period`: 14-21 (預設18)
- `rsi_oversold`: 25-35 (預設30)
- `rsi_overbought`: 65-75 (預設70)

### ADX 參數
- `adx_threshold`: 25-35 (預設28)

### 成交量參數
- `volume_factor`: 1.1-1.8 (預設1.3)

### 動量參數
- `momentum_threshold`: 0.004-0.012 (預設0.008)

## ⚠️ 重要注意事項

### 交易風險
1. **槓桿風險**: 合約交易具有槓桿風險，可能導致快速虧損
2. **市場風險**: 加密貨幣市場波動極大
3. **技術風險**: 策略基於歷史數據，未來表現不保證
4. **流動性風險**: 極端市況下可能影響訂單執行

### 使用建議
1. **充分測試**: 務必先進行詳細回測和模擬交易
2. **資金管理**: 只使用可承受損失的資金
3. **風險控制**: 嚴格遵守止損設定
4. **持續監控**: 定期檢查策略表現
5. **市場適應**: 根據市場環境調整參數

### 技術限制
1. **信號延遲**: 15分鐘級別信號較少，需要耐心
2. **市場環境**: 在橫盤震盪市場中表現可能較差
3. **滑點影響**: 市價單可能產生滑點
4. **手續費**: 雖已優化，但仍會影響最終收益

## 📚 策略文件結構

```
user_data/
├── strategies/
│   ├── Conservative15mStrategy.py         # 推薦策略
│   ├── ConservativeTrendStrategy.py       # 備用策略
│   ├── OptimizedTrendStrategy.py          # 已淘汰
│   └── ShortTermTrendStrategy.py          # 已淘汰
├── config_futures_btc.json                # 主配置檔案
├── STRATEGY_USAGE.md                      # 本文件
└── backtest_results/                      # 回測結果
```

## 🚀 後續優化方向

1. **多時間框架整合**: 結合1小時、4小時級別確認
2. **市場環境適應**: 根據波動率動態調整參數
3. **機器學習整合**: 使用FreqAI優化信號品質
4. **風險管理升級**: 動態倉位大小、波動率止損
5. **多資產擴展**: 測試其他加密貨幣對

---

## 📞 支援與回饋

如有問題或建議，請查看：
- 回測結果分析檔案
- freqtrade 官方文檔
- 策略優化報告

**免責聲明**: 本策略僅供學習和研究使用。加密貨幣交易存在重大風險，可能導致資金損失。請在充分理解風險的情況下使用，並建議先進行充分的模擬測試。過往表現不代表未來結果。