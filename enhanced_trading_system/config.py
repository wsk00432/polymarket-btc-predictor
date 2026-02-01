"""
Configuration settings for the Enhanced Trading Analysis System
"""

import os
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG = {
    # Binance API settings
    'BINANCE_API_KEY': os.getenv('BINANCE_API_KEY', ''),
    'BINANCE_SECRET_KEY': os.getenv('BINANCE_SECRET_KEY', ''),
    
    # Data retrieval settings
    'KLINE_INTERVAL': '5m',  # 5-minute intervals
    'KLINE_LIMIT': 100,      # Number of klines to retrieve
    'ORDER_BOOK_LIMIT': 100, # Order book depth
    
    # Technical indicator settings
    'RSI_PERIOD': 14,
    'MACD_FAST': 12,
    'MACD_SLOW': 26,
    'MACD_SIGNAL': 9,
    'BB_PERIOD': 20,
    'BB_STD_DEV': 2,
    'MA_PERIODS': [5, 10, 20, 50],
    
    # Risk management settings
    'MAX_RISK_PER_TRADE': 0.02,  # 2% maximum risk per trade
    'RISK_REWARD_RATIO': 2.0,    # 1:2 risk-reward ratio
    'DEFAULT_VOLATILITY': 2.5,   # Default volatility percentage
    
    # Signal integration weights
    'INDICATOR_WEIGHTS': {
        'rsi': 0.25,           # 25% weight to RSI
        'macd': 0.20,          # 20% weight to MACD
        'bollinger_bands': 0.20, # 20% weight to Bollinger Bands
        'oi_signals': 0.25,    # 25% weight to OI signals
        'trend': 0.10          # 10% weight to trend
    },
    
    # Market symbols to monitor
    'DEFAULT_SYMBOLS': [
        'BTCUSDT',
        'ETHUSDT',
        'BNBUSDT',
        'ADAUSDT',
        'XRPUSDT',
        'SOLUSDT',
        'DOTUSDT',
        'LINKUSDT'
    ],
    
    # Update intervals (in seconds)
    'DATA_UPDATE_INTERVAL': 30,      # 30 seconds for regular updates
    'SIGNAL_PANEL_REFRESH': 60,      # 60 seconds for signal panel refresh
    'FULL_ANALYSIS_INTERVAL': 300,   # 5 minutes for full analysis
    
    # Logging settings
    'LOG_LEVEL': 'INFO',
    'LOG_FILE': 'trading_system.log',
    
    # Database settings (for storing historical data)
    'DATABASE_URL': os.getenv('DATABASE_URL', 'sqlite:///trading_data.db'),
    
    # Webhook settings (for sending alerts)
    'WEBHOOK_ENABLED': False,
    'WEBHOOK_URL': os.getenv('WEBHOOK_URL', ''),
    
    # Simulation mode (for testing without real API keys)
    'SIMULATION_MODE': True,
}

def get_config(key: str, default: Any = None) -> Any:
    """
    Get configuration value by key
    """
    return DEFAULT_CONFIG.get(key, default)

def update_config(config_dict: Dict[str, Any]) -> None:
    """
    Update configuration with new values
    """
    DEFAULT_CONFIG.update(config_dict)

def validate_config() -> bool:
    """
    Validate configuration settings
    """
    # Check if required settings are present
    required_keys = ['KLINE_INTERVAL', 'KLINE_LIMIT', 'ORDER_BOOK_LIMIT']
    for key in required_keys:
        if key not in DEFAULT_CONFIG:
            print(f"Missing required configuration key: {key}")
            return False
    
    # Validate intervals
    intervals = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
    if DEFAULT_CONFIG['KLINE_INTERVAL'] not in intervals:
        print(f"Invalid KLINE_INTERVAL: {DEFAULT_CONFIG['KLINE_INTERVAL']}")
        return False
    
    # Validate limits
    if DEFAULT_CONFIG['KLINE_LIMIT'] <= 0 or DEFAULT_CONFIG['KLINE_LIMIT'] > 1000:
        print(f"Invalid KLINE_LIMIT: {DEFAULT_CONFIG['KLINE_LIMIT']}. Must be between 1-1000")
        return False
    
    if DEFAULT_CONFIG['ORDER_BOOK_LIMIT'] <= 0 or DEFAULT_CONFIG['ORDER_BOOK_LIMIT'] > 1000:
        print(f"Invalid ORDER_BOOK_LIMIT: {DEFAULT_CONFIG['ORDER_BOOK_LIMIT']}. Must be between 1-1000")
        return False
    
    return True

# Validate config on import
config_valid = validate_config()
if not config_valid:
    print("Warning: Configuration validation failed!")