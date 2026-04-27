# BTCWeeklySwing — 策略設計與回測計劃 v1.0

> 建立日期：2026-04-18
> 狀態：執行中

---

## Background

與 BTCIndexTracker v11（長週期週期騎手）並行，建立獨立的短週期波段策略，各自追蹤績效。

**問題**：BTCIndexTracker v11 使用 1d 時框 + EMA 21/55/120，設計為週期騎手，年交易2-6次，完全不符合每週1-3次交易的需求。

**方案**：C 方案 — 多策略並行，長短週期各自獨立。

---

## 策略設計

### 基本資訊

| 項目 | 設定 |
|------|------|
| 策略名稱 | `BTCWeeklySwing` |
| Primary Timeframe | 4h |
| Informative | 1d |
| 方向 | Long-only（BTC多頭環境） |
| 槓桿 | 1x（Phase 1現貨；Phase 2視勝率決定） |
| 交易對 | BTC/USDT（Binance現貨） |

### 進場邏輯（三層過濾）

**Layer 1 — 大方向（1d）**
- 收盤 > 1d EMA50（比EMA200寬鬆，捕捉趨勢初段）

**Layer 2 — 市場環境（4h）**
- 4h EMA20 > EMA50（中期趨勢向上）
- OR 4h EMA20 剛上穿 EMA50（趨勢初確認）

**Layer 3 — 進場時機（4h回調）**
- RSI 回調到 40-58 區間（回調但未超賣）
- 接近任一 S/R 位（EMA50 / Fib61.8% / VP支撐）
- MACD 柱體轉正（動能確認）
- 當根收陽（確認反彈）
- 量能 > 20期均量 × 1.1（溫和量能確認）

### 出場邏輯

**ROI（台階式）**
```python
minimal_roi = {
    "0":  0.04,   # 立即 4%
    "8":  0.03,   # 8h 後 3%
    "16": 0.02,   # 16h 後 2%
    "32": 0.01,   # 32h 後 1%
}
```

**止損**：-2.5%（硬止損）

**信號出場**：
- RSI > 73 且收陰（短線超買離場）
- 4h 收盤跌破 EMA50（趨勢失守）

### Hyperopt 參數（5個）

| 參數 | 範圍 | 說明 |
|------|------|------|
| `rsi_buy_min` | 35–50 | 回調RSI下限 |
| `rsi_buy_max` | 55–65 | 回調RSI上限 |
| `macd_min` | 0–0.001 | MACD柱體最小值 |
| `vol_ratio` | 1.0–1.8 | 量能確認倍數 |
| `sr_touch_pct` | 0.008–0.02 | S/R容忍帶寬度 |

---

## 熔斷機制（四版本並列測試）

| 版本 | 熔斷條件 | 重啟條件 |
|------|---------|---------|
| **Base** | 無熔斷 | — |
| **A** | 月MDD > 8% 暫停 | 下月自動重啟 |
| **B** | 連敗 3 次暫停 | 1個月後重啟 |
| **B2** ⭐ | 連敗 3 次暫停 | 1d EMA50 重新站回才重啟 |

> ⭐ B2 為推薦版本（歷史熊市通常 > 1 個月，EMA50條件更合理）

---

## 執行計劃

### Phase 1 — 現貨回測（主要驗證）

- **交易所**：Binance BTC/USDT spot
- **時間範圍**：2017-09 – 2025-12（含 2017 ICO泡沫、2018 熊市）
- **槓桿**：1x

```bash
# 數據下載
freqtrade download-data --exchange binance --pairs BTC/USDT \
  --timeframes 4h 1d --timerange 20170901-20251231

# 回測（四版本各跑一次）
freqtrade backtesting \
  --config user_data/config_btcweekly_backtest.json \
  --strategy BTCWeeklySwing \
  --timerange 20170901-20251231
```

### Phase 2 — 期貨版本（條件觸發）

- **前提**：Phase 1 勝率穩定 > 50%
- **交易所**：Binance BTC/USDT perp
- **時間範圍**：2019-09 – 2025-12
- **槓桿**：2x
- **若勝率未突破50% → 不執行 Phase 2**

---

## 驗收標準

| 指標 | 目標 | 備註 |
|------|------|------|
| 交易頻率 | 4–12 次/月 | 即每週1-3次 |
| 總報酬 | > 80% | 2017-2025全期 |
| MDD | < 25% | |
| Calmar Ratio | > 3.0 | |
| Sharpe Ratio | > 1.2 | |
| **勝率** | **45%+** | **用戶高度關注，月度分佈需穩定** |
| 盈虧比 | > 1.8 | |
| Profit Factor | > 1.4 | |

---

## 回測報告必含項目

1. 各版本績效對比表（Base / A / B / B2）
2. **最大連敗次數 + 發生時間區間**（即使不用連敗熔斷也要列出）
3. 熔斷觸發次數 + 重啟時機分析
4. 月度勝率分佈（按市況分段）：
   - 2017 牛市 / 2018 熊市 / 2019-2020 過渡 / 2021 牛市 / 2022 熊市 / 2023-2025
5. 與 BTCIndexTracker v11 相關性分析（進場時機重疊度）

---

## 槓桿使用原則

> 勝率未穩定突破 50% → **不使用槓桿**

Kelly Criterion 推導：
- 勝率 45%、RR 1.8 → 最優 Kelly = 45% - 55%/1.8 ≈ 14% → 槓桿約 1.1x
- 強制 2x 槓桿 = 負 Kelly 區域，長期必然侵蝕資本

Phase 2 期貨（2x 槓桿）**僅在 Phase 1 勝率達標後才執行**。

---

## 關鍵檔案

| 檔案 | 說明 | 狀態 |
|------|------|------|
| `user_data/strategies/BTCWeeklySwing.py` | 主策略 | 待建立 |
| `user_data/config_btcweekly_backtest.json` | 回測 config | 待建立 |
| `user_data/strategies/SRCryptoStrategy.py` | 參考：S/R計算 | 已存在 |
| `user_data/strategies/RegimeAwareCryptoStrategy.py` | 參考：制度判斷 | 已存在 |
| `user_data/config_btctracker_paper.json` | 參考：config格式 | 已存在 |

---

## 版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| v1.0 | 2026-04-18 | 初版，完整設計確認 |
