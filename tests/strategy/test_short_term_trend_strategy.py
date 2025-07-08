import pytest
from pandas import DataFrame
from datetime import datetime, timezone
from unittest.mock import MagicMock

import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.strategy.interface import SellType
from freqtrade.persistence import Trade
from tests.conftest import get_patched_exchange
from tests.strategy.strats import StrategyTestV3


def test_short_term_trend_strategy_imports():
    """Test that ShortTermTrendStrategy can be imported"""
    from user_data.strategies.ShortTermTrendStrategy import ShortTermTrendStrategy
    assert ShortTermTrendStrategy


def test_short_term_trend_strategy_initialization():
    """Test strategy initialization"""
    from user_data.strategies.ShortTermTrendStrategy import ShortTermTrendStrategy
    
    strategy = ShortTermTrendStrategy({})
    
    # Test basic strategy attributes
    assert strategy.INTERFACE_VERSION == 3
    assert strategy.can_short is True
    assert strategy.timeframe == "3m"
    assert strategy.stoploss == -0.02
    assert strategy.trailing_stop is True
    assert strategy.leverage == 3


def test_short_term_trend_strategy_populate_indicators():
    """Test populate_indicators method"""
    from user_data.strategies.ShortTermTrendStrategy import ShortTermTrendStrategy
    
    strategy = ShortTermTrendStrategy({})
    
    # Create sample dataframe
    data = {
        'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109] * 10,
        'high': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111] * 10,
        'low': [98, 99, 100, 101, 102, 103, 104, 105, 106, 107] * 10,
        'close': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110] * 10,
        'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900] * 10
    }
    dataframe = DataFrame(data)
    
    # Test indicator population
    result = strategy.populate_indicators(dataframe, {'pair': 'BTC/USDT:USDT'})
    
    # Check that required indicators are present
    required_indicators = [
        'ema_fast', 'ema_slow', 'rsi', 'macd', 'macdsignal', 'macdhist',
        'adx', 'volume_mean', 'price_change', 'price_momentum',
        'bb_lower', 'bb_middle', 'bb_upper'
    ]
    
    for indicator in required_indicators:
        assert indicator in result.columns, f"Missing indicator: {indicator}"
    
    # Check that indicators have reasonable values
    assert not result['ema_fast'].isna().all()
    assert not result['ema_slow'].isna().all()
    assert not result['rsi'].isna().all()
    assert not result['macd'].isna().all()


def test_short_term_trend_strategy_populate_entry_trend():
    """Test populate_entry_trend method"""
    from user_data.strategies.ShortTermTrendStrategy import ShortTermTrendStrategy
    
    strategy = ShortTermTrendStrategy({})
    
    # Create sample dataframe with trend indicators
    data = {
        'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109] * 10,
        'high': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111] * 10,
        'low': [98, 99, 100, 101, 102, 103, 104, 105, 106, 107] * 10,
        'close': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110] * 10,
        'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900] * 10
    }
    dataframe = DataFrame(data)
    
    # Populate indicators first
    dataframe = strategy.populate_indicators(dataframe, {'pair': 'BTC/USDT:USDT'})
    
    # Populate entry signals
    result = strategy.populate_entry_trend(dataframe, {'pair': 'BTC/USDT:USDT'})
    
    # Check that entry columns are present
    assert 'enter_long' in result.columns
    assert 'enter_short' in result.columns
    
    # Check that entry signals are binary (0 or 1)
    assert result['enter_long'].isin([0, 1]).all()
    assert result['enter_short'].isin([0, 1]).all()


def test_short_term_trend_strategy_populate_exit_trend():
    """Test populate_exit_trend method"""
    from user_data.strategies.ShortTermTrendStrategy import ShortTermTrendStrategy
    
    strategy = ShortTermTrendStrategy({})
    
    # Create sample dataframe
    data = {
        'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109] * 10,
        'high': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111] * 10,
        'low': [98, 99, 100, 101, 102, 103, 104, 105, 106, 107] * 10,
        'close': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110] * 10,
        'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900] * 10
    }
    dataframe = DataFrame(data)
    
    # Populate indicators first
    dataframe = strategy.populate_indicators(dataframe, {'pair': 'BTC/USDT:USDT'})
    
    # Populate exit signals
    result = strategy.populate_exit_trend(dataframe, {'pair': 'BTC/USDT:USDT'})
    
    # Check that exit columns are present
    assert 'exit_long' in result.columns
    assert 'exit_short' in result.columns
    
    # Check that exit signals are binary (0 or 1)
    assert result['exit_long'].isin([0, 1]).all()
    assert result['exit_short'].isin([0, 1]).all()


def test_short_term_trend_strategy_leverage():
    """Test leverage function"""
    from user_data.strategies.ShortTermTrendStrategy import ShortTermTrendStrategy
    
    strategy = ShortTermTrendStrategy({})
    
    # Test leverage function
    leverage = strategy.leverage(
        pair='BTC/USDT:USDT',
        current_time=datetime.now(timezone.utc),
        current_rate=50000.0,
        proposed_leverage=5.0,
        max_leverage=10.0,
        entry_tag=None,
        side='long'
    )
    
    assert leverage == 3.0


def test_short_term_trend_strategy_confirm_trade_entry():
    """Test confirm_trade_entry function"""
    from user_data.strategies.ShortTermTrendStrategy import ShortTermTrendStrategy
    
    strategy = ShortTermTrendStrategy({})
    
    # Test trade entry confirmation
    confirm = strategy.confirm_trade_entry(
        pair='BTC/USDT:USDT',
        order_type='market',
        amount=0.01,
        rate=50000.0,
        time_in_force='GTC',
        current_time=datetime.now(timezone.utc),
        entry_tag=None,
        side='long'
    )
    
    assert confirm is True


def test_short_term_trend_strategy_parameters():
    """Test strategy parameters are within expected ranges"""
    from user_data.strategies.ShortTermTrendStrategy import ShortTermTrendStrategy
    
    strategy = ShortTermTrendStrategy({})
    
    # Test parameter ranges
    assert 5 <= strategy.fast_ema_period.value <= 15
    assert 20 <= strategy.slow_ema_period.value <= 35
    assert 10 <= strategy.rsi_period.value <= 20
    assert 25 <= strategy.rsi_oversold.value <= 35
    assert 65 <= strategy.rsi_overbought.value <= 75
    assert 8 <= strategy.macd_fast.value <= 15
    assert 20 <= strategy.macd_slow.value <= 30
    assert 7 <= strategy.macd_signal.value <= 12
    assert 12 <= strategy.adx_period.value <= 18
    assert 20 <= strategy.adx_threshold.value <= 30


def test_short_term_trend_strategy_startup_candle_count():
    """Test startup candle count is sufficient"""
    from user_data.strategies.ShortTermTrendStrategy import ShortTermTrendStrategy
    
    strategy = ShortTermTrendStrategy({})
    
    # Strategy needs sufficient candles for indicators
    assert strategy.startup_candle_count >= 50


def test_short_term_trend_strategy_order_types():
    """Test order types configuration"""
    from user_data.strategies.ShortTermTrendStrategy import ShortTermTrendStrategy
    
    strategy = ShortTermTrendStrategy({})
    
    # Test order types for futures trading
    assert strategy.order_types['entry'] == 'market'
    assert strategy.order_types['exit'] == 'market'
    assert strategy.order_types['stoploss'] == 'market'
    assert strategy.order_types['stoploss_on_exchange'] is True