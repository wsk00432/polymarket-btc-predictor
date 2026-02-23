"""
Technical Indicator Calculator Module
Calculates various technical indicators for trading analysis
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
import logging


class TechnicalIndicatorCalculator:
    """
    Calculator class for various technical indicators
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """
        Calculate Relative Strength Index (RSI)
        """
        if len(prices) < period + 1:
            return 50.0  # Return neutral value if not enough data
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calculate average gains and losses using exponential moving average
        avg_gains = self._ema(gains, period)
        avg_losses = self._ema(losses, period)
        
        # Prevent division by zero
        if avg_losses[-1] == 0:
            return 100.0
        
        rs = avg_gains[-1] / avg_losses[-1]
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, prices: List[float], 
                      fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        """
        if len(prices) < slow_period:
            return {'macd': 0.0, 'signal': 0.0, 'histogram': 0.0}
        
        # Calculate EMAs
        ema_fast = self._ema(prices, fast_period)
        ema_slow = self._ema(prices, slow_period)
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line (EMA of MACD line)
        signal_line = self._ema(macd_line, signal_period)
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line[-1],
            'signal': signal_line[-1],
            'histogram': histogram[-1]
        }
    
    def calculate_bollinger_bands(self, prices: List[float], 
                                 period: int = 20, std_dev: float = 2.0) -> Dict:
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
        
        # Calculate middle band (SMA)
        sma = self._sma(prices, period)
        middle_band = sma[-1]
        
        # Calculate standard deviation
        price_slice = prices[-period:]
        std = np.std(price_slice)
        
        # Calculate upper and lower bands
        upper_band = middle_band + (std_dev * std)
        lower_band = middle_band - (std_dev * std)
        
        current_price = prices[-1]
        
        return {
            'upper': upper_band,
            'middle': middle_band,
            'lower': lower_band,
            'current_price': current_price
        }
    
    def calculate_moving_averages(self, prices: List[float]) -> Dict:
        """
        Calculate various moving averages
        """
        result = {'current_price': prices[-1] if prices else 0}
        
        periods = [5, 10, 20, 50]
        for period in periods:
            if len(prices) >= period:
                ma = self._sma(prices, period)[-1]
                result[f'ma_{period}'] = ma
            else:
                result[f'ma_{period}'] = result['current_price']
        
        return result
    
    def calculate_stochastic(self, highs: List[float], lows: List[float], 
                           closes: List[float], k_period: int = 14, d_period: int = 3) -> Dict:
        """
        Calculate Stochastic Oscillator
        """
        if len(closes) < k_period:
            return {'k': 50.0, 'd': 50.0}
        
        # Calculate %K
        recent_close = closes[-1]
        lowest_low = min(lows[-k_period:])
        highest_high = max(highs[-k_period:])
        
        if highest_high - lowest_low == 0:
            pct_k = 50.0
        else:
            pct_k = (recent_close - lowest_low) / (highest_high - lowest_low) * 100
        
        # Calculate %D (3-period SMA of %K)
        # For simplicity, we'll return the same value for initial implementation
        pct_d = pct_k  # In a full implementation, we'd track multiple %K values
        
        return {
            'k': pct_k,
            'd': pct_d
        }
    
    def calculate_atr(self, highs: List[float], lows: List[float], 
                     closes: List[float], period: int = 14) -> float:
        """
        Calculate Average True Range (ATR)
        """
        if len(closes) < period + 1:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(highs)):
            tr = max(
                highs[i] - lows[i],  # High - Low
                abs(highs[i] - closes[i-1]),  # High - Previous Close
                abs(lows[i] - closes[i-1])   # Low - Previous Close
            )
            true_ranges.append(tr)
        
        # Calculate ATR using simple moving average for simplicity
        if len(true_ranges) >= period:
            atr = np.mean(true_ranges[-period:])
        else:
            atr = np.mean(true_ranges)
        
        return atr
    
    def calculate_volume_indicators(self, volumes: List[float], closes: List[float], 
                                  period: int = 20) -> Dict:
        """
        Calculate volume-based indicators
        """
        if len(volumes) < period:
            return {'obv': 0, 'avg_volume': sum(volumes) / len(volumes) if volumes else 0}
        
        # On Balance Volume (OBV)
        obv = 0
        prev_close = closes[0]
        for i in range(len(closes)):
            if i > 0:
                if closes[i] > prev_close:
                    obv += volumes[i]
                elif closes[i] < prev_close:
                    obv -= volumes[i]
                # If equal, OBV remains unchanged
                prev_close = closes[i]
        
        avg_volume = np.mean(volumes[-period:])
        
        return {
            'obv': obv,
            'avg_volume': avg_volume,
            'volume_ratio': volumes[-1] / avg_volume if avg_volume > 0 else 0
        }
    
    def _ema(self, data: List[float], period: int) -> np.ndarray:
        """
        Calculate Exponential Moving Average
        """
        data_array = np.array(data)
        ema = np.zeros_like(data_array)
        ema[0] = data_array[0]
        
        multiplier = 2 / (period + 1)
        for i in range(1, len(data_array)):
            ema[i] = (data_array[i] * multiplier) + (ema[i-1] * (1 - multiplier))
        
        return ema
    
    def _sma(self, data: List[float], period: int) -> np.ndarray:
        """
        Calculate Simple Moving Average
        """
        data_array = np.array(data)
        sma = np.zeros_like(data_array)
        
        for i in range(len(data_array)):
            if i < period - 1:
                sma[i] = np.mean(data_array[:i+1])
            else:
                sma[i] = np.mean(data_array[i-period+1:i+1])
        
        return sma
    
    def calculate_support_resistance(self, prices: List[float], 
                                   window: int = 20, tolerance: float = 0.02) -> Dict:
        """
        Calculate potential support and resistance levels
        """
        if len(prices) < window * 2:
            current_price = prices[-1] if prices else 0
            return {
                'resistance': current_price,
                'support': current_price,
                'current_price': current_price
            }
        
        # Find local maxima and minima in the given window
        local_maxima = []
        local_minima = []
        
        # Simple method: compare each point with neighbors
        for i in range(window, len(prices) - window):
            window_slice = prices[i-window:i+window+1]
            mid_point = window  # Middle of the slice
            
            if prices[i] == max(window_slice):
                local_maxima.append(prices[i])
            elif prices[i] == min(window_slice):
                local_minima.append(prices[i])
        
        # Get the most recent significant levels
        resistance = np.mean(local_maxima[-3:]) if len(local_maxima) >= 3 else prices[-1]
        support = np.mean(local_minima[-3:]) if len(local_minima) >= 3 else prices[-1]
        
        current_price = prices[-1]
        
        return {
            'resistance': resistance,
            'support': support,
            'current_price': current_price
        }