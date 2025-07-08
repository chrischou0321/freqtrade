# AdaptiveCryptoStrategy - 適應性加密貨幣交易策略

## 🎯 策略概述

`AdaptiveCryptoStrategy` 是一個創新的適應性交易策略，能夠根據市場狀態自動切換交易邏輯，在不同市場環境下採用最適合的交易方法。

### 核心創新
- **實時市場狀態檢測**: 自動識別趨勢市 vs 震盪市
- **雙重策略切換**: 趨勢跟隨 + 均值回歸
- **ATR動態風險管理**: 根據波動率調整止損和倉位
- **多層風險控制**: 防止過度虧損

## 📊 策略邏輯

### 市場狀態檢測
策略通過以下三個維度判斷市場狀態：

1. **ATR擴張度** (`atr_expansion`): 當前ATR vs 平均ATR
2. **EMA分離度** (`ema_separation`): 快慢EMA的距離
3. **波動率比率** (`volatility_ratio`): 當前波動率 vs 平均波動率

**判斷標準**: 至少滿足2個條件判定為趨勢市，否則為震盪市

### 趨勢跟隨策略 (Trending Market)
**適用條件**: 市場狀態 = 趨勢市

**做多信號**:
- EMA快線 > EMA慢線
- 價格突破EMA快線
- RSI在30-75範圍
- 成交量放大 > 1.1倍
- MACD > Signal
- 正向動量

**做空信號**: 相反條件

### 均值回歸策略 (Consolidation Market)
**適用條件**: 市場狀態 = 震盪市

**做多信號**:
- RSI < 30 (超賣)
- 價格偏離EMA慢線 > 2%
- 接近布林下軌

**做空信號**:
- RSI > 70 (超買)
- 價格偏離EMA慢線 > 2%
- 接近布林上軌

## 🛡️ 風險管理

### 動態止損
- **基礎止損**: 3%
- **ATR動態止損**: 2倍ATR距離
- **追蹤止損**: 2%利潤後啟動，保持2.5%利潤

### 動態倉位管理
- **目標風險**: 每筆交易2%
- **ATR調整**: 根據2倍ATR風險距離計算倉位
- **槓桿控制**: 趨勢市1.5-2.5倍，震盪市1.5倍

### 動態止盈
- **ATR止盈**: 3倍ATR距離
- **狀態變化**: 市場狀態改變時考慮止盈

## ⚙️ 策略參數

### 核心參數
| 參數 | 範圍 | 默認值 | 說明 |
|------|------|--------|------|
| `lookback_period` | 15-25 | 20 | 市場狀態判斷週期 |
| `atr_period` | 12-16 | 14 | ATR計算週期 |
| `ema_fast_period` | 10-14 | 12 | 快速EMA週期 |
| `ema_slow_period` | 24-30 | 26 | 慢速EMA週期 |

### 市場狀態參數
| 參數 | 範圍 | 默認值 | 說明 |
|------|------|--------|------|
| `atr_expansion_threshold` | 1.15-1.3 | 1.2 | ATR擴張閾值 |
| `ema_separation_threshold` | 0.008-0.015 | 0.01 | EMA分離度閾值 |
| `volatility_threshold` | 1.05-1.2 | 1.1 | 波動率閾值 |

## 🚀 使用方法

### 1. 基本回測
```bash
freqtrade backtesting \
  --config user_data/config_futures_btc.json \
  --strategy AdaptiveCryptoStrategy \
  --timerange 20240601-20240701
```

### 2. 參數優化
```bash
freqtrade hyperopt \
  --config user_data/config_futures_btc.json \
  --strategy AdaptiveCryptoStrategy \
  --hyperopt-loss SharpeHyperOptLoss \
  --spaces buy sell \
  --epochs 100
```

### 3. 實盤交易
```bash
freqtrade trade \
  --config user_data/config_futures_btc.json \
  --strategy AdaptiveCryptoStrategy
```

## 📈 策略特點

### 優勢
1. **適應性強**: 自動識別市場狀態並切換策略
2. **風險控制**: 多層次動態風險管理
3. **參數優化**: 所有關鍵參數可優化
4. **全市場覆蓋**: 趨勢市和震盪市都有對應策略

### 適用場景
- **時間框架**: 15分鐘 (平衡效率與準確性)
- **市場類型**: 加密貨幣期貨/現貨
- **交易風格**: 中短期 (持倉幾小時到幾天)
- **風險偏好**: 中等風險

### 注意事項
1. **參數敏感性**: 需要根據不同交易對調整參數
2. **回測週期**: 建議至少3個月數據進行回測
3. **模擬測試**: 實盤前務必進行模擬測試
4. **監控重要性**: 需要監控市場狀態識別準確性

## 🔧 自定義配置

### 配置文件示例
```json
{
  "strategy": "AdaptiveCryptoStrategy",
  "strategy_path": "user_data/strategies/",
  "timeframe": "15m",
  "tradable_balance_ratio": 0.95,
  "fiat_display_currency": "USD",
  "stake_currency": "USDT",
  "stake_amount": "unlimited",
  "dry_run": true,
  "cancel_open_orders_on_exit": true
}
```

### 建議的風險設置
```json
{
  "max_open_trades": 3,
  "stake_amount": "unlimited",
  "tradable_balance_ratio": 0.95,
  "available_capital": 1000
}
```

## 📊 績效指標

### 關鍵指標
- **夏普比率**: 目標 > 1.5
- **最大回撤**: 目標 < 15%
- **勝率**: 目標 > 55%
- **盈虧比**: 目標 > 1.2

### 監控指標
- 市場狀態識別準確率
- 不同狀態下的策略表現
- ATR動態調整效果
- 風險控制效果

## 🛠️ 故障排除

### 常見問題
1. **無交易信號**: 參數過於嚴格，適當放寬條件
2. **頻繁交易**: 參數過於寬鬆，提高篩選標準
3. **大幅虧損**: 檢查風險管理參數設置

### 性能優化
1. 根據具體交易對調整參數
2. 定期重新優化參數
3. 監控實際vs預期表現

---

## 📝 版本歷史

- **v1.0**: 初始版本，包含基本適應性邏輯
- 創建日期: 2024-07-08
- 作者: Claude Code Assistant

---

**免責聲明**: 本策略僅供教育和研究目的，不構成投資建議。交易有風險，請謹慎操作。