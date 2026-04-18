"""
AltcoinPullbackSwing — 4H EMA回調進場策略（C方案）
===================================================

策略C設計目標：
  比 BTCWeeklySwing 更高的天生頻率（2-4次/月/標的）
  進場邏輯從「突破」改為「回調後確認」

核心思路：
  BTC突破策略：等創新高 → 頻率低（0.5-1次/月）
  EMA回調策略：趨勢途中每次回調到均線都是機會 → 頻率高（2-4次/月）

進場邏輯（三層過濾）：
  Layer 1：1d EMA50 多頭（大方向）
  Layer 2：4h EMA20 > EMA50（中期趨勢向上）
  Layer 3：4h 回調確認
    - RSI 回調到 35-55 區間（回調但未跌破趨勢）
    - 4h 收盤回到 EMA20 ±ATR 範圍內（觸碰均線）
    - 當根陽線收盤 > EMA8（微結構恢復）
    - 量能 < 1.5x 均量（回調量縮，恐慌盤，不是崩潰）

出場邏輯：
  - 移動止損：達2%後啟動，保護1.5%獲利
  - 初始止損：-2.5%（回調策略需要稍多空間）
  - ROI 天花板：10%（基本不觸發）
  - 信號出場：4h EMA死叉 或 1d 趨勢轉空

設計標的：BTC + ETH + SOL + BNB（4對 × 2-4次/月 = 8-16次/月總計）
"""

from datetime import datetime
from typing import Optional

import talib.abstract as ta
from freqtrade.strategy import (
    DecimalParameter,
    IStrategy,
    IntParameter,
    informative,
)
from pandas import DataFrame


class AltcoinPullbackSwing(IStrategy):
    """4H EMA回調進場策略 — 趨勢途中每次均線支撐都是機會"""

    INTERFACE_VERSION = 3
    timeframe = "4h"
    startup_candle_count = 200

    can_short = False

    # ── 出場：移動止損為主 ────────────────────────────────────────────────────
    minimal_roi = {
        "0": 0.10,   # 10% 天花板，幾乎不觸發
    }

    stoploss = -0.025             # -2.5% 初始止損（比突破策略稍寬）
    trailing_stop = True
    trailing_stop_positive = 0.015         # 達1.5%後啟動移動止損
    trailing_stop_positive_offset = 0.025  # 從2.5%高點追蹤
    trailing_only_offset_is_reached = True

    use_custom_stoploss = False
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    process_only_new_candles = True

    # ── Hyperopt 參數 ─────────────────────────────────────────────────────────
    rsi_pullback_max = IntParameter(45, 62, default=46, space="buy", optimize=True)    # 回調RSI上限（HO: 46）
    rsi_pullback_min = IntParameter(28, 48, default=30, space="buy", optimize=True)    # 回調RSI下限（HO: 30）
    ema_touch_pct    = DecimalParameter(0.005, 0.03, default=0.015, decimals=3, space="buy", optimize=True)  # EMA20觸碰容忍帶（HO: 0.015）
    vol_max_ratio    = DecimalParameter(0.8, 2.0, default=1.1, decimals=1, space="buy", optimize=True)  # 量能上限（HO: 1.1，嚴格量縮）
    adx_min          = IntParameter(15, 35, default=25, space="buy", optimize=True)    # ADX趨勢強度（HO: 25）

    # ─────────────────────────────────────────────────────────────────────────
    # 1D 大方向（informative）
    # ─────────────────────────────────────────────────────────────────────────

    @informative("1d")
    def populate_indicators_1d(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_50"] = ta.EMA(dataframe["close"], timeperiod=50)
        dataframe["trend_up"] = (
            dataframe["close"] > dataframe["ema_50"]
        ).astype(int)
        return dataframe

    # ─────────────────────────────────────────────────────────────────────────
    # 4H 主要指標
    # ─────────────────────────────────────────────────────────────────────────

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 趨勢均線
        dataframe["ema_8"]     = ta.EMA(dataframe["close"], timeperiod=8)
        dataframe["ema_20"]    = ta.EMA(dataframe["close"], timeperiod=20)
        dataframe["ema_50"]    = ta.EMA(dataframe["close"], timeperiod=50)
        dataframe["adx"]       = ta.ADX(dataframe, timeperiod=14)
        dataframe["rsi"]       = ta.RSI(dataframe["close"], timeperiod=14)
        dataframe["vol_ema20"] = ta.EMA(dataframe["volume"], timeperiod=20)
        dataframe["atr"]       = ta.ATR(dataframe, timeperiod=14)

        # 趨勢狀態
        dataframe["trend_up"] = (dataframe["ema_20"] > dataframe["ema_50"]).astype(int)

        # EMA死叉（出場用）
        dataframe["death_cross"] = (
            (dataframe["ema_20"] < dataframe["ema_50"]) &
            (dataframe["ema_20"].shift(1) >= dataframe["ema_50"].shift(1))
        ).astype(int)

        # EMA20觸碰判斷：收盤在EMA20附近（± ema_touch_pct 範圍）
        # 先用固定值計算，hyperopt優化時用self.ema_touch_pct.value
        dataframe["near_ema20"] = (
            (dataframe["close"] >= dataframe["ema_20"] * (1 - 0.015)) &
            (dataframe["close"] <= dataframe["ema_20"] * (1 + 0.015))
        ).astype(int)

        # 微結構恢復：EMA8向上
        dataframe["micro_recovery"] = (
            dataframe["ema_8"] > dataframe["ema_8"].shift(1)
        ).astype(int)

        # 陽線確認
        dataframe["bullish_candle"] = (
            dataframe["close"] > dataframe["open"]
        ).astype(int)

        return dataframe

    # ─────────────────────────────────────────────────────────────────────────
    # 進場條件（EMA回調）
    # ─────────────────────────────────────────────────────────────────────────

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        EMA回調進場：
          Layer 1 — 1d EMA50 上方（大方向多頭）
          Layer 2 — 4h EMA20 > EMA50（中期趨勢向上）
          Layer 3 — 回調到EMA20後確認恢復
        """
        # Layer 1：大方向
        cond_1d = dataframe["trend_up_1d"] == 1

        # Layer 2：4h 中期趨勢
        cond_4h_trend = dataframe["trend_up"] == 1

        # Layer 3A：RSI 回調確認（不是崩盤，是正常回調）
        cond_rsi = (
            (dataframe["rsi"] >= self.rsi_pullback_min.value) &
            (dataframe["rsi"] <= self.rsi_pullback_max.value)
        )

        # Layer 3B：觸碰 EMA20（近均線）
        touch_band = self.ema_touch_pct.value
        cond_ema_touch = (
            (dataframe["close"] >= dataframe["ema_20"] * (1 - touch_band)) &
            (dataframe["close"] <= dataframe["ema_20"] * (1 + touch_band))
        )

        # Layer 3C：微結構恢復（EMA8向上 + 陽線）
        cond_recovery = (
            (dataframe["micro_recovery"] == 1) &
            (dataframe["bullish_candle"] == 1) &
            (dataframe["close"] > dataframe["ema_8"])
        )

        # Layer 3D：量縮（回調期量縮，非崩潰）
        cond_vol = dataframe["volume"] < dataframe["vol_ema20"] * self.vol_max_ratio.value

        # Layer 3E：ADX 趨勢強度（確保趨勢有力）
        cond_adx = dataframe["adx"] >= self.adx_min.value

        entry_signal = (
            cond_1d &
            cond_4h_trend &
            cond_rsi &
            cond_ema_touch &
            cond_recovery &
            cond_vol &
            cond_adx
        )

        dataframe.loc[
            entry_signal,
            ["enter_long", "enter_tag"]
        ] = [1, "ema_pullback"]

        return dataframe

    # ─────────────────────────────────────────────────────────────────────────
    # 出場條件
    # ─────────────────────────────────────────────────────────────────────────

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        cond_4h_death = dataframe["death_cross"] == 1
        cond_1d_bear  = dataframe["trend_up_1d"] == 0

        dataframe.loc[
            cond_4h_death,
            ["exit_long", "exit_tag"]
        ] = [1, "4h_death_cross"]

        dataframe.loc[
            cond_1d_bear & ~cond_4h_death,
            ["exit_long", "exit_tag"]
        ] = [1, "1d_trend_lost"]

        return dataframe

    # ─────────────────────────────────────────────────────────────────────────
    # 槓桿（1x 現貨）
    # ─────────────────────────────────────────────────────────────────────────

    def leverage(
        self,
        pair: str,
        current_time: datetime,
        current_rate: float,
        proposed_leverage: float,
        max_leverage: float,
        entry_tag: Optional[str],
        side: str,
        **kwargs,
    ) -> float:
        return 1.0
