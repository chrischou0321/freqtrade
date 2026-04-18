"""
BTCWeeklySwing — BTC 4H 動量突破策略（MTF架構）
================================================

版本歷史：
  v1-v6：RSI回調進場（均值回歸），失敗，勝率42%，低於費用損益平衡44%
  v7：4h動量突破，勝率56.9%，+3.32%，但ROI出場截斷贏家；頻率0.6次/月
  v8：1h主時框，ROI出場，RR=0.74（負期望），頻率1.37次/月
  v9：1h主時框，移動止損出場，贏家跑但勝率降至44.3%（假突破太多）
  v10：1h+ATR buffer過濾假突破，勝率38.4%（進場更晚，更差）
  v11：回到4h主時框（v7品質進場，56.9%勝率），換移動止損出場捕捉動量
  v12：出場Hyperopt（CalmarLoss），雙段式移動止損，CAGR 0.93%→16.83%

v11假設：
  4h進場品質（v7已驗證勝率56.9%）+ 移動止損出場（取代截斷贏家的ROI）
  = 正報酬 + 更好的RR

頻率問題說明：
  4h主時框的頻率限制（0.6-3次/月）來自多層過濾的累積效應。
  先驗證策略的邊際（Edge）是否存在，再通過Hyperopt調整頻率。
  寧可少交易但每筆有邊際，不要多交易但負期望值。

設計目標：
  與BTCIndexTracker v11並行獨立績效

核心架構（v11）：
  Primary timeframe : 4h（信號執行）
  Informative 1d    : 大方向確認（EMA50站上）

進場邏輯：
  1. 1d EMA50 上方（大方向多頭）
  2. 4h EMA20 > EMA50（中期趨勢向上）
  3. 4h 收盤突破 N 根高點（動量突破信號）
  4. 量能放大（≥ 1.3x 均量）
  5. RSI 不超買（< 70），下限40
  6. ADX ≥ 20（趨勢強度確認）

出場邏輯（v11關鍵改動 vs v7）：
  v7：ROI 4%(0h)/3%(24h)/2%(48h) → 截斷贏家
  v11：移動止損 → 達3%後啟動，保護2%利潤（贏家跑）
  - 初始止損：-3%（4h需要更多呼吸空間）
  - 移動止損：達3%後啟動，保護2%獲利
  - 極高ROI天花板：15%（幾乎不觸發）
  - 信號出場：4h EMA死叉 或 1d 趨勢轉空

熔斷機制（B2）：連敗3次 → 等待1d EMA50重新站回才重啟

Phase 1：Binance BTC/USDT 現貨，1x槓桿，2017.9-2025.12
Phase 2：勝率穩定>50%才執行，2x槓桿
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


# ─── 熔斷版本選擇 ────────────────────────────────────────────────────────────────
# "none" = Base，"streak_ema" = B2（推薦）
CIRCUIT_BREAKER = "none"


class BTCWeeklySwing(IStrategy):
    """BTC 4H 動量突破策略（MTF：4h執行 + 1d大方向）v11"""

    INTERFACE_VERSION = 3
    timeframe = "4h"
    startup_candle_count = 200    # 4h EMA50 需要 50 根 = 200h + buffer

    can_short = False             # Phase 1 long-only

    # ── v12 出場邏輯：雙段式移動止損（exit-HO 優化結果）─────────────────────────
    # 機制說明：
    #   Phase A（未達offset）：從最高點追蹤 -5.7%（截斷無動能交易）
    #   Phase B（達+19.3%）  ：切換至 -15.7% 追蹤，讓大動量盡情跑
    # 效果：CAGR 0.93% → 16.83%，Calmar 0.34 → 12.17
    minimal_roi = {
        "0": 0.15,   # 15% — 天花板，偶爾觸發（最佳交易 +14.99% = ROI出場）
    }

    stoploss = -0.057             # 初始止損 -5.7%（更寬，允許更多呼吸空間）
    trailing_stop = True
    trailing_stop_positive = 0.157          # 達+15.7%後縮緊保護比例
    trailing_stop_positive_offset = 0.193  # +19.3%高點後切換為寬追蹤
    trailing_only_offset_is_reached = False  # 從進場即開始追蹤

    use_custom_stoploss = False

    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    process_only_new_candles = True

    # ── Hyperopt 參數 ─────────────────────────────────────────────────────────
    # Buy space（進場條件）
    # Hyperopt epoch 79 best params (IS: 2019-2024, 57 trades, 59.6% win, +10.7%)
    breakout_bars = IntParameter(4, 16, default=11, space="buy", optimize=True)
    vol_ratio     = DecimalParameter(1.0, 2.5, default=1.7, decimals=1, space="buy", optimize=True)
    rsi_max       = IntParameter(55, 78, default=75, space="buy", optimize=True)
    rsi_min       = IntParameter(25, 55, default=31, space="buy", optimize=True)
    adx_min       = IntParameter(15, 35, default=20, space="buy", optimize=True)
    # Sell space（出場優化）：trailing stop是靜態設定，用ROI表格作為sell space
    # 使用minimal_roi作為保底（sell space在freqtrade通過stoploss優化）

    # ── 熔斷狀態 ────────────────────────────────────────────────────────────
    _consecutive_losses: int = 0
    _circuit_open: bool = False
    _circuit_open_since: Optional[datetime] = None
    _circuit_open_close_ema50: float = 0.0

    # ─────────────────────────────────────────────────────────────────────────
    # 1D 大方向指標（informative）
    # ─────────────────────────────────────────────────────────────────────────

    @informative("1d")
    def populate_indicators_1d(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_20"] = ta.EMA(dataframe["close"], timeperiod=20)
        dataframe["ema_50"] = ta.EMA(dataframe["close"], timeperiod=50)

        # 大方向：收盤 > 1d EMA50
        dataframe["trend_up"] = (
            dataframe["close"] > dataframe["ema_50"]
        ).astype(int)

        # 制度濾網（v12 C優化）：1d EMA20 > EMA50（雙均線多頭排列）
        # 2021年5月大跌時EMA20跌破EMA50，此條件可攔截假趨勢進場
        dataframe["dual_ema_bull"] = (
            dataframe["ema_20"] > dataframe["ema_50"]
        ).astype(int)

        # 熔斷重啟判斷：EMA50 站回且斜率向上
        dataframe["ema50_recovering"] = (
            (dataframe["close"] > dataframe["ema_50"]) &
            (dataframe["ema_50"] > dataframe["ema_50"].shift(3))
        ).astype(int)

        return dataframe

    # ─────────────────────────────────────────────────────────────────────────
    # 4H 主要指標（primary timeframe）
    # ─────────────────────────────────────────────────────────────────────────

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # ── 4H 趨勢指標 ──────────────────────────────────────────────────────
        dataframe["ema_20"]    = ta.EMA(dataframe["close"], timeperiod=20)
        dataframe["ema_50"]    = ta.EMA(dataframe["close"], timeperiod=50)
        dataframe["adx"]       = ta.ADX(dataframe, timeperiod=14)
        dataframe["rsi"]       = ta.RSI(dataframe["close"], timeperiod=14)
        dataframe["vol_ema20"] = ta.EMA(dataframe["volume"], timeperiod=20)
        dataframe["atr"]       = ta.ATR(dataframe, timeperiod=14)

        # ── 4h EMA 方向 ───────────────────────────────────────────────────────
        dataframe["trend_up"] = (dataframe["ema_20"] > dataframe["ema_50"]).astype(int)

        # ── 4h EMA 死叉（用於出場）────────────────────────────────────────────
        dataframe["death_cross"] = (
            (dataframe["ema_20"] < dataframe["ema_50"]) &
            (dataframe["ema_20"].shift(1) >= dataframe["ema_50"].shift(1))
        ).astype(int)

        # ── 突破水位（shift(1) 防 lookahead）─────────────────────────────────
        for v in self.breakout_bars.range:
            dataframe[f"high_{v}"] = dataframe["high"].shift(1).rolling(v).max()

        return dataframe

    # ─────────────────────────────────────────────────────────────────────────
    # 進場條件（4h動量突破）
    # ─────────────────────────────────────────────────────────────────────────

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        三層過濾動量突破進場：
          Layer 1 — 1d EMA50 上方（大方向多頭）
          Layer 2 — 4h EMA20 > EMA50（中期趨勢向上）
          Layer 3 — 4h 收盤突破 N 根高點 + 量能 + RSI 範圍 + ADX
        """
        n   = int(self.breakout_bars.value)
        col = f"high_{n}"

        # Layer 1：大方向（1d close > EMA50，雙EMA濾網測試後撤回，效果負面）
        cond_1d = dataframe["trend_up_1d"] == 1

        # Layer 2：4h 中期趨勢
        cond_4h = dataframe["trend_up"] == 1

        # Layer 3A：突破信號（4h收盤突破N根高點）
        cond_breakout = (
            (col in dataframe.columns) &
            (dataframe["close"] > dataframe[col])
        )

        # Layer 3B：量能確認
        cond_volume = dataframe["volume"] > dataframe["vol_ema20"] * self.vol_ratio.value

        # Layer 3C：RSI 範圍（非超賣也非極端超買）
        cond_rsi = (
            (dataframe["rsi"] >= self.rsi_min.value) &
            (dataframe["rsi"] <= self.rsi_max.value)
        )

        # Layer 3D：ADX 趨勢強度
        cond_adx = dataframe["adx"] >= self.adx_min.value

        base_signal = (
            cond_1d &
            cond_4h &
            cond_breakout &
            cond_volume &
            cond_rsi &
            cond_adx
        )

        dataframe.loc[
            base_signal,
            ["enter_long", "enter_tag"]
        ] = [1, "breakout_4h"]

        return dataframe

    # ─────────────────────────────────────────────────────────────────────────
    # 出場條件
    # ─────────────────────────────────────────────────────────────────────────

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        出場信號：
          - 4h EMA 死叉（中期趨勢翻空）
          - 1d 趨勢轉空（大方向改變）
        v11：移動止損是主要保護機制，信號出場作為趨勢崩潰後備
        """
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
    # 熔斷機制（B2）
    # ─────────────────────────────────────────────────────────────────────────

    def confirm_trade_entry(
        self,
        pair: str,
        order_type: str,
        amount: float,
        rate: float,
        time_in_force: str,
        current_time: datetime,
        entry_tag: Optional[str],
        side: str,
        **kwargs,
    ) -> bool:
        if CIRCUIT_BREAKER == "none":
            return True

        if self._circuit_open:
            if CIRCUIT_BREAKER == "streak_ema":
                df_1d, _ = self.dp.get_analyzed_dataframe(pair, "1d")
                if df_1d.empty:
                    return False
                last_1d = df_1d.iloc[-1]
                recovered = (
                    last_1d.get("ema50_recovering_1d", 0) == 1 and
                    last_1d["close"] > self._circuit_open_close_ema50 * 1.01
                )
                if recovered:
                    self._circuit_open = False
                    self._consecutive_losses = 0
                    return True
                return False

        return True

    def confirm_trade_exit(
        self,
        pair: str,
        trade,
        order_type: str,
        amount: float,
        rate: float,
        time_in_force: str,
        exit_reason: str,
        current_time: datetime,
        **kwargs,
    ) -> bool:
        if CIRCUIT_BREAKER == "none":
            return True

        # 統計連敗（只計算虧損出場）
        if trade.calc_profit_ratio(rate) < 0:
            self._consecutive_losses += 1
            if self._consecutive_losses >= 3:
                self._circuit_open = True
                self._circuit_open_since = current_time
                df_1d, _ = self.dp.get_analyzed_dataframe(pair, "1d")
                if not df_1d.empty:
                    self._circuit_open_close_ema50 = df_1d.iloc[-1].get("ema_50_1d", rate)
        else:
            self._consecutive_losses = 0

        return True

    # ─────────────────────────────────────────────────────────────────────────
    # 槓桿（Phase 1 = 1x 現貨）
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
