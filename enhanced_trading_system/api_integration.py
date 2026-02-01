"""
API Integration Module for Enhanced Trading System
Handles connections to Binance API and other data sources
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime

import aiohttp
import pandas as pd
import numpy as np

from binance.client import Client
from binance.exceptions import BinanceAPIException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BinanceAPIIntegration:
    """
    Class to handle integration with Binance API
    """
    
    def __init__(self, api_key: str = None, secret_key: str = None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.client = None
        self.session = None
        
        # Initialize Binance client if credentials provided
        if api_key and secret_key:
            try:
                self.client = Client(api_key, secret_key)
                logger.info("Binance client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Binance client: {e}")
        
        # Create async session
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close the async session"""
        if self.session:
            await self.session.close()
    
    async def get_kline_data(self, symbol: str, interval: str = '5m', limit: int = 100) -> List:
        """
        Get K-line data from Binance
        """
        try:
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            formatted_klines = []
            for kline in klines:
                formatted_klines.append({
                    'open_time': kline[0],
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5]),
                    'close_time': kline[6],
                    'quote_asset_volume': float(kline[7]),
                    'number_of_trades': kline[8],
                    'taker_buy_base_asset_volume': float(kline[9]),
                    'taker_buy_quote_asset_volume': float(kline[10])
                })
            
            return formatted_klines
            
        except Exception as e:
            logger.error(f"Error getting kline data for {symbol}: {e}")
            return []
    
    async def get_order_book(self, symbol: str, limit: int = 100) -> Dict:
        """
        Get order book data from Binance
        """
        try:
            order_book = self.client.get_order_book(symbol=symbol, limit=limit)
            return order_book
        except Exception as e:
            logger.error(f"Error getting order book for {symbol}: {e}")
            return {}
    
    async def get_ticker_price(self, symbol: str) -> Dict:
        """
        Get current ticker price for a symbol
        """
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return ticker
        except Exception as e:
            logger.error(f"Error getting ticker for {symbol}: {e}")
            return {}
    
    async def get_account_info(self) -> Dict:
        """
        Get account information
        """
        try:
            account_info = self.client.get_account()
            return account_info
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return {}
    
    async def get_futures_position_info(self) -> List:
        """
        Get futures position information
        """
        try:
            positions = self.client.futures_position_information()
            return positions
        except Exception as e:
            logger.error(f"Error getting futures position info: {e}")
            return []


class OISpikeRadarIntegration:
    """
    Class to integrate with the existing OI Spike Radar
    """
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close the async session"""
        if self.session:
            await self.session.close()
    
    async def get_latest_signals(self) -> List[Dict]:
        """
        Get the latest OI spike signals from the radar
        """
        try:
            async with self.session.get(f"{self.base_url}/api/status") as resp:
                if resp.status == 200:
                    status_data = await resp.json()
                    
                    # Now get recent alerts from the SQLite database
                    # We'll use the existing Python script approach
                    import sqlite3
                    import json
                    
                    conn = sqlite3.connect('/root/clawd/binance-oi-spike-radar-clone/data/alerts.sqlite3')
                    cursor = conn.cursor()
                    
                    # Get the most recent alerts (last 30 minutes)
                    since_time = time.time() - 1800  # 30 minutes ago
                    cursor.execute('SELECT * FROM alerts WHERE ts > ? ORDER BY ts DESC LIMIT 20', (since_time,))
                    rows = cursor.fetchall()
                    
                    alerts = []
                    for row in rows:
                        payload = json.loads(row[2])
                        alerts.append(payload)
                    
                    conn.close()
                    return alerts
                else:
                    logger.error(f"Failed to get status from OI Spike Radar: {resp.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting OI signals: {e}")
            return []
    
    async def get_radar_status(self) -> Dict:
        """
        Get the status of the OI Spike Radar
        """
        try:
            async with self.session.get(f"{self.base_url}/api/status") as resp:
                if resp.status == 200:
                    status_data = await resp.json()
                    return status_data
                else:
                    logger.error(f"Failed to get status from OI Spike Radar: {resp.status}")
                    return {}
        except Exception as e:
            logger.error(f"Error getting radar status: {e}")
            return {}


class TechnicalIndicatorCalculator:
    """
    Class to calculate various technical indicators
    """
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """
        Calculate RSI (Relative Strength Index)
        """
        if len(prices) < period + 1:
            return 50.0  # Neutral value if not enough data
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Calculate for the rest of the periods
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rsi = 100.0
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        """
        if len(prices) < slow:
            return {'macd': 0, 'signal': 0, 'histogram': 0}
        
        exp1 = pd.Series(prices).ewm(span=fast).mean()
        exp2 = pd.Series(prices).ewm(span=slow).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line.iloc[-1],
            'signal': signal_line.iloc[-1],
            'histogram': histogram.iloc[-1]
        }
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: int = 2) -> Dict:
        """
        Calculate Bollinger Bands
        """
        if len(prices) < period:
            return {'upper': 0, 'middle': 0, 'lower': 0, 'current_price': prices[-1] if prices else 0}
        
        series = pd.Series(prices)
        sma = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'upper': upper_band.iloc[-1],
            'middle': sma.iloc[-1],
            'lower': lower_band.iloc[-1],
            'current_price': prices[-1]
        }
    
    @staticmethod
    def calculate_moving_averages(prices: List[float], periods: List[int] = [5, 10, 20, 50]) -> Dict:
        """
        Calculate multiple moving averages
        """
        series = pd.Series(prices)
        mas = {}
        
        for period in periods:
            if len(prices) >= period:
                ma = series.rolling(window=period).mean().iloc[-1]
                mas[f'ma_{period}'] = ma
            else:
                mas[f'ma_{period}'] = 0
        
        mas['current_price'] = prices[-1] if prices else 0
        return mas


async def main():
    """
    Example usage of the API Integration classes
    """
    # Initialize the integrations
    binance_api = BinanceAPIIntegration()
    oi_radar = OISpikeRadarIntegration()
    indicator_calc = TechnicalIndicatorCalculator()
    
    # Test getting kline data
    symbol = "BTCUSDT"
    klines = await binance_api.get_kline_data(symbol, '5m', 100)
    print(f"Retrieved {len(klines)} klines for {symbol}")
    
    # Calculate indicators from the kline data
    if klines:
        closes = [k['close'] for k in klines]
        
        rsi = indicator_calc.calculate_rsi(closes)
        macd = indicator_calc.calculate_macd(closes)
        bb = indicator_calc.calculate_bollinger_bands(closes)
        mas = indicator_calc.calculate_moving_averages(closes)
        
        print(f"RSI: {rsi}")
        print(f"MACD: {macd}")
        print(f"Bollinger Bands: {bb}")
        print(f"Moving Averages: {mas}")
    
    # Get OI signals
    oi_signals = await oi_radar.get_latest_signals()
    print(f"Retrieved {len(oi_signals)} OI signals")
    
    # Close sessions
    await binance_api.close()
    await oi_radar.close()


if __name__ == "__main__":
    asyncio.run(main())