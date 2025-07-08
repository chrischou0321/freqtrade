# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About Freqtrade

Freqtrade is a free and open-source cryptocurrency trading bot written in Python. It supports all major exchanges, can be controlled via Telegram or WebUI, and includes backtesting, plotting, money management tools, and strategy optimization through machine learning (FreqAI).

## Development Commands

### Setup
```bash
# Automated setup for development
./setup.sh

# Manual setup
pip install -r requirements-dev.txt
pip install -e .[all]
pre-commit install
```

### Code Quality
```bash
ruff check .              # Linting
ruff format .             # Formatting  
mypy freqtrade           # Type checking
pytest                   # Run all tests
pytest tests/test_<file>.py              # Run specific test file
pytest tests/test_<file>.py::test_<method>  # Run specific test
pre-commit run -a        # All pre-commit hooks
```

### Bot Operations
```bash
# Start trading
freqtrade trade --config config.json

# Backtesting
freqtrade backtesting --config config.json --strategy SampleStrategy

# Hyperopt (strategy optimization)
freqtrade hyperopt --config config.json --hyperopt-loss SharpeHyperOptLoss --strategy SampleStrategy

# Download data
freqtrade download-data --config config.json --exchange binance --pairs BTC/USDT ETH/USDT
```

## Architecture Overview

### Core Entry Points
- `freqtrade/main.py` - Main bot entry point with CLI argument parsing
- `freqtrade/worker.py` - Main trading worker that orchestrates bot operations
- `freqtrade/freqtradebot.py` - Core bot logic and trading loop

### Key Module Structure
- **`commands/`** - CLI command implementations (trade, backtest, hyperopt, etc.)
- **`configuration/`** - Configuration management and validation using JSON schemas
- **`data/`** - Data handling, conversion, and backtesting analysis
- **`exchange/`** - Exchange-specific implementations with ccxt integration
- **`freqai/`** - Machine learning models and AI-driven strategy optimization
- **`optimize/`** - Backtesting engine and hyperparameter optimization
- **`persistence/`** - Database models using SQLAlchemy (trades, pairs, orders)
- **`plugins/`** - Extensible pairlist and protection plugins system
- **`rpc/`** - Remote procedure call implementations (Telegram, REST API, WebSocket)
- **`strategy/`** - Strategy interface and helper functions
- **`templates/`** - Jinja2 templates for strategy and configuration generation

### Exchange Architecture
- Uses ccxt library for exchange abstraction
- Exchange-specific implementations in `exchange/` directory
- Supports spot and futures trading (futures is experimental)
- Handles rate limiting, retries, and error handling per exchange

### Strategy System
- All strategies inherit from `IStrategy` base class
- Required methods: `populate_indicators()`, `populate_entry_trend()`, `populate_exit_trend()`
- Optional methods for advanced features: `custom_stoploss()`, `custom_exit()`, `confirm_trade_entry()`
- Strategy parameters can be optimized via hyperopt

### Data Pipeline
- Supports multiple data formats: JSON, Feather, Parquet
- Timeframe conversion and resampling
- Data validation and cleaning
- Backtesting data analysis with rich statistical outputs

### FreqAI Integration
- ML-based strategy optimization using scikit-learn, catboost, lightgbm, xgboost, pytorch
- Feature engineering pipeline
- Model training and prediction integration
- Reinforcement learning support for advanced strategies

## Development Standards

### Code Quality
- Max line length: 100 characters
- Type hints required for all public methods
- Docstrings required for all public methods (reST format)
- All tests must pass before merging

### Branch Structure
- `develop` - Main development branch (target for PRs)
- `stable` - Latest stable release
- `feat/*` - Feature branches

### Testing
- Unit tests for all new functionality
- Integration tests for exchange compatibility
- Strategy tests using multiple test strategies
- Online tests require API keys (optional)

## Configuration

### User Directory Structure
```
user_data/
├── backtest_results/     # Backtesting results and analysis
├── data/                # Historical market data
├── freqaimodels/        # Trained FreqAI models
├── hyperopts/           # Hyperopt results
├── logs/                # Bot logs
├── notebooks/           # Jupyter notebooks for analysis
└── strategies/          # Custom strategies
```

### Configuration Files
- `config_examples/` contains exchange-specific configuration templates
- Configuration uses JSON with extensive validation
- Supports dry-run mode for testing strategies

## Docker Development

### Building
```bash
docker build -t freqtrade .
docker-compose up -d
```

### Key Environment Variables
- `FREQTRADE_STRATEGY` - Strategy to use (default: SampleStrategy)
- `FREQTRADE_CONFIG` - Configuration file path
- Web interface exposed on port 8080

## Key Technical Decisions

### Async/Sync Architecture
- Main bot loop is synchronous for reliability
- WebSocket connections and API server use async/await
- Exchange operations use synchronous ccxt for consistency

### Error Handling
- Comprehensive exception hierarchy
- Graceful handling of exchange errors and network issues
- Detailed logging with structured output

### Performance Optimizations
- Periodic cache for expensive operations
- Multi-process support for hyperopt
- Efficient data structures for large datasets

### Plugin System
- Extensible pairlist plugins for dynamic pair selection
- Protection plugins for risk management
- Clean interfaces for custom implementations

## FreqAI Specific Notes

### Model Types
- Regression models for price prediction
- Classification models for buy/sell signals
- Reinforcement learning for adaptive strategies

### Data Pipeline
- Feature engineering with technical indicators
- Data normalization and scaling
- Train/test split with proper time-based validation

### Model Management
- Model versioning and storage
- Automatic retraining based on performance
- Integration with backtesting for strategy validation