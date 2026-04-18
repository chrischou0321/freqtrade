# Session Notes 2026-04-18 (B) — B/C 雙軌驗證結果

## 工作目標
在 BTCWeeklySwing（A方案）基礎上，同步驗證：
- **B方案**：多對擴展（BTC+ETH+BNB+SOL）
- **C方案**：AltcoinPullbackSwing（EMA回調，新策略類型）

---

## 驗證結果彙整

### B方案：BTCWeeklySwing 多對擴展

| 組合 | 筆數 | 勝率 | 總報酬 | 頻率 |
|------|------|------|--------|------|
| BTC Only（基準） | 64 | 59.4% | +7.93% | 0.65/月 |
| BTC+BNB | 137 | 59.1% | +0.72% | ~1.2/月 |
| BTC+ETH+BNB+SOL | 137 | 59.1% | +0.72% | ~1.2/月 |

**根本問題**：BTC-優化的參數不能遷移到山寨幣。
- BTC：+4.45%（有真實Edge）
- BNB：-3.73%（BTC動量突破邏輯不適用BNB特性）
- ETH hyperopt（150 epochs）最佳結果：僅2筆 = 過度擬合

### C方案：AltcoinPullbackSwing（EMA回調進場）

| 測試 | 筆數 | 勝率 | 總報酬 | 頻率 |
|------|------|------|--------|------|
| BTC Only（預設值） | 4 | 50% | -1.76% | 0.04/月 |
| BTC Only（hyperopt值）| 4 | 50% | -1.76% | 0.04/月 |
| 4對多標的（hyperopt值）| 8 | 62.5% | -0.18% | 0.11/月 |

**根本問題**：三條件同時為真機率接近零
- RSI 30-46 + EMA20 ±1.5% + 量縮 < 1.1x 在 BTC 4h 幾乎不共現
- BTC 牛市回調的 RSI 通常在 40-55，不會低到 46 以下又接近 EMA20
- 不是參數問題，是條件邏輯設計的衝突

---

## 已使用的 Hyperopt 結果

### BTCWeeklySwing Epoch 79（正在使用的有效結果）
```
breakout_bars=11, vol_ratio=1.7, rsi_max=75, rsi_min=31, adx_min=20
IS (2019-2024): 57 trades, 59.6% win, +10.7%
Full (2017-2025): 64 trades, 59.4% win, +7.93%, MDD 14.85%
```

### BTCWeeklySwing ETH Hyperopt（已刪除，過度擬合）
```
adx_min=30, breakout_bars=8, rsi_max=62, rsi_min=33, vol_ratio=1.1
只有2筆交易，過度擬合，已刪除 BTCWeeklySwing.json
```

### AltcoinPullbackSwing Hyperopt（BTC，實用最佳）
```
adx_min=25, ema_touch_pct=0.015, rsi_pullback_max=46, rsi_pullback_min=30, vol_max_ratio=1.1
但這些參數在全期只產生4筆交易，無統計意義
```

---

## 核心結論

**4h時框的頻率物理上限**

| 策略類型 | 最大頻率（4對）| 代價 |
|---------|--------------|------|
| 動量突破（4h） | ~1.2次/月 | BTC以外的Edge不存在 |
| EMA回調（4h） | ~0.1次/月 | 條件衝突，幾乎不觸發 |
| 目標頻率 | 4-12次/月 | ❌ 當前方法無法達到 |

---

## 待用戶決策的方向（已發 Discord）

**A** — 接受2次/月上限，保留BTC+BNB組合
**B** — 換策略框架：2h/1h RSI過賣反彈（高頻但需重新驗證）
**C** — 放棄頻率目標，BTCWeeklySwing作為核心（0.65/月）

---

## 檔案狀態

| 檔案 | 狀態 |
|------|------|
| `user_data/strategies/BTCWeeklySwing.py` | ✅ 有效（epoch79參數） |
| `user_data/strategies/AltcoinPullbackSwing.py` | ⚠️ hyperopt值已更新但策略本身失效 |
| `user_data/strategies/BTCWeeklySwing.json` | ✅ 已刪除（過度擬合的ETH參數） |
| `user_data/config_btcweekly_backtest.json` | ✅ BTC單對 |
| `user_data/config_multipair_backtest.json` | ✅ 4對多標的 |

---

*記錄時間：2026-04-18*
