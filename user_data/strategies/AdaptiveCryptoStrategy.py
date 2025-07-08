# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these imports ---
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from pandas import DataFrame
from typing import Optional, Union

from freqtrade.strategy import (
    IStrategy,
    Trade,
    Order,
    PairLocks,
    informative,
    BooleanParameter,
    CategoricalParameter,
    DecimalParameter,
    IntParameter,
    RealParameter,
    timeframe_to_minutes,
    timeframe_to_next_date,
    timeframe_to_prev_date,
    merge_informative_pair,
    stoploss_from_absolute,
    stoploss_from_open,
)

import talib.abstract as ta
from technical import qtpylib


class AdaptiveCryptoStrategy(IStrategy):
    """
    適應性加密貨幣交易策略 - Freqtrade版本
    
    核心理念：根據市場狀態自動切換交易邏輯
    - 趨勢市：使用趨勢跟隨策略 (EMA突破+動量確認)
    - 震盪市：使用均值回歸策略 (RSI極值+價格偏離)
    
    創新特點：
    1. 實時市場狀態檢測 (ATR+波動率+EMA分離度)
    2. 雙重策略自動切換
    3. ATR動態止損
    4. 多層風險控制
    """

    # Strategy interface version
    INTERFACE_VERSION = 3

    # Enable short selling
    can_short: bool = True

    # 時間框架：15分鐘平衡效率與準確性
    timeframe = "15m"

    # 動態ROI - 根據市場狀態調整
    minimal_roi = {
        "0": 0.05,    # 5% 初始目標
        "15": 0.03,   # 15分鐘後 3%
        "30": 0.02,   # 30分鐘後 2%
        "60": 0.015,  # 1小時後 1.5%
        "120": 0.01,  # 2小時後 1%
    }

    # 基礎止損 - 將由ATR動態調整
    stoploss = -0.03  # 3% 基礎止損

    # 追蹤止損配置
    trailing_stop = True
    trailing_stop_positive = 0.02     # 2%利潤後開始追蹤
    trailing_stop_positive_offset = 0.025  # 保持2.5%利潤
    trailing_only_offset_is_reached = True

    # Process only new candles
    process_only_new_candles = True

    # Exit signal
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # 策略參數 - 可優化
    lookback_period = IntParameter(15, 25, default=20, space="buy", optimize=True)
    atr_period = IntParameter(12, 16, default=14, space="buy", optimize=True)
    rsi_period = IntParameter(12, 16, default=14, space="buy", optimize=True)
    ema_fast_period = IntParameter(10, 14, default=12, space="buy", optimize=True)
    ema_slow_period = IntParameter(24, 30, default=26, space="buy", optimize=True)
    
    # 市場狀態判斷參數
    atr_expansion_threshold = RealParameter(1.15, 1.3, default=1.2, space="buy", optimize=True)
    ema_separation_threshold = RealParameter(0.008, 0.015, default=0.01, space="buy", optimize=True)
    volatility_threshold = RealParameter(1.05, 1.2, default=1.1, space="buy", optimize=True)
    
    # 趨勢策略參數
    trending_rsi_lower = IntParameter(25, 35, default=30, space="buy", optimize=True)
    trending_rsi_upper = IntParameter(70, 80, default=75, space="buy", optimize=True)
    trending_volume_threshold = RealParameter(1.05, 1.2, default=1.1, space="buy", optimize=True)
    
    # 震盪策略參數
    consolidation_rsi_oversold = IntParameter(25, 35, default=30, space="buy", optimize=True)
    consolidation_rsi_overbought = IntParameter(65, 75, default=70, space="sell", optimize=True)
    consolidation_ema_distance = RealParameter(0.015, 0.025, default=0.02, space="buy", optimize=True)

    # Startup candles
    startup_candle_count: int = 50

    # Order types
    order_types = {
        "entry": "limit",
        "exit": "limit", 
        "stoploss": "market",
        "stoploss_on_exchange": True,
    }

    order_time_in_force = {
        "entry": "GTC",
        "exit": "GTC"
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        計算技術指標和市場狀態指標
        """
        # 基礎技術指標
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=self.atr_period.value)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.rsi_period.value)
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=self.ema_fast_period.value)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=self.ema_slow_period.value)
        
        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        
        # 市場狀態檢測指標
        dataframe['price_range'] = (dataframe['high'] - dataframe['low']) / dataframe['close']
        dataframe['volatility'] = dataframe['close'].pct_change().rolling(self.lookback_period.value).std()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume'].rolling(self.lookback_period.value).mean()
        
        # ATR相關指標
        dataframe['atr_avg'] = dataframe['atr'].rolling(self.lookback_period.value).mean()
        dataframe['atr_expansion'] = dataframe['atr'] / dataframe['atr_avg']
        
        # EMA分離度
        dataframe['ema_separation'] = abs(dataframe['ema_fast'] - dataframe['ema_slow']) / dataframe['ema_slow']
        
        # 波動率指標
        dataframe['volatility_avg'] = dataframe['volatility'].rolling(self.lookback_period.value).mean()
        dataframe['volatility_ratio'] = dataframe['volatility'] / dataframe['volatility_avg']
        
        # 市場狀態檢測
        dataframe['market_regime'] = self._detect_market_regime(dataframe)
        
        # 動量指標
        dataframe['momentum_3'] = dataframe['close'].pct_change(periods=3)
        dataframe['momentum_6'] = dataframe['close'].pct_change(periods=6)
        
        # 布林帶
        bollinger = qtpylib.bollinger_bands(dataframe['close'], window=20, stds=2)
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_middle'] = bollinger['mid']
        dataframe['bb_upper'] = bollinger['upper']
        dataframe['bb_percent'] = (dataframe['close'] - dataframe['bb_lower']) / (dataframe['bb_upper'] - dataframe['bb_lower'])
        
        return dataframe

    def _detect_market_regime(self, dataframe: DataFrame) -> pd.Series:
        """
        市場狀態檢測：趨勢市 vs 震盪市
        
        趨勢市特徵：
        1. ATR持續擴大 (atr_expansion > threshold)
        2. EMA快慢線分離度大 (ema_separation > threshold)  
        3. 波動率上升 (volatility_ratio > threshold)
        
        至少滿足2個條件判定為趨勢市
        """
        # 初始化為震盪市
        regime = pd.Series(0, index=dataframe.index)  # 0=consolidation, 1=trending
        
        # 確保有足夠數據
        valid_idx = dataframe.index[self.lookback_period.value:]
        
        for idx in valid_idx:
            trending_conditions = [
                dataframe.loc[idx, 'atr_expansion'] > self.atr_expansion_threshold.value,
                dataframe.loc[idx, 'ema_separation'] > self.ema_separation_threshold.value,
                dataframe.loc[idx, 'volatility_ratio'] > self.volatility_threshold.value
            ]
            
            if sum(trending_conditions) >= 2:
                regime.loc[idx] = 1  # trending
            else:
                regime.loc[idx] = 0  # consolidation
                
        return regime

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        根據市場狀態選擇進場策略
        """
        # 趨勢跟隨策略 - 做多
        trending_long_conditions = (
            (dataframe['market_regime'] == 1) &  # 趨勢市
            (dataframe['ema_fast'] > dataframe['ema_slow']) &  # 快線在慢線上方
            (dataframe['close'] > dataframe['ema_fast']) &     # 價格在快線上方
            (dataframe['close'].shift(1) <= dataframe['ema_fast'].shift(1)) &  # 突破
            (dataframe['rsi'] > self.trending_rsi_lower.value) &
            (dataframe['rsi'] < self.trending_rsi_upper.value) &
            (dataframe['volume_ratio'] > self.trending_volume_threshold.value) &
            (dataframe['macd'] > dataframe['macdsignal']) &
            (dataframe['momentum_3'] > 0.001) &
            (dataframe['volume'] > 0)
        )
        
        # 趨勢跟隨策略 - 做空
        trending_short_conditions = (
            (dataframe['market_regime'] == 1) &  # 趨勢市
            (dataframe['ema_fast'] < dataframe['ema_slow']) &  # 快線在慢線下方
            (dataframe['close'] < dataframe['ema_fast']) &     # 價格在快線下方
            (dataframe['close'].shift(1) >= dataframe['ema_fast'].shift(1)) &  # 跌破
            (dataframe['rsi'] > self.trending_rsi_lower.value) &
            (dataframe['rsi'] < self.trending_rsi_upper.value) &
            (dataframe['volume_ratio'] > self.trending_volume_threshold.value) &
            (dataframe['macd'] < dataframe['macdsignal']) &
            (dataframe['momentum_3'] < -0.001) &
            (dataframe['volume'] > 0)
        )
        
        # 均值回歸策略 - 做多 (震盪市超賣)
        consolidation_long_conditions = (
            (dataframe['market_regime'] == 0) &  # 震盪市
            (dataframe['rsi'] < self.consolidation_rsi_oversold.value) &  # RSI超賣
            ((dataframe['close'] - dataframe['ema_slow']) / dataframe['ema_slow'] < -self.consolidation_ema_distance.value) &  # 價格偏離EMA
            (dataframe['bb_percent'] < 0.2) &  # 接近布林下軌
            (dataframe['volume'] > 0)
        )
        
        # 均值回歸策略 - 做空 (震盪市超買)
        consolidation_short_conditions = (
            (dataframe['market_regime'] == 0) &  # 震盪市
            (dataframe['rsi'] > self.consolidation_rsi_overbought.value) &  # RSI超買
            ((dataframe['close'] - dataframe['ema_slow']) / dataframe['ema_slow'] > self.consolidation_ema_distance.value) &  # 價格偏離EMA
            (dataframe['bb_percent'] > 0.8) &  # 接近布林上軌
            (dataframe['volume'] > 0)
        )
        
        # 合併所有做多條件
        dataframe.loc[
            trending_long_conditions | consolidation_long_conditions,
            'enter_long'
        ] = 1
        
        # 合併所有做空條件
        dataframe.loc[
            trending_short_conditions | consolidation_short_conditions,
            'enter_short'
        ] = 1
        
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        出場條件 - 根據策略類型和市場狀態
        """
        # 趨勢策略出場 - 做多
        trending_exit_long = (
            (dataframe['market_regime'] == 1) &  # 趨勢市
            (
                (dataframe['ema_fast'] <= dataframe['ema_slow']) |  # EMA交叉
                (dataframe['close'] < dataframe['ema_fast']) |      # 跌破快線
                (dataframe['rsi'] > 75) |                           # RSI超買
                (dataframe['macd'] < dataframe['macdsignal']) |     # MACD轉負
                (dataframe['momentum_3'] < -0.002)                  # 動量轉負
            )
        )
        
        # 趨勢策略出場 - 做空
        trending_exit_short = (
            (dataframe['market_regime'] == 1) &  # 趨勢市
            (
                (dataframe['ema_fast'] >= dataframe['ema_slow']) |  # EMA交叉
                (dataframe['close'] > dataframe['ema_fast']) |      # 突破快線
                (dataframe['rsi'] < 25) |                           # RSI超賣
                (dataframe['macd'] > dataframe['macdsignal']) |     # MACD轉正
                (dataframe['momentum_3'] > 0.002)                   # 動量轉正
            )
        )
        
        # 均值回歸出場 - 做多 (回到中軌或超買)
        consolidation_exit_long = (
            (dataframe['market_regime'] == 0) &  # 震盪市
            (
                (dataframe['rsi'] > 60) |                           # RSI回升
                (dataframe['close'] > dataframe['bb_middle']) |     # 回到中軌上方
                (dataframe['bb_percent'] > 0.6) |                   # 遠離下軌
                ((dataframe['close'] - dataframe['ema_slow']) / dataframe['ema_slow'] > 0.005)  # 回到EMA附近
            )
        )
        
        # 均值回歸出場 - 做空 (回到中軌或超賣)
        consolidation_exit_short = (
            (dataframe['market_regime'] == 0) &  # 震盪市
            (
                (dataframe['rsi'] < 40) |                           # RSI回落
                (dataframe['close'] < dataframe['bb_middle']) |     # 回到中軌下方
                (dataframe['bb_percent'] < 0.4) |                   # 遠離上軌
                ((dataframe['close'] - dataframe['ema_slow']) / dataframe['ema_slow'] < -0.005)  # 回到EMA附近
            )
        )
        
        # 合併出場條件
        dataframe.loc[
            trending_exit_long | consolidation_exit_long,
            'exit_long'
        ] = 1
        
        dataframe.loc[
            trending_exit_short | consolidation_exit_short,
            'exit_short'
        ] = 1
        
        return dataframe

    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime,
                       current_rate: float, current_profit: float, **kwargs) -> float:
        """
        ATR動態止損
        """
        # 獲取最新數據
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return self.stoploss
        
        # 獲取最新ATR
        latest_atr = dataframe['atr'].iloc[-1]
        entry_rate = trade.open_rate
        
        # 計算ATR止損距離 (2倍ATR)
        atr_stop_distance = 2 * latest_atr / entry_rate
        
        # 根據持倉方向調整
        if trade.is_short:
            return atr_stop_distance  # 做空使用正值
        else:
            return -atr_stop_distance  # 做多使用負值

    def custom_exit(self, pair: str, trade: Trade, current_time: datetime, 
                   current_rate: float, current_profit: float, **kwargs) -> Optional[Union[str, bool]]:
        """
        自定義出場邏輯 - 考慮市場狀態變化
        """
        # 獲取最新數據
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return None
        
        # 獲取最新市場狀態
        latest_regime = dataframe['market_regime'].iloc[-1]
        entry_regime = dataframe['market_regime'].iloc[-len(dataframe)//2]  # 大概的進場時市場狀態
        
        # 如果市場狀態發生重大變化，考慮出場
        if latest_regime != entry_regime:
            if current_profit > 0.01:  # 有1%以上利潤時可以因狀態變化而出場
                return "market_regime_change"
        
        # ATR動態止盈
        latest_atr = dataframe['atr'].iloc[-1]
        entry_rate = trade.open_rate
        atr_profit_target = 3 * latest_atr / entry_rate  # 3倍ATR止盈
        
        if trade.is_short:
            if current_profit > atr_profit_target:
                return "atr_profit_target"
        else:
            if current_profit > atr_profit_target:
                return "atr_profit_target"
        
        return None

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                           rate: float, time_in_force: str, current_time: datetime,
                           entry_tag: Optional[str], side: str, **kwargs) -> bool:
        """
        進場確認 - 最後的風險檢查
        """
        # 基本確認通過
        return True

    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag: Optional[str],
                 side: str, **kwargs) -> float:
        """
        根據市場狀態動態調整槓桿
        """
        # 獲取當前市場狀態
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return 2.0  # 默認保守槓桿
        
        latest_regime = dataframe['market_regime'].iloc[-1]
        latest_atr_expansion = dataframe['atr_expansion'].iloc[-1]
        
        # 趨勢市可以使用稍高槓桿，震盪市保守
        if latest_regime == 1:  # 趨勢市
            if latest_atr_expansion > 1.3:  # 高波動
                return 2.0
            else:
                return 2.5
        else:  # 震盪市
            return 1.5  # 更保守

    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                           proposed_stake: float, min_stake: Optional[float], max_stake: float,
                           leverage: float, entry_tag: Optional[str], side: str, **kwargs) -> float:
        """
        根據ATR動態調整倉位大小
        """
        # 獲取最新ATR數據
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return proposed_stake
        
        latest_atr = dataframe['atr'].iloc[-1]
        current_price = current_rate
        
        # 計算2倍ATR的風險距離
        atr_risk_distance = 2 * latest_atr / current_price
        
        # 目標每筆交易風險2%
        target_risk = 0.02
        if atr_risk_distance > 0:
            # 根據ATR風險調整倉位
            risk_adjusted_stake = (target_risk / atr_risk_distance) * proposed_stake
            # 限制在合理範圍內
            return max(min_stake or 0, min(risk_adjusted_stake, max_stake))
        
        return proposed_stake