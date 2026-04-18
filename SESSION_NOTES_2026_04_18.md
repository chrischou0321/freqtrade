# Session Notes 2026-04-18 — BTCWeeklySwing 完整回測

## 本次工作階段完成事項

### 任務：BTCWeeklySwing 新策略設計 + 完整回測

從 plan `snappy-doodling-feigenbaum.md` 啟動，完整執行 BTCWeeklySwing 策略的開發與回測。

---

## 版本演進記錄

| 版本 | 主時框 | 出場方式 | 關鍵改動 | 交易/月 | 勝率 | 總報酬 |
|------|-------|---------|---------|---------|------|--------|
| v7（原有）| 4h | ROI | 動量突破原型 | 0.6 | 56.9% | +3.32% |
| v8 | 1h | ROI | 改1h提高頻率 | 1.37 | 50.7% | -34.03% |
| v9 | 1h | 移動止損 | 移除ROI天花板 | 3.5 | 44.3% | -67.03% |
| v10 | 1h | ATR+移動 | ATR buffer過濾假突破 | 3.1 | 38.4% | -51.81% |
| v11 | 4h | 移動止損 | 回到4h，改移動止損 | 0.75 | 53.3% | -15.89% |
| **v11+HO** | **4h** | **移動止損** | **Hyperopt epoch79** | **0.65** | **59.4%** | **+7.93%** |

### 關鍵洞察
1. **BTC是動量市場**：均值回歸（v1-v6）必然失敗，勝率42%低於費用門檻
2. **ROI天花板殺死贏家**：截斷贏家到2%，輸家吃完整2.5%，RR=0.74導致負EV
3. **1h突破品質低**：60%在20小時內失敗，即使移動止損也無法救回
4. **4h突破品質佳**：53-59%勝率，這是真實的邊際（Edge）
5. **頻率問題是結構性的**：單一BTC + 4h主時框最多0.5-1次/月，這是物理限制

---

## 最終版本（v11, BTCWeeklySwing.py）

### 當前策略設定
```python
# 主時框：4h
# Informative：1d

# 出場（v11核心）
minimal_roi = {"0": 0.15}  # 極高天花板
stoploss = -0.03
trailing_stop = True
trailing_stop_positive = 0.02      # 達2%後啟動
trailing_stop_positive_offset = 0.03  # 從3%高點追蹤

# Hyperopt epoch 79 最優參數
breakout_bars = 11      # 4h bar（44小時突破）
vol_ratio = 1.7x        # 量能門檻
rsi_max = 75            # RSI上限（放寬）
rsi_min = 31            # RSI下限
adx_min = 20            # ADX趨勢強度
```

### Base版本回測結果（2017-2025, Binance BTC/USDT spot）
- 64筆交易 / 0.65次月
- 勝率：59.4% ✅
- 總報酬：+7.93%
- CAGR：0.93%/年
- MDD：14.85% ✅
- Calmar：0.34
- 最大連敗：3次 ✅
- Profit Factor：1.09

### B2熔斷版本（連敗3次→等EMA50恢復）
- 21筆交易 / +2.66% / MDD 12.89%
- **結論：Base優於B2**（熔斷擋掉了正期望值的交易）

---

## 驗收標準對照

| 指標 | 目標 | 實際 | 狀態 |
|------|------|------|------|
| 交易頻率 | 4-12次/月 | 0.65次/月 | ❌ |
| 總報酬 | >80% | +7.93% | ❌ |
| MDD | <25% | 14.85% | ✅ |
| Calmar | >3.0 | 0.34 | ❌ |
| Sharpe | >1.2 | ~0.01 | ❌ |
| 勝率 | 45%+ | 59.4% | ✅ |

---

## 等待用戶決策

**頻率問題**是結構性問題，不是參數問題。提出三條出路給用戶：

A. **接受低頻**：保留 BTCWeeklySwing 作為補充（0.5-1次/月）
B. **多標的**：加入 ETH/SOL/BNB，各1-2次/月 → 總4-8次/月
C. **策略轉型**：換 EMA pullback 或 Keltner Channel，天生頻率更高

---

## 技術問題記錄

### Hyperopt 依賴安裝
joblib 無法通過 venv pip 安裝，解決方式：
```bash
python3 -m pip install joblib scikit-learn hyperopt \
  --target /mnt/e/claude-workspace/projects/freqtrade/.venv/lib/python3.12/site-packages/
```

### Hyperopt 參數文件格式
freqtrade 不接受自定義 JSON 格式，需直接改 strategy 的 default 值。

---

## 重要檔案

| 檔案 | 說明 |
|------|------|
| `user_data/strategies/BTCWeeklySwing.py` | 最終版本（4h, v11, Base） |
| `user_data/config_btcweekly_backtest.json` | 回測 config |
| `user_data/data/binance/BTC_USDT-1h.feather` | 1h 數據（v8-v10用） |
| `user_data/data/binance/BTC_USDT-4h.feather` | 4h 數據 |
| `user_data/data/binance/BTC_USDT-1d.feather` | 1d 數據 |
| `plan/BTCWeeklySwing/BTCWeeklySwing_v1.0.md` | 策略計劃文件 |

---

*文件生成時間：2026-04-18*
