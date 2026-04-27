# ShortMJ WFO 系列 — 工作階段交接文件
**日期：2026-03-24 | 討論串：Discord #1485458101044776990**

---

## 一、背景與脈絡

做空策略 `ShortMJ`（MACD+KDJ 複合空頭）在完整歷史 WFO（Fold 8-26）中只有 5/19 通過，
且通過折全集中在崩盤事件（FTX、2021-05崩、2024Q2回調）。
團隊共識：策略 edge 只在「波動急增的崩盤環境」有效，與單純熊市方向無關。

---

## 二、三版本 WFO 結果

| 版本 | 變更 | 總 PASS | 有效折 PASS（Trades≥10 或 30）| 問題 |
|------|------|---------|-------------------------------|------|
| **ShortMJ** | 原版，無 Regime | 5/19 | ~5/9 = 55% | 牛市段信號噪音多 |
| **ShortMJR** | 加 Regime（close<EMA100+slope+ADX>20） | 3/19 | 3/7 = 43% | Fold 14 零信號（錯過 FTX 崩） |
| **ShortMJRB** | Regime 改 close<EMA100×1.02 | 2/19 | 2/8 = 25% | Fold 21/23 引入假信號，退步 |
| **ShortMJRv2** | Regime 改 ATR>ATR_MA×1.5 | 0/19 | 0/0 = 0% | ⚠️ 日線 ATR 1.5x 太嚴，幾乎零信號 |

**根本診斷（團隊共識）：**
現有 Regime Filter 全部使用靜態/方向性指標，但 ShortMJ 的 edge 需要「波動急增條件」。
ShortMJRv2 方向正確但閾值設錯（日線 ATR 1.5x 只在黑天鵝才觸發）。

---

## 三、待解決的兩個問題

### 問題一：WFO 進度通知沒有自動發出
**現象：** 每次啟動 WFO 說「每 10 分鐘自動回報」，但通知從未發出。
**根本原因：** 需要同時啟動 `wfo_monitor.py` 背景進程，每次都漏掉這步。
**修法（下個 session 執行）：**
```bash
# 啟動 WFO 同時啟動 monitor
cd /mnt/e/claude-workspace/projects/freqtrade
nohup .venv/bin/python3 user_data/scripts/wfo_shortmjrv2b_full.py --epochs 100 > /tmp/wfo_v2b.log 2>&1 &
nohup .venv/bin/python3 user_data/scripts/wfo_monitor.py \
    --log /tmp/wfo_v2b.log \
    --label "ShortMJRv2b" \
    --total-folds 19 \
    --interval 10 > /tmp/monitor_v2b.log 2>&1 &
```
**待確認：** `wfo_monitor.py` 的 THREAD_ID 目前固定為 `1485152487387168848`（WFO 討論串），
而使用者在 `1485458101044776990`（本串）。需確認是否要改 THREAD_ID 或讓 Claude MCP 直接回報。

---

### 問題二：ShortMJRv2 ATR 閾值太嚴
**現象：** 19 折平均 0.3 筆/折，只有 Fold 14（FTX崩，4筆）有任何信號。
**根本原因：** 日線 ATR > 20日均值 × 1.5 = 只在極端黑天鵝時觸發（每年 < 5 天）。
**三個備選方案（等使用者確認選哪個）：**

**A — 降低 ATR 倍數（最快）**
```python
# 把 1.5x 改成 1.1x
atr_14 > atr_14.rolling(20).mean() * 1.1
```
預期每折信號量：20-60 筆

**B — 換成 4H ATR（信號更即時）**
用 4H 週期計算 ATR Regime，比日線反應更快
```python
# 在 4H informative frame 中：
inf4h["atr_regime"] = ta.ATR(inf4h, timeperiod=14)
inf4h["atr_regime_ma"] = inf4h["atr_regime"].rolling(20).mean()
regime_atr = atr_regime_4h > atr_regime_ma_4h * 1.3
```

**C — 回頭 ShortMJ + 換 loss function**
放棄 Regime Filter 路線，直接 ShortMJ 用 200 epochs + CalmarHyperOptLoss 重打

---

## 四、檔案位置

| 檔案 | 路徑 |
|------|------|
| 策略：ShortMJ | `user_data/strategies/ShortMJ.py` |
| 策略：ShortMJR | `user_data/strategies/ShortMJR.py` |
| 策略：ShortMJRB | `user_data/strategies/ShortMJRB.py` |
| 策略：ShortMJRv2 | `user_data/strategies/ShortMJRv2.py` |
| WFO 腳本 | `user_data/scripts/wfo_shortmjrv2_full.py` |
| WFO Monitor | `user_data/scripts/wfo_monitor.py` |
| 結果：ShortMJ | `user_data/wfo_results/smjf_wfo_summary.json` |
| 結果：ShortMJRB | `user_data/wfo_results/smjrb_wfo_summary.json` |
| 結果：ShortMJRv2 | `user_data/wfo_results/smjv2_wfo_summary.json` |
| Log（ShortMJRv2）| `/tmp/wfo_shortmjrv2_full.log` |

---

## 五、下一個 Session 開始時的 Checklist

- [ ] 確認使用者選擇方案 A / B / C
- [ ] 建立對應策略檔（ShortMJRv2b 或其他）
- [ ] 啟動 WFO **同時** 啟動 monitor（不能漏）
- [ ] 確認 monitor 的 THREAD_ID 要推到哪個串
- [ ] 如果選 A：修改 `ShortMJRv2.py` 的 `regime_atr_mult` 預設值 1.5 → 1.1，新建 ShortMJRv2b
