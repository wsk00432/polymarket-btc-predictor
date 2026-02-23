"""
API Integration Module for Enhanced Trading Analysis System
Handles all external API communications including Binance and other data sources
"""

import asyncio
import aiohttp
import time
import hmac
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from binance.client import Client
from binance.async_client import AsyncClient
from binance.exceptions import BinanceAPIException
from binance.enums import HistoricalKlinesType

from config import get_config, DEFAULT_CONFIG
from utils import safe_float_conversion


class BinanceAPIManager:
    """
    Manager class for Binance API interactions
    Handles authentication, rate limiting, and request management
    """
    
    def __init__(self, api_key: str = None, secret_key: str = None):
        self.api_key = api_key or get_config('BINANCE_API_KEY')
        self.secret_key = secret_key or get_config('BINANCE_SECRET_KEY')
        
        # Initialize synchronous client
        if self.api_key and self.secret_key:
            try:
                self.sync_client = Client(self.api_key, self.secret_key)
                logging.info("Binance synchronous client initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize Binance sync client: {e}")
                self.sync_client = Client()  # Initialize without auth for public endpoints
        else:
            self.sync_client = Client()  # Public endpoints only
            logging.info("Binance client initialized without authentication")
        
        # Initialize asynchronous client
        self.async_client = None
        self.session = None
        
        # Rate limiting
        self.last_request_time = {}
        self.rate_limit_delay = 0.1  # 100ms minimum delay between requests
        
        # API endpoints
        self.base_url = "https://api.binance.com"
        self.futures_url = "https://fapi.binance.com"
        
    async def initialize_async_client(self):
        """Initialize asynchronous Binance client"""
        try:
            self.async_client = await AsyncClient.create(
                api_key=self.api_key if self.api_key else None,
                api_secret=self.secret_key if self.secret_key else None
            )
            logging.info("Binance async client initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Binance async client: {e}")
            # Still create async client without auth for public endpoints
            self.async_client = await AsyncClient.create()
    
    def _check_rate_limit(self, endpoint: str):
        """Check and enforce rate limiting"""
        current_time = time.time()
        if endpoint in self.last_request_time:
            elapsed = current_time - self.last_request_time[endpoint]
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)
        
        self.last_request_time[endpoint] = time.time()
    
    def get_server_time(self) -> Dict:
        """Get server time from Binance"""
        try:
            self._check_rate_limit('/api/v3/time')
            return self.sync_client.get_server_time()
        except BinanceAPIException as e:
            logging.error(f"Error getting server time: {e}")
            return {}
    
    def get_exchange_info(self) -> Dict:
        """Get exchange information"""
        try:
            self._check_rate_limit('/api/v3/exchangeInfo')
            return self.sync_client.get_exchange_info()
        except BinanceAPIException as e:
            logging.error(f"Error getting exchange info: {e}")
            return {}
    
    def get_symbol_ticker(self, symbol: str) -> Dict:
        """Get ticker price for a symbol"""
        try:
            self._check_rate_limit(f'/api/v3/ticker/price?symbol={symbol}')
            return self.sync_client.get_symbol_ticker(symbol=symbol)
        except BinanceAPIException as e:
            logging.error(f"Error getting ticker for {symbol}: {e}")
            return {}
    
    def get_all_tickers(self) -> List[Dict]:
        """Get ticker price for all symbols"""
        try:
            self._check_rate_limit('/api/v3/ticker/price')
            return self.sync_client.get_all_tickers()
        except BinanceAPIException as e:
            logging.error(f"Error getting all tickers: {e}")
            return []
    
    def get_klines(self, symbol: str, interval: str, limit: int = 500) -> List[List]:
        """Get kline/candlestick data"""
        try:
            self._check_rate_limit(f'/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}')
            return self.sync_client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=min(limit, 1000)  # Max limit is 1000
            )
        except BinanceAPIException as e:
            logging.error(f"Error getting klines for {symbol}: {e}")
            return []
    
    async def get_kline_data(self, symbol: str, interval: str, limit: int = 100) -> List[Dict]:
        """Get kline data in a format compatible with the trading system"""
        try:
            # Use the synchronous method but wrap in async
            klines = self.get_klines(symbol, interval, limit)
            # Convert to the expected format
            formatted_klines = []
            for kline in klines:
                formatted_klines.append({
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5]),
                    'timestamp': kline[0]
                })
            return formatted_klines
        except Exception as e:
            logging.error(f"Error getting kline data for {symbol}: {e}")
            return []

    def get_historical_klines(self, symbol: str, interval: str, start_str: str, end_str: str = None) -> List[List]:
        """Get historical kline data"""
        try:
            return self.sync_client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_str,
                end_str=end_str,
                limit=1000
            )
        except BinanceAPIException as e:
            logging.error(f"Error getting historical klines for {symbol}: {e}")
            return []
    
    def get_order_book(self, symbol: str, limit: int = 100) -> Dict:
        """Get order book for a symbol"""
        try:
            self._check_rate_limit(f'/api/v3/depth?symbol={symbol}&limit={limit}')
            return self.sync_client.get_order_book(
                symbol=symbol,
                limit=min(limit, 5000)  # Max limit is 5000
            )
        except BinanceAPIException as e:
            logging.error(f"Error getting order book for {symbol}: {e}")
            return {}

    async def get_order_book_async(self, symbol: str, limit: int = 100) -> Dict:
        """Async version of get_order_book for the trading system"""
        try:
            return self.get_order_book(symbol, limit)
        except Exception as e:
            logging.error(f"Error getting order book for {symbol}: {e}")
            return {}
    
    def get_aggregate_trades(self, symbol: str, limit: int = 500) -> List[Dict]:
        """Get aggregate trades for a symbol"""
        try:
            self._check_rate_limit(f'/api/v3/aggTrades?symbol={symbol}&limit={min(limit, 1000)}')
            return self.sync_client.get_aggregate_trades(
                symbol=symbol,
                limit=min(limit, 1000)
            )
        except BinanceAPIException as e:
            logging.error(f"Error getting aggregate trades for {symbol}: {e}")
            return []
    
    def get_24hr_ticker(self, symbol: str) -> Dict:
        """Get 24 hour price change statistics"""
        try:
            self._check_rate_limit(f'/api/v3/ticker/24hr?symbol={symbol}')
            return self.sync_client.get_ticker(symbol=symbol)
        except BinanceAPIException as e:
            logging.error(f"Error getting 24hr ticker for {symbol}: {e}")
            return {}
    
    # Futures-related methods
    def get_futures_klines(self, symbol: str, interval: str, limit: int = 500) -> List[List]:
        """Get futures kline/candlestick data"""
        try:
            # Using the underlying client for futures endpoint
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': min(limit, 1000)
            }
            return self.sync_client.futures_klines(**params)
        except BinanceAPIException as e:
            logging.error(f"Error getting futures klines for {symbol}: {e}")
            return []
    
    def get_open_interest(self, symbol: str) -> Dict:
        """Get open interest for a futures symbol"""
        try:
            # This would require direct HTTP request since python-binance doesn't have this method
            import requests
            url = f"{self.futures_url}/fapi/v1/openInterest"
            params = {'symbol': symbol}
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            logging.error(f"Error getting open interest for {symbol}: {e}")
            return {}
    
    def get_futures_ticker(self, symbol: str) -> Dict:
        """Get futures ticker for a symbol"""
        try:
            return self.sync_client.futures_ticker(symbol=symbol)
        except BinanceAPIException as e:
            logging.error(f"Error getting futures ticker for {symbol}: {e}")
            return {}


class APIIntegrationManager:
    """
    Main integration manager that coordinates all API communications
    """
    
    def __init__(self):
        self.binance_manager = BinanceAPIManager()
        self.logger = logging.getLogger(__name__)
        self._initialized = False
    
    async def initialize(self):
        """Initialize all API managers"""
        if not self._initialized:
            await self.binance_manager.initialize_async_client()
            self._initialized = True
            self.logger.info("API Integration Manager initialized")
    
    async def get_market_data(self, symbol: str, include_klines: bool = True, kline_limit: int = 100) -> Dict:
        """Get comprehensive market data for a symbol"""
        await self.initialize()
        
        data = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'price': None,
            'ticker_24h': {},
            'order_book': {},
            'klines': [],
            'aggregate_trades': []
        }
        
        try:
            # Get current price
            ticker = self.binance_manager.get_symbol_ticker(symbol)
            if ticker:
                data['price'] = safe_float_conversion(ticker.get('price', 0))
            
            # Get 24h ticker
            ticker_24h = self.binance_manager.get_24hr_ticker(symbol)
            if ticker_24h:
                data['ticker_24h'] = ticker_24h
            
            # Get order book
            order_book = self.binance_manager.get_order_book(symbol)
            if order_book:
                data['order_book'] = order_book
            
            # Get klines if requested
            if include_klines:
                klines = self.binance_manager.get_klines(
                    symbol, 
                    get_config('KLINE_INTERVAL', '5m'), 
                    kline_limit
                )
                if klines:
                    data['klines'] = klines
            
            # Get aggregate trades
            trades = self.binance_manager.get_aggregate_trades(symbol, 100)
            if trades:
                data['aggregate_trades'] = trades
                
        except Exception as e:
            self.logger.error(f"Error getting market data for {symbol}: {e}")
        
        return data
    
    async def get_multiple_symbols_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get market data for multiple symbols concurrently"""
        await self.initialize()
        
        tasks = []
        for symbol in symbols:
            task = asyncio.create_task(self.get_market_data(symbol))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        data = {}
        for i, symbol in enumerate(symbols):
            result = results[i]
            if isinstance(result, Exception):
                self.logger.error(f"Error getting data for {symbol}: {result}")
                data[symbol] = {}
            else:
                data[symbol] = result
        
        return data
    
    async def get_technical_data(self, symbol: str, interval: str = None, limit: int = None) -> Dict:
        """Get data specifically for technical analysis"""
        await self.initialize()
        
        if interval is None:
            interval = get_config('KLINE_INTERVAL', '5m')
        if limit is None:
            limit = get_config('KLINE_LIMIT', 100)
        
        # Get klines for technical analysis
        klines = self.binance_manager.get_klines(symbol, interval, limit)
        
        # Get order book for depth analysis
        order_book = self.binance_manager.get_order_book(symbol, get_config('ORDER_BOOK_LIMIT', 100))
        
        # Get aggregate trades for flow analysis
        trades = self.binance_manager.get_aggregate_trades(symbol, limit)
        
        # Get current price
        ticker = self.binance_manager.get_symbol_ticker(symbol)
        current_price = safe_float_conversion(ticker.get('price', 0)) if ticker else 0
        
        technical_data = {
            'symbol': symbol,
            'interval': interval,
            'current_price': current_price,
            'klines': klines,
            'order_book': order_book,
            'trades': trades,
            'timestamp': datetime.now()
        }
        
        return technical_data
    
    async def get_futures_data(self, symbol: str) -> Dict:
        """Get futures-specific data including open interest"""
        await self.initialize()
        
        futures_data = {
            'symbol': symbol,
            'futures_ticker': {},
            'futures_klines': [],
            'open_interest': {},
            'timestamp': datetime.now()
        }
        
        try:
            # Get futures ticker
            futures_ticker = self.binance_manager.get_futures_ticker(symbol)
            if futures_ticker:
                futures_data['futures_ticker'] = futures_ticker
            
            # Get futures klines
            futures_klines = self.binance_manager.get_futures_klines(
                symbol, 
                get_config('KLINE_INTERVAL', '5m'),
                get_config('KLINE_LIMIT', 100)
            )
            if futures_klines:
                futures_data['futures_klines'] = futures_klines
            
            # Get open interest
            open_interest = self.binance_manager.get_open_interest(symbol)
            if open_interest:
                futures_data['open_interest'] = open_interest
                
        except Exception as e:
            self.logger.error(f"Error getting futures data for {symbol}: {e}")
        
        return futures_data
    
    async def get_funding_rate(self, symbol: str) -> Dict:
        """Get funding rate for futures symbol"""
        await self.initialize()
        
        try:
            import requests
            url = f"{self.binance_manager.futures_url}/fapi/v1/fundingRate"
            params = {'symbol': symbol}
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            self.logger.error(f"Error getting funding rate for {symbol}: {e}")
            return {}
    
    def get_exchange_status(self) -> bool:
        """Check if exchange is accessible"""
        try:
            server_time = self.binance_manager.get_server_time()
            return 'serverTime' in server_time
        except:
            return False
    
    async def close(self):
        """Clean up resources"""
        if hasattr(self.binance_manager, 'async_client') and self.binance_manager.async_client:
            await self.binance_manager.async_client.close_connection()


class APIDataCache:
    """
    Cache for API data to reduce redundant requests and improve performance
    """
    
    def __init__(self, ttl_seconds: int = 30):
        self.cache = {}
        self.ttl = ttl_seconds
        self.logger = logging.getLogger(__name__)
    
    def _is_expired(self, timestamp: datetime) -> bool:
        """Check if cached data has expired"""
        return (datetime.now() - timestamp).seconds > self.ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get data from cache if not expired"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if not self._is_expired(timestamp):
                return data
            else:
                # Remove expired data
                del self.cache[key]
        return None
    
    def set(self, key: str, data: Any):
        """Set data in cache with timestamp"""
        self.cache[key] = (data, datetime.now())
        self.logger.debug(f"Cached data for key: {key}")
    
    def invalidate(self, key: str = None):
        """Invalidate specific key or all cache"""
        if key and key in self.cache:
            del self.cache[key]
            self.logger.debug(f"Invalidated cache for key: {key}")
        elif key is None:
            self.cache.clear()
            self.logger.debug("Cleared entire cache")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        active_items = 0
        expired_items = 0
        
        for key, (data, timestamp) in self.cache.items():
            if self._is_expired(timestamp):
                expired_items += 1
            else:
                active_items += 1
        
        return {
            'total_items': len(self.cache),
            'active_items': active_items,
            'expired_items': expired_items
        }


# Global instances
api_manager = None
data_cache = None


async def get_api_manager() -> APIIntegrationManager:
    """Get or create the global API manager instance"""
    global api_manager
    if api_manager is None:
        api_manager = APIIntegrationManager()
        await api_manager.initialize()
    return api_manager


def get_data_cache(ttl_seconds: int = 30) -> APIDataCache:
    """Get or create the global data cache instance"""
    global data_cache
    if data_cache is None:
        data_cache = APIDataCache(ttl_seconds)
    return data_cache


# Convenience functions
async def get_symbol_data(symbol: str) -> Dict:
    """Convenience function to get data for a single symbol"""
    manager = await get_api_manager()
    cache = get_data_cache()
    
    # Try to get from cache first
    cache_key = f"symbol_data_{symbol}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # Fetch fresh data
    data = await manager.get_market_data(symbol)
    
    # Cache the result
    cache.set(cache_key, data)
    
    return data


async def get_multiple_symbols_data_cached(symbols: List[str]) -> Dict[str, Dict]:
    """Convenience function to get data for multiple symbols with caching"""
    manager = await get_api_manager()
    cache = get_data_cache()
    
    results = {}
    
    # Check cache for each symbol
    uncached_symbols = []
    for symbol in symbols:
        cache_key = f"symbol_data_{symbol}"
        cached_data = cache.get(cache_key)
        if cached_data:
            results[symbol] = cached_data
        else:
            uncached_symbols.append(symbol)
    
    # Fetch uncached data
    if uncached_symbols:
        fresh_data = await manager.get_multiple_symbols_data(uncached_symbols)
        
        # Cache fresh data and add to results
        for symbol, data in fresh_data.items():
            cache_key = f"symbol_data_{symbol}"
            cache.set(cache_key, data)
            results[symbol] = data
    
    return results


async def get_technical_data_cached(symbol: str, interval: str = None, limit: int = None) -> Dict:
    """Convenience function to get technical data with caching"""
    manager = await get_api_manager()
    cache = get_data_cache(ttl_seconds=15)  # Shorter TTL for technical data
    
    cache_key = f"tech_data_{symbol}_{interval or get_config('KLINE_INTERVAL')}_{limit or get_config('KLINE_LIMIT')}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # Fetch fresh data
    data = await manager.get_technical_data(symbol, interval, limit)
    
    # Cache the result
    cache.set(cache_key, data)
    
    return data


async def cleanup_api_resources():
    """Cleanup function to close API connections"""
    global api_manager
    if api_manager:
        await api_manager.close()
        api_manager = None