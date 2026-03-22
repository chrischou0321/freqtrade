#!/usr/bin/env python3
"""
Walk-Forward Optimization — MultiBreakoutStrategy
===================================================
策略：MultiBreakoutStrategy（多對主流幣動量破位策略）
目標：最大化 Profit Factor，RR ≥ 1.2，每折 OOS 交易數 ≥ 25

交易對：13 對主流幣（BTC/ETH/SOL/BNB/AVAX/XRP/LINK/ARB/OP/NEAR/INJ/TIA/SUI）
框架：15m 執行 + 1H MACD + 4H EMA200

用法：
  cd /mnt/e/claude-workspace/projects/freqtrade
  .venv/bin/python3 user_data/scripts/wfo_multi_breakout.py [--epochs 100] [--folds 8]
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ── 設定 ────────────────────────────────────────────────────────────────────

FREQTRADE_BIN = ".venv/bin/python3"
FREQTRADE_CMD = [FREQTRADE_BIN, "-m", "freqtrade"]
CONFIG        = "user_data/config_bybit_mb.json"
STRATEGY      = "MultiBreakoutStrategy"
STRATEGY_PATH = "user_data/strategies/"

# Walk-Forward 參數
# 15m × 13 對 → 訊號更多，可縮短窗口
TRAIN_DAYS = 90    # 訓練窗口（天）≈ 8640 根 15m K 棒
OOS_DAYS   = 30    # OOS 驗證窗口（天）≈ 2880 根
STEP_DAYS  = 30    # 滑動步長（非重疊）

# 資料時間範圍
DATA_START = datetime(2023, 1, 1)
DATA_END   = datetime(2026, 1, 1)

# 輸出目錄
RESULTS_DIR  = Path("user_data/wfo_results")
HYPEROPT_DIR = Path("user_data/hyperopt_results")

# 績效目標（訊號更多，標準可拉高）
TARGET_PF    = 1.3   # Profit Factor > 1.3
MIN_TRADES   = 25    # OOS 至少 25 筆交易（13 對 × 2/月）
MAX_DRAWDOWN = 0.20  # OOS MDD < 20%

PAIRS = [
    "BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT", "BNB/USDT:USDT",
    "AVAX/USDT:USDT", "LINK/USDT:USDT", "ARB/USDT:USDT", "OP/USDT:USDT",
    "NEAR/USDT:USDT", "INJ/USDT:USDT", "TIA/USDT:USDT", "SUI/USDT:USDT",
    # XRP 移除：Bybit leverage tiers 資料缺失，無法回測
]


# ── 工具函數 ─────────────────────────────────────────────────────────────────

def date_str(dt: datetime) -> str:
    return dt.strftime("%Y%m%d")


def run_cmd(cmd: list, desc: str, timeout: int = 7200) -> tuple[int, str, str]:
    print(f"\n{'='*60}\n[{desc}]\nCMD: {' '.join(cmd)}\n{'='*60}")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(Path(__file__).parent.parent.parent),
    )
    if result.returncode != 0:
        print(f"[STDERR] {result.stderr[-2000:]}")
    return result.returncode, result.stdout, result.stderr


# ── Hyperopt ─────────────────────────────────────────────────────────────────

def run_hyperopt(train_start: datetime, train_end: datetime, epochs: int, fold_id: int) -> Path | None:
    timerange = f"{date_str(train_start)}-{date_str(train_end)}"
    cmd = FREQTRADE_CMD + [
        "hyperopt",
        "--config", CONFIG,
        "--strategy", STRATEGY,
        "--strategy-path", STRATEGY_PATH,
        "--hyperopt-loss", "ProfitDrawDownHyperOptLoss",
        "--timerange", timerange,
        "--epochs", str(epochs),
        "--spaces", "buy",
        "--no-color",
        "--job-workers", "-1",
    ]
    rc, stdout, stderr = run_cmd(cmd, f"HYPEROPT fold {fold_id} [{timerange}]", timeout=7200)
    if rc != 0:
        print(f"[ERROR] Hyperopt fold {fold_id} failed")
        return None

    hyperopt_files = sorted(
        HYPEROPT_DIR.glob("*.fthypt"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    strategy_files = [f for f in hyperopt_files if STRATEGY in f.name] or hyperopt_files
    return strategy_files[0] if strategy_files else None


def extract_best_params(hyperopt_file: Path, fold_id: int) -> dict | None:
    cmd = FREQTRADE_CMD + [
        "hyperopt-show",
        "--config", CONFIG,
        "--hyperopt-filename", hyperopt_file.name,
        "--best",
        "--print-json",
    ]
    rc, stdout, stderr = run_cmd(cmd, f"EXTRACT PARAMS fold {fold_id}")
    if rc != 0 or not stdout.strip():
        return None

    for line in stdout.strip().split("\n"):
        line = line.strip()
        if line.startswith("{"):
            try:
                raw = json.loads(line)
                all_params = raw.get("params", raw)
                return {"buy_params": dict(all_params), "raw": raw}
            except json.JSONDecodeError:
                pass
    return None


def write_strategy_params(params: dict, fold_id: int):
    strategy_json = Path(STRATEGY_PATH) / f"{STRATEGY}.json"
    all_params = params.get("buy_params", {})

    output = {
        "strategy_name": STRATEGY,
        "params": {
            "buy":  all_params,
            "sell": {},
            "protection": {},
            "stoploss": {},
        },
        "ft_stratparam_v": 1,
        "export_time": datetime.now().isoformat(),
        "_wfo_fold": fold_id,
    }
    strategy_json.write_text(json.dumps(output, indent=2))
    print(f"[INFO] Wrote fold {fold_id} params to {strategy_json}")


# ── Backtest ──────────────────────────────────────────────────────────────────

def run_backtest_oos(oos_start: datetime, oos_end: datetime, fold_id: int) -> dict | None:
    timerange = f"{date_str(oos_start)}-{date_str(oos_end)}"
    result_file = RESULTS_DIR / f"mb_fold_{fold_id}_oos.json"

    cmd = FREQTRADE_CMD + [
        "backtesting",
        "--config", CONFIG,
        "--strategy", STRATEGY,
        "--strategy-path", STRATEGY_PATH,
        "--timerange", timerange,
        "--export", "trades",
        "--export-filename", str(result_file),
        "--cache", "none",
    ]
    rc, stdout, stderr = run_cmd(cmd, f"BACKTEST OOS fold {fold_id} [{timerange}]", timeout=600)
    if rc != 0:
        return None
    return parse_backtest(stdout, fold_id)


def parse_backtest(stdout: str, fold_id: int) -> dict:
    result = {
        "fold_id":        fold_id,
        "profit_factor":  None,
        "sortino":        None,
        "win_rate":       None,
        "total_trades":   None,
        "max_drawdown":   None,
        "avg_profit_pct": None,
        "raw":            stdout[-3000:],
    }

    for line in stdout.split("\n"):
        line = line.strip()
        try:
            if "Profit factor" in line:
                val = line.split("│")[2].strip()
                result["profit_factor"] = float(val)
            elif "Sortino" in line and result["sortino"] is None:
                val = line.split("│")[2].strip()
                result["sortino"] = float(val)
            elif "Absolute Drawdown (Account)" in line:
                val = line.split("│")[2].strip().replace("%", "")
                result["max_drawdown"] = float(val) / 100
        except (IndexError, ValueError):
            pass

    in_summary = False
    for line in stdout.split("\n"):
        if "STRATEGY SUMMARY" in line:
            in_summary = True
        if in_summary and STRATEGY in line:
            parts = [p.strip() for p in line.split("│") if p.strip() and p.strip() != STRATEGY]
            try:
                result["total_trades"]   = int(parts[0])
                result["avg_profit_pct"] = float(parts[1].replace("%", ""))
            except (IndexError, ValueError):
                pass
            break

    return result


# ── 主流程 ────────────────────────────────────────────────────────────────────

def print_summary(fold_results: list[dict]):
    print("\n" + "="*70)
    print(f"WFO 結果摘要 — {STRATEGY}")
    print("="*70)
    print(f"{'折數':>4} {'PF':>6} {'Sortino':>8} {'Win%':>6} {'Trades':>7} {'MDD%':>6} {'Pass':>5}")
    print("-"*70)

    pass_count = 0
    for r in fold_results:
        pf    = r.get("profit_factor") or 0.0
        sor   = r.get("sortino") or 0.0
        wr    = r.get("win_rate") or 0.0
        tr    = r.get("total_trades") or 0
        mdd   = (r.get("max_drawdown") or 0.0) * 100
        passed = pf >= TARGET_PF and tr >= MIN_TRADES and (r.get("max_drawdown") or 1) <= MAX_DRAWDOWN
        if passed:
            pass_count += 1
        tag = "✅" if passed else "❌"
        print(f"  {r['fold_id']:>2}  {pf:>6.2f}  {sor:>8.2f}  {wr:>5.1f}%  {tr:>6}  {mdd:>5.1f}%  {tag}")

    print("-"*70)
    print(f"合格折數: {pass_count}/{len(fold_results)}")

    pf_values = [r.get("profit_factor") for r in fold_results if r.get("profit_factor")]
    if pf_values:
        print(f"Profit Factor: avg={sum(pf_values)/len(pf_values):.2f}  min={min(pf_values):.2f}  max={max(pf_values):.2f}")

    tr_values = [r.get("total_trades") for r in fold_results if r.get("total_trades")]
    if tr_values:
        print(f"Trades/fold:   avg={sum(tr_values)/len(tr_values):.1f}  min={min(tr_values)}  max={max(tr_values)}")

    summary_file = RESULTS_DIR / "mb_wfo_summary.json"
    with open(summary_file, "w") as f:
        json.dump({
            "strategy": STRATEGY,
            "run_time": datetime.now().isoformat(),
            "folds": fold_results,
            "pass_count": pass_count,
            "total_folds": len(fold_results),
        }, f, indent=2)
    print(f"\n結果已存: {summary_file}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs",     type=int, default=100)
    parser.add_argument("--folds",      type=int, default=10)
    parser.add_argument("--start-fold", type=int, default=1, help="從第幾折開始（中斷恢復用）")
    parser.add_argument("--baseline",   action="store_true", help="跳過 hyperopt，只用預設參數做 baseline 回測")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    folds = []
    oos_start = DATA_START + timedelta(days=TRAIN_DAYS)
    while oos_start + timedelta(days=OOS_DAYS) <= DATA_END and len(folds) < args.folds:
        train_start = oos_start - timedelta(days=TRAIN_DAYS)
        train_end   = oos_start
        oos_end     = oos_start + timedelta(days=OOS_DAYS)
        folds.append((train_start, train_end, oos_start, oos_end))
        oos_start = oos_end

    print(f"\nMultiBreakoutStrategy WFO")
    print(f"Folds: {len(folds)}  |  Train: {TRAIN_DAYS}d  |  OOS: {OOS_DAYS}d  |  Epochs/fold: {args.epochs}")
    print(f"Pairs: {len(PAIRS)} 對主流幣")
    print(f"Data: {DATA_START.date()} → {DATA_END.date()}")
    if args.baseline:
        print("[BASELINE MODE] 跳過 hyperopt，使用預設參數")

    fold_results = []

    for i, (ts, te, os_, oe) in enumerate(folds):
        fold_id = i + 1
        if fold_id < args.start_fold:
            print(f"\n[fold {fold_id}] 跳過（--start-fold={args.start_fold}）")
            continue

        print(f"\n{'#'*60}")
        print(f"# Fold {fold_id}/{len(folds)}")
        print(f"# Train: {ts.date()} → {te.date()}")
        print(f"# OOS  : {os_.date()} → {oe.date()}")
        print(f"{'#'*60}")

        if not args.baseline:
            # Step 1: Hyperopt
            hyperopt_file = run_hyperopt(ts, te, args.epochs, fold_id)

            # Step 2: 提取最佳參數
            if hyperopt_file:
                best_params = extract_best_params(hyperopt_file, fold_id)
                if best_params:
                    write_strategy_params(best_params, fold_id)
                    print(f"[fold {fold_id}] 最佳參數: {best_params.get('buy_params', {})}")

        # Step 3: OOS 回測
        oos_result = run_backtest_oos(os_, oe, fold_id)
        if oos_result:
            fold_results.append(oos_result)

            pf = oos_result.get("profit_factor") or 0.0
            tr = oos_result.get("total_trades") or 0
            status = "✅ PASS" if pf >= TARGET_PF and tr >= MIN_TRADES else "❌ FAIL"
            print(f"\n[fold {fold_id}] {status}  PF={pf:.2f}  Trades={tr}")
        else:
            print(f"[fold {fold_id}] ⚠️  OOS 回測失敗，跳過")
            fold_results.append({"fold_id": fold_id, "error": "backtest_failed"})

    if fold_results:
        print_summary([r for r in fold_results if "error" not in r])


if __name__ == "__main__":
    main()
