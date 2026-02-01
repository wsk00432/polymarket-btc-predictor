"""
Utility functions for the Enhanced Trading Analysis System
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from .models import TechnicalIndicators, KlineData, OrderBookDepth, FundFlow, OISignal, TradingSignal
from .config import get_config


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """
    Calculate Relative Strength Index (RSI)
    """
    if len(prices) < period + 1:
        return 50.0  # Return neutral if insufficient data
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return float(rsi)


def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    """
    if len(prices) < slow:
        return {'macd': 0.0, 'signal': 0.0, 'histogram': 0.0}
    
    series = pd.Series(prices)
    exp1 = series.ewm(span=fast).mean()
    exp2 = series.ewm(span=slow).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    
    return {
        'macd': float(macd_line.iloc[-1]),
        'signal': float(signal_line.iloc[-1]),
        'histogram': float(histogram.iloc[-1])
    }


def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: int = 2) -> Dict[str, float]:
    """
    Calculate Bollinger Bands
    """
    if len(prices) < period:
        current_price = prices[-1] if prices else 0
        return {
            'upper': current_price,
            'middle': current_price,
            'lower': current_price,
            'current_price': current_price
        }
    
    series = pd.Series(prices)
    sma = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    
    return {
        'upper': float(upper_band.iloc[-1]),
        'middle': float(sma.iloc[-1]),
        'lower': float(lower_band.iloc[-1]),
        'current_price': float(prices[-1])
    }


def calculate_moving_averages(prices: List[float], periods: List[int] = None) -> Dict[str, float]:
    """
    Calculate multiple moving averages
    """
    if periods is None:
        periods = get_config('MA_PERIODS', [5, 10, 20, 50])
    
    if not prices:
        return {'current_price': 0.0}
    
    series = pd.Series(prices)
    mas = {}
    
    for period in periods:
        if len(prices) >= period:
            ma = series.rolling(window=period).mean()
            mas[f'ma_{period}'] = float(ma.iloc[-1])
        else:
            mas[f'ma_{period}'] = float(prices[-1])
    
    mas['current_price'] = float(prices[-1])
    return mas


def calculate_volatility(prices: List[float], window: int = 20) -> float:
    """
    Calculate price volatility as standard deviation of returns
    """
    if len(prices) < 2:
        return get_config('DEFAULT_VOLATILITY', 2.5)
    
    returns = np.diff(prices) / prices[:-1]
    
    if len(returns) < window:
        window = len(returns)
    
    if window < 1:
        return get_config('DEFAULT_VOLATILITY', 2.5)
    
    volatility = np.std(returns[-window:]) * np.sqrt(365) * 100  # Annualized
    return float(volatility)


def calculate_support_resistance(prices: List[float], window: int = 20) -> Dict[str, float]:
    """
    Calculate approximate support and resistance levels
    """
    if len(prices) < window:
        window = len(prices)
    
    recent_prices = prices[-window:]
    max_price = max(recent_prices)
    min_price = min(recent_prices)
    
    # Calculate pivot points
    pivot = (max_price + min_price) / 2
    
    return {
        'resistance': max_price,
        'support': min_price,
        'pivot': pivot
    }


def analyze_order_flow(order_book: OrderBookDepth) -> Dict[str, Any]:
    """
    Analyze order book for potential signals
    """
    total_bid_volume = order_book.bid_volume
    total_ask_volume = order_book.ask_volume
    total_volume = total_bid_volume + total_ask_volume
    
    if total_volume == 0:
        return {
            'bid_ask_ratio': 1.0,
            'order_imbalance': 0.0,
            'pressure': 'NEUTRAL'
        }
    
    bid_ask_ratio = total_bid_volume / total_ask_volume if total_ask_volume > 0 else float('inf')
    order_imbalance = (total_bid_volume - total_ask_volume) / total_volume
    
    # Determine pressure based on top levels
    top_bids = sum([item['quantity'] for item in order_book.bids[:5]]) if order_book.bids else 0
    top_asks = sum([item['quantity'] for item in order_book.asks[:5]]) if order_book.asks else 0
    
    total_top_volume = top_bids + top_asks
    if total_top_volume > 0:
        top_level_pressure = (top_bids - top_asks) / total_top_volume
    else:
        top_level_pressure = 0
    
    if abs(order_imbalance) > 0.1:  # Significant imbalance
        pressure = 'BULLISH' if order_imbalance > 0 else 'BEARISH'
    else:
        pressure = 'NEUTRAL'
    
    return {
        'bid_ask_ratio': bid_ask_ratio,
        'order_imbalance': order_imbalance,
        'top_level_pressure': top_level_pressure,
        'pressure': pressure
    }


def detect_trend(prices: List[float], ma_short: int = 5, ma_long: int = 20) -> str:
    """
    Detect trend based on moving average relationship
    """
    if len(prices) < ma_long:
        return 'NEUTRAL'
    
    series = pd.Series(prices)
    short_ma = series.rolling(window=ma_short).mean().iloc[-1]
    long_ma = series.rolling(window=ma_long).mean().iloc[-1]
    current_price = prices[-1]
    
    # Determine trend based on MA relationship and price position
    if current_price > short_ma > long_ma:
        return 'BULLISH'
    elif current_price < short_ma < long_ma:
        return 'BEARISH'
    elif short_ma > long_ma:
        return 'BULLISH_MOMENTUM'
    elif short_ma < long_ma:
        return 'BEARISH_MOMENTUM'
    else:
        return 'NEUTRAL'


def calculate_correlation_matrix(data: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
    """
    Calculate correlation matrix between different data series
    """
    df = pd.DataFrame(data)
    correlation_matrix = df.corr()
    
    result = {}
    for col1 in correlation_matrix.columns:
        result[col1] = {}
        for col2 in correlation_matrix.columns:
            result[col1][col2] = float(correlation_matrix.loc[col1, col2])
    
    return result


def normalize_value(value: float, min_val: float, max_val: float, target_min: float = -1.0, target_max: float = 1.0) -> float:
    """
    Normalize a value from one range to another
    """
    if max_val == min_val:
        return 0.0  # Avoid division by zero
    
    normalized = (value - min_val) / (max_val - min_val)
    return target_min + normalized * (target_max - target_min)


def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sharpe ratio for a series of returns
    """
    if len(returns) < 2:
        return 0.0
    
    excess_returns = [r - risk_free_rate/252 for r in returns]  # Assuming daily returns
    avg_excess_return = np.mean(excess_returns)
    volatility = np.std(excess_returns)
    
    if volatility == 0:
        return 0.0
    
    # Annualize Sharpe ratio
    sharpe = avg_excess_return / volatility
    return float(sharpe * np.sqrt(252))


def format_currency(value: float, currency: str = 'USD') -> str:
    """
    Format a value as currency
    """
    if currency.upper() == 'BTC':
        return f"{value:.8f} BTC"
    elif currency.upper() == 'ETH':
        return f"{value:.6f} ETH"
    else:
        return f"${value:,.2f}"


def save_to_json(data: Any, filename: str, indent: int = 2) -> None:
    """
    Save data to JSON file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, default=str)


def load_from_json(filename: str) -> Any:
    """
    Load data from JSON file
    """
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def setup_logging(log_file: str = None, log_level: str = 'INFO'):
    """
    Setup logging for the application
    """
    logger = logging.getLogger('EnhancedTradingSystem')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


async def async_delay(seconds: float):
    """
    Asynchronous delay utility
    """
    await asyncio.sleep(seconds)


def safe_float_conversion(value: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to float
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
    """
    Calculate Average True Range (ATR) for volatility measurement
    """
    if len(closes) < period + 1:
        return 0.0
    
    true_ranges = []
    for i in range(1, len(closes)):
        high = highs[i] if i < len(highs) else closes[i]
        low = lows[i] if i < len(lows) else closes[i]
        prev_close = closes[i-1]
        
        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )
        true_ranges.append(tr)
    
    if len(true_ranges) < period:
        return np.mean(true_ranges) if true_ranges else 0.0
    
    atr = np.mean(true_ranges[-period:])
    return float(atr)


def calculate_stochastic_oscillator(
    highs: List[float], 
    lows: List[float], 
    closes: List[float], 
    k_period: int = 14, 
    d_period: int = 3
) -> Dict[str, float]:
    """
    Calculate Stochastic Oscillator (K%D lines)
    """
    if len(closes) < k_period:
        return {'k': 50.0, 'd': 50.0}
    
    # Calculate %K
    recent_highs = highs[-k_period:] if len(highs) >= k_period else highs
    recent_lows = lows[-k_period:] if len(lows) >= k_period else lows
    current_close = closes[-1]
    
    highest_high = max(recent_highs)
    lowest_low = min(recent_lows)
    
    if highest_high == lowest_low:
        k_value = 50.0
    else:
        k_value = (current_close - lowest_low) / (highest_high - lowest_low) * 100
    
    # Calculate %D (3-period SMA of %K)
    # For now, we'll return the current K value as both K and D
    # In a full implementation, we'd track multiple K values to calculate D
    return {
        'k': float(k_value),
        'd': float(k_value)  # Simplified - in practice, D is SMA of K
    }


def prepare_for_ml(data: Dict[str, float]) -> List[float]:
    """
    Prepare data for machine learning models by converting to normalized feature vector
    """
    features = []
    
    # Normalize each feature to range [-1, 1] or [0, 1] based on meaning
    for key, value in data.items():
        if 'ratio' in key.lower() or 'percentage' in key.lower():
            # Ratios and percentages typically in [0, 1] or [0, 100], normalize to [-1, 1]
            features.append(normalize_value(min(max(value, 0), 100), 0, 100, -1, 1))
        elif 'price' in key.lower() or 'volume' in key.lower():
            # Log-transform large values like prices and volumes
            log_val = np.log(abs(value) + 1) if value != 0 else 0
            features.append(normalize_value(log_val, 0, 10, -1, 1))
        elif 'score' in key.lower() or key in ['rsi', 'k', 'd']:
            # Scores typically in [0, 100], normalize to [-1, 1]
            features.append(normalize_value(value, 0, 100, -1, 1))
        else:
            # Other values, normalize assuming reasonable bounds
            features.append(normalize_value(min(max(value, -100), 100), -100, 100, -1, 1))
    
    return features


def generate_signal_summary(signal: TradingSignal) -> str:
    """
    Generate a textual summary of a trading signal
    """
    summary_parts = [
        f"Symbol: {signal.symbol}",
        f"Recommendation: {signal.recommendation.value}",
        f"Confidence: {signal.confidence_level:.1f}%",
        f"Composite Score: {signal.composite_score:.3f}"
    ]
    
    if signal.technical_indicators:
        ti = signal.technical_indicators
        summary_parts.append(f"RSI: {ti.rsi:.2f}")
        current_price = ti.moving_averages.get('current_price', 'N/A')
        summary_parts.append(f"Price: {current_price}")
    
    if signal.risk_management:
        rm = signal.risk_management
        if rm.stop_loss:
            summary_parts.append(f"Stop Loss: {rm.stop_loss}")
        if rm.take_profit:
            summary_parts.append(f"Take Profit: {rm.take_profit}")
    
    return " | ".join(summary_parts)