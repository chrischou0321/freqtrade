"""
MultiBreakoutStrategy — 多對主流幣動量破位策略
================================================
交易對：13 對主流 USDT 永續（BTC/ETH/SOL/BNB/AVAX/XRP/LINK/ARB/OP/NEAR/INJ/TIA/SUI）
框架：15m 執行 + 1H setup 確認 + 4H 趨勢方向

進場邏輯（優先順序）：
  1. 4H close > EMA200（大趨勢方向確認，不逆勢）
  2. 1H MACD > signal AND > macd_min（動量方向確認）
  3. 15m close 突破近 N 根高點（rolling_high_bars）
  4. 15m volume > vol_ma20 × vol_spike_ratio（量能爆量過濾假突破）
  5. 1H RSI < rsi_upper（不追過熱）

雜訊過濾：
  - 15m 信號必須同時滿足 1H MACD（防逆勢小幅破位）
  - 不在近 100 根最高點下 0.5% 附近進場（大阻力壓制）

止損 / 獲利：
  - stoploss = -2%（15m 小框架，止損要緊）
  - ROI: 0H=2.5%, 2H=2.0%

Hyperopt 4 個參數（防過擬合）：
  - vol_spike_ratio / macd_min / rsi_upper / rolling_high_bars
"""

import pandas as pd
import talib.abstract as ta
from freqtrade.strategy import DecimalParameter, IntParameter, IStrategy
from pandas import DataFrame


class MultiBreakoutStrategy(IStrategy):
    INTERFACE_VERSION = 3

    # ── 時間框架 ────────────────────────────────────────────────────────────
    timeframe = "15m"

    # startup_candle_count：15m 主框架，rolling(100) 是最長窗口
    startup_candle_count: int = 200

    # ── 止損 / 獲利 ──────────────────────────────────────────────────────────
    stoploss = -0.02

    # 0分鐘=2.5%，120分鐘（2H）=2.0%；不設 24H 低目標避免 RR 劣化
    minimal_roi = {"0": 0.025, "120": 0.020}

    # ── 期貨 ────────────────────────────────────────────────────────────────
    can_short = False

    # ── Hyperopt 參數（4個，≤4 防過擬合）────────────────────────────────────
    vol_spike_ratio   = DecimalParameter(1.5, 3.0, default=1.8, decimals=1, space="buy", optimize=True)
    macd_min          = DecimalParameter(-0.0005, 0.001, default=0.0, decimals=4, space="buy", optimize=True)
    rsi_upper         = IntParameter(55, 75, default=65, space="buy", optimize=True)
    rolling_high_bars = IntParameter(10, 30, default=20, space="buy", optimize=True)

    # ── 指標計算 ─────────────────────────────────────────────────────────────

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # ── 15m 指標 ─────────────────────────────────────────────────────
        dataframe["vol_ma20"]   = dataframe["volume"].rolling(20).mean()
        # 大阻力：近 100 根最高點（排除當前根）
        dataframe["roll_hi_100"] = dataframe["high"].shift(1).rolling(100).max()

        # ── 1H informative ───────────────────────────────────────────────
        inf_1h = self.dp.get_pair_dataframe(metadata["pair"], "1h")
        if inf_1h is not None and not inf_1h.empty:
            inf_1h = inf_1h.copy()
            inf_1h["rsi_1h"]     = ta.RSI(inf_1h, timeperiod=14)
            macd_1h              = ta.MACD(inf_1h, fastperiod=12, slowperiod=26, signalperiod=9)
            inf_1h["macd_1h"]    = macd_1h["macd"]
            inf_1h["macd_sig_1h"] = macd_1h["macdsignal"]

            dataframe = pd.merge_asof(
                dataframe.sort_values("date"),
                inf_1h[["date", "rsi_1h", "macd_1h", "macd_sig_1h"]].sort_values("date"),
                on="date",
                direction="backward",
            )

        # ── 4H informative ───────────────────────────────────────────────
        inf_4h = self.dp.get_pair_dataframe(metadata["pair"], "4h")
        if inf_4h is not None and not inf_4h.empty:
            inf_4h = inf_4h.copy()
            inf_4h["ema200_4h"] = ta.EMA(inf_4h, timeperiod=200)

            dataframe = pd.merge_asof(
                dataframe.sort_values("date"),
                inf_4h[["date", "ema200_4h"]].sort_values("date"),
                on="date",
                direction="backward",
            )

        # informative 欄位不存在時補 NaN（避免 KeyError）
        for col in ["rsi_1h", "macd_1h", "macd_sig_1h", "ema200_4h"]:
            if col not in dataframe.columns:
                dataframe[col] = float("nan")

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 動態取 rolling high（依 hyperopt 參數）
        bars = self.rolling_high_bars.value
        roll_hi = dataframe["high"].shift(1).rolling(bars).max()

        # 1. 4H 趨勢方向
        cond_trend    = dataframe["close"] > dataframe["ema200_4h"]

        # 2. 1H MACD 動量確認
        cond_macd     = (
            (dataframe["macd_1h"] > dataframe["macd_sig_1h"]) &
            (dataframe["macd_1h"] > self.macd_min.value)
        )

        # 3. 1H RSI 不追過熱
        cond_rsi      = dataframe["rsi_1h"] < self.rsi_upper.value

        # 4. 15m 突破近 N 根高點
        cond_breakout = dataframe["close"] > roll_hi

        # 5. 15m 量能爆量（過濾假突破）
        cond_volume   = dataframe["volume"] > dataframe["vol_ma20"] * self.vol_spike_ratio.value

        # 6. 不在大阻力（100-bar high）下方 0.5% 追進
        cond_not_wall = (
            dataframe["roll_hi_100"].isna() |
            (dataframe["close"] < dataframe["roll_hi_100"] * 0.995) |
            (dataframe["close"] >= dataframe["roll_hi_100"])
        )

        dataframe.loc[
            cond_trend & cond_macd & cond_rsi & cond_breakout & cond_volume & cond_not_wall,
            "enter_long",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # ROI + stoploss 處理出場，不加額外訊號出場
        dataframe["exit_long"] = 0
        return dataframe

    def informative_pairs(self):
        """為每個交易對申報所需的 informative timeframes"""
        pairs = self.dp.current_whitelist()
        return [(pair, tf) for pair in pairs for tf in ("1h", "4h")]
