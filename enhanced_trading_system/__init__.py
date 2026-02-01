"""
Enhanced Trading Analysis System - Package Initialization

This package provides a comprehensive trading analysis system that integrates:
- Real-time technical indicators (RSI, MACD, Bollinger Bands, Moving Averages)
- 5-minute K-line data
- Real-time order book depth
- Funds flow analysis
- OI signal integration
- Risk management with dynamic stop-loss/take-profit
- Real-time trading signal panel
"""

__version__ = "1.0.0"
__author__ = "Enhanced Trading System"

from .trading_system import EnhancedTradingSystem
from .data_fetcher import DataFetcher, MockDataFetcher
from .models import *
from .config import *

def create_default_system():
    """
    Create a default instance of the Enhanced Trading System
    """
    return EnhancedTradingSystem()

__all__ = [
    'EnhancedTradingSystem',
    'DataFetcher', 
    'MockDataFetcher',
    'create_default_system',
    # Models
    'TechnicalIndicators',
    'KlineData', 
    'OrderBookDepth',
    'FundFlow',
    'OISignal',
    'RiskParameters',
    'TradingSignal',
    'TradingSignalPanel',
    'HistoricalDataPoint',
    'BacktestResult',
    'MarketSnapshot',
    # Config
    'get_config',
    'update_config',
    'validate_config'
]