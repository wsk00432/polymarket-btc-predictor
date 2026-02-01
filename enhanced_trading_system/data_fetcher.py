"""
Data fetcher module for the Enhanced Trading Analysis System
Handles communication with exchanges and data providers
"""

import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd

from .models import KlineData, OrderBookDepth, FundFlow, OISignal
from .config import get_config
from .utils import safe_float_conversion


class DataFetcher:
    """
    Class responsible for fetching data from various sources
    """
    
    def __init__(self, api_key: str = None, secret_key: str = None):
        self.api_key = api_key or get_config('BINANCE_API_KEY')
        self.secret_key = secret_key or get_config('BINANCE_SECRET_KEY')
        
        # Initialize Binance client
        if self.api_key and self.secret_key:
            try:
                self.binance_client = Client(self.api_key, self.secret_key)
                print("Binance client initialized successfully")
            except Exception as e:
                print(f"Failed to initialize Binance client: {e}")
                self.binance_client = None
        else:
            print("No API keys provided, initializing without authentication")
            self.binance_client = Client()
    
    async def fetch_kline_data(self, symbol: str, interval: str = None, limit: int = None) -> List[KlineData]:
        """
        Fetch K-line data from Binance
        """
        interval = interval or get_config('KLINE_INTERVAL')
        limit = limit or get_config('KLINE_LIMIT')
        
        try:
            klines = self.binance_client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            kline_objects = []
            for kline in klines:
                kline_obj = KlineData(
                    symbol=symbol,
                    open_time=kline[0],
                    open=safe_float_conversion(kline[1]),
                    high=safe_float_conversion(kline[2]),
                    low=safe_float_conversion(kline[3]),
                    close=safe_float_conversion(kline[4]),
                    volume=safe_float_conversion(kline[5]),
                    close_time=kline[6],
                    quote_asset_volume=safe_float_conversion(kline[7]),
                    number_of_trades=kline[8],
                    taker_buy_base_asset_volume=safe_float_conversion(kline[9]),
                    taker_buy_quote_asset_volume=safe_float_conversion(kline[10])
                )
                kline_objects.append(kline_obj)
            
            return kline_objects
            
        except BinanceAPIException as e:
            print(f"Error fetching kline data for {symbol}: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error fetching kline data for {symbol}: {e}")
            return []
    
    async def fetch_order_book_depth(self, symbol: str, limit: int = None) -> Optional[OrderBookDepth]:
        """
        Fetch order book depth data from Binance
        """
        limit = limit or get_config('ORDER_BOOK_LIMIT')
        
        try:
            order_book = self.binance_client.get_order_book(symbol=symbol, limit=limit)
            
            # Process bids and asks
            bids = [(safe_float_conversion(price), safe_float_conversion(qty)) for price, qty in order_book['bids']]
            asks = [(safe_float_conversion(price), safe_float_conversion(qty)) for price, qty in order_book['asks']]
            
            # Calculate cumulative volumes
            bid_cumulative = [qty for _, qty in bids]
            ask_cumulative = [qty for _, qty in asks]
            
            # Calculate running sums
            for i in range(1, len(bid_cumulative)):
                bid_cumulative[i] += bid_cumulative[i-1]
            for i in range(1, len(ask_cumulative)):
                ask_cumulative[i] += ask_cumulative[i-1]
            
            depth_data = OrderBookDepth(
                symbol=symbol,
                timestamp=datetime.now(),
                bids=[{'price': price, 'quantity': qty} for price, qty in bids[:20]],
                asks=[{'price': price, 'quantity': qty} for price, qty in asks[:20]],
                bid_volume=sum([qty for _, qty in bids]),
                ask_volume=sum([qty for _, qty in asks]),
                bid_cumulative=bid_cumulative[:20],
                ask_cumulative=ask_cumulative[:20],
                spread=(asks[0][0] - bids[0][0]) if bids and asks else 0,
                spread_percentage=((asks[0][0] - bids[0][0]) / bids[0][0] * 100) if bids and asks else 0
            )
            
            return depth_data
            
        except BinanceAPIException as e:
            print(f"Error fetching order book depth for {symbol}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error fetching order book depth for {symbol}: {e}")
            return None
    
    async def fetch_current_price(self, symbol: str) -> float:
        """
        Fetch current price for a symbol
        """
        try:
            ticker = self.binance_client.get_symbol_ticker(symbol=symbol)
            return safe_float_conversion(ticker['price'])
        except BinanceAPIException as e:
            print(f"Error fetching current price for {symbol}: {e}")
            return 0.0
        except Exception as e:
            print(f"Unexpected error fetching current price for {symbol}: {e}")
            return 0.0
    
    async def fetch_24h_ticker(self, symbol: str) -> Dict:
        """
        Fetch 24-hour ticker statistics
        """
        try:
            ticker = self.binance_client.get_ticker(symbol=symbol)
            return ticker
        except BinanceAPIException as e:
            print(f"Error fetching 24h ticker for {symbol}: {e}")
            return {}
        except Exception as e:
            print(f"Unexpected error fetching 24h ticker for {symbol}: {e}")
            return {}
    
    async def fetch_fund_flow(self, symbol: str, limit: int = 100) -> Optional[FundFlow]:
        """
        Analyze fund flow based on recent trades
        """
        try:
            # Get recent aggregate trades
            trades = self.binance_client.get_aggregate_trades(
                symbol=symbol,
                limit=limit
            )
            
            buy_volume = 0
            sell_volume = 0
            buy_count = 0
            sell_count = 0
            
            for trade in trades:
                # 'm' indicates whether buyer is maker (True) or seller is maker (False)
                # When 'm' is True, it means a buy order was matched against existing sell orders (selling pressure)
                # When 'm' is False, it means a sell order was matched against existing buy orders (buying pressure)
                if trade['m']:  # Seller is maker (buying pressure)
                    buy_volume += safe_float_conversion(trade['q'])
                    buy_count += 1
                else:  # Buyer is maker (selling pressure)
                    sell_volume += safe_float_conversion(trade['q'])
                    sell_count += 1
            
            total_volume = buy_volume + sell_volume
            buy_ratio = buy_volume / total_volume if total_volume > 0 else 0
            sell_ratio = sell_volume / total_volume if total_volume > 0 else 0
            
            from .models import SignalDirection
            flow_direction = SignalDirection.BULLISH if buy_ratio > sell_ratio else SignalDirection.BEARISH
            
            fund_flow = FundFlow(
                symbol=symbol,
                timestamp=datetime.now(),
                buy_volume=buy_volume,
                sell_volume=sell_volume,
                total_volume=total_volume,
                buy_ratio=buy_ratio,
                sell_ratio=sell_ratio,
                net_flow=buy_volume - sell_volume,
                buy_trade_count=buy_count,
                sell_trade_count=sell_count,
                flow_direction=flow_direction
            )
            
            return fund_flow
            
        except BinanceAPIException as e:
            print(f"Error analyzing fund flow for {symbol}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error analyzing fund flow for {symbol}: {e}")
            return None
    
    async def fetch_multiple_symbols_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Fetch data for multiple symbols concurrently
        """
        tasks = []
        for symbol in symbols:
            task = asyncio.create_task(self.fetch_symbol_data(symbol))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        data = {}
        for i, symbol in enumerate(symbols):
            result = results[i]
            if isinstance(result, Exception):
                print(f"Error fetching data for {symbol}: {result}")
                data[symbol] = {}
            else:
                data[symbol] = result
        
        return data
    
    async def fetch_symbol_data(self, symbol: str) -> Dict:
        """
        Fetch comprehensive data for a single symbol
        """
        # Run multiple fetch operations concurrently for this symbol
        klines_task = self.fetch_kline_data(symbol)
        order_book_task = self.fetch_order_book_depth(symbol)
        fund_flow_task = self.fetch_fund_flow(symbol)
        price_task = self.fetch_current_price(symbol)
        ticker_task = self.fetch_24h_ticker(symbol)
        
        klines, order_book, fund_flow, price, ticker = await asyncio.gather(
            klines_task, order_book_task, fund_flow_task, price_task, ticker_task,
            return_exceptions=True
        )
        
        data = {
            'symbol': symbol,
            'klines': klines if not isinstance(klines, Exception) else [],
            'order_book': order_book if not isinstance(order_book, Exception) else None,
            'fund_flow': fund_flow if not isinstance(fund_flow, Exception) else None,
            'current_price': price if not isinstance(price, Exception) else 0.0,
            'ticker_24h': ticker if not isinstance(ticker, Exception) else {},
            'timestamp': datetime.now()
        }
        
        return data
    
    async def fetch_historical_klines(self, symbol: str, interval: str, start_str: str, end_str: str = None) -> List[KlineData]:
        """
        Fetch historical klines for backtesting
        """
        try:
            klines = self.binance_client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_str,
                end_str=end_str
            )
            
            kline_objects = []
            for kline in klines:
                kline_obj = KlineData(
                    symbol=symbol,
                    open_time=kline[0],
                    open=safe_float_conversion(kline[1]),
                    high=safe_float_conversion(kline[2]),
                    low=safe_float_conversion(kline[3]),
                    close=safe_float_conversion(kline[4]),
                    volume=safe_float_conversion(kline[5]),
                    close_time=kline[6],
                    quote_asset_volume=safe_float_conversion(kline[7]),
                    number_of_trades=kline[8],
                    taker_buy_base_asset_volume=safe_float_conversion(kline[9]),
                    taker_buy_quote_asset_volume=safe_float_conversion(kline[10])
                )
                kline_objects.append(kline_obj)
            
            return kline_objects
            
        except BinanceAPIException as e:
            print(f"Error fetching historical klines for {symbol}: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error fetching historical klines for {symbol}: {e}")
            return []
    
    async def fetch_exchange_info(self) -> Dict:
        """
        Fetch exchange information
        """
        try:
            info = self.binance_client.get_exchange_info()
            return info
        except BinanceAPIException as e:
            print(f"Error fetching exchange info: {e}")
            return {}
        except Exception as e:
            print(f"Unexpected error fetching exchange info: {e}")
            return {}
    
    async def fetch_account_info(self) -> Dict:
        """
        Fetch account information (requires valid API keys)
        """
        if not self.api_key or not self.secret_key:
            print("Account info requires valid API keys")
            return {}
        
        try:
            account = self.binance_client.get_account()
            return account
        except BinanceAPIException as e:
            print(f"Error fetching account info: {e}")
            return {}
        except Exception as e:
            print(f"Unexpected error fetching account info: {e}")
            return {}
    
    async def fetch_oi_data(self, symbol: str) -> Optional[OISignal]:
        """
        Fetch Open Interest data (placeholder - would connect to futures data source)
        This is a placeholder implementation since Binance API doesn't directly provide OI
        In a real implementation, this would connect to a futures data provider
        """
        # This is a simulated OI signal - in reality, you would get this from a futures exchange API
        # or calculate it from futures data
        
        # For demonstration purposes, return a mock OI signal
        from .models import SignalDirection
        
        # In a real implementation, you would fetch actual OI data here
        # This is just a placeholder showing the structure
        oi_signal = OISignal(
            symbol=symbol,
            timestamp=datetime.now(),
            magnitude=0.0,  # Would come from actual OI data
            direction=SignalDirection.NEUTRAL,  # Would be determined from OI changes
            source="simulated"  # Indicates this is simulated data
        )
        
        return oi_signal
    
    async def fetch_multiple_oi_data(self, symbols: List[str]) -> Dict[str, OISignal]:
        """
        Fetch OI data for multiple symbols
        """
        tasks = []
        for symbol in symbols:
            task = asyncio.create_task(self.fetch_oi_data(symbol))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        oi_data = {}
        for i, symbol in enumerate(symbols):
            result = results[i]
            if not isinstance(result, Exception):
                oi_data[symbol] = result
            else:
                print(f"Error fetching OI data for {symbol}: {result}")
        
        return oi_data
    
    def close(self):
        """
        Close connections
        """
        if hasattr(self, 'binance_client'):
            # Binance client doesn't have a close method, but we could implement cleanup here
            pass


class MockDataFetcher(DataFetcher):
    """
    Mock data fetcher for testing without real API calls
    """
    
    def __init__(self):
        # Don't initialize the real client
        self.api_key = None
        self.secret_key = None
        print("Initialized MockDataFetcher for testing")
    
    async def fetch_kline_data(self, symbol: str, interval: str = None, limit: int = None) -> List[KlineData]:
        """
        Generate mock K-line data
        """
        import random
        
        interval = interval or get_config('KLINE_INTERVAL')
        limit = limit or get_config('KLINE_LIMIT')
        
        # Generate mock data
        kline_objects = []
        base_price = 30000 + random.uniform(-5000, 5000)  # Base around $30k
        
        for i in range(limit):
            # Create somewhat realistic price movements
            open_price = base_price + random.uniform(-100, 100)
            high = open_price + random.uniform(0, 50)
            low = open_price - random.uniform(0, 50)
            close = low + random.uniform(0, high - low)
            volume = random.uniform(100, 1000)
            
            kline_obj = KlineData(
                symbol=symbol,
                open_time=int((datetime.now() - timedelta(minutes=i)).timestamp() * 1000),
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=volume,
                close_time=int((datetime.now() - timedelta(minutes=i)).timestamp() * 1000 + 59999),
                quote_asset_volume=volume * close,
                number_of_trades=random.randint(50, 500),
                taker_buy_base_asset_volume=volume * 0.5,
                taker_buy_quote_asset_volume=volume * close * 0.5
            )
            kline_objects.append(kline_obj)
        
        return kline_objects
    
    async def fetch_order_book_depth(self, symbol: str, limit: int = None) -> Optional[OrderBookDepth]:
        """
        Generate mock order book depth data
        """
        import random
        
        limit = limit or get_config('ORDER_BOOK_LIMIT')
        
        # Generate mock order book
        current_price = 30000 + random.uniform(-1000, 1000)
        
        bids = []
        asks = []
        
        bid_total = 0
        ask_total = 0
        
        bid_cumulative = []
        ask_cumulative = []
        
        for i in range(20):
            bid_price = current_price - (i + 1) * 5
            bid_qty = random.uniform(1, 10)
            bid_total += bid_qty
            bid_cumulative.append(bid_total)
            
            ask_price = current_price + (i + 1) * 5
            ask_qty = random.uniform(1, 10)
            ask_total += ask_qty
            ask_cumulative.append(ask_total)
            
            bids.append({'price': bid_price, 'quantity': bid_qty})
            asks.append({'price': ask_price, 'quantity': ask_qty})
        
        depth_data = OrderBookDepth(
            symbol=symbol,
            timestamp=datetime.now(),
            bids=bids,
            asks=asks,
            bid_volume=bid_total,
            ask_volume=ask_total,
            bid_cumulative=bid_cumulative,
            ask_cumulative=ask_cumulative,
            spread=10.0,  # 5 * 2 levels
            spread_percentage=(10.0 / current_price) * 100
        )
        
        return depth_data
    
    async def fetch_current_price(self, symbol: str) -> float:
        """
        Generate mock current price
        """
        import random
        return 30000 + random.uniform(-1000, 1000)
    
    async def fetch_fund_flow(self, symbol: str, limit: int = 100) -> Optional[FundFlow]:
        """
        Generate mock fund flow data
        """
        import random
        from .models import SignalDirection
        
        buy_volume = random.uniform(1000, 5000)
        sell_volume = random.uniform(1000, 5000)
        total_volume = buy_volume + sell_volume
        
        buy_ratio = buy_volume / total_volume
        sell_ratio = sell_volume / total_volume
        
        flow_direction = SignalDirection.BULLISH if buy_ratio > sell_ratio else SignalDirection.BEARISH
        
        fund_flow = FundFlow(
            symbol=symbol,
            timestamp=datetime.now(),
            buy_volume=buy_volume,
            sell_volume=sell_volume,
            total_volume=total_volume,
            buy_ratio=buy_ratio,
            sell_ratio=sell_ratio,
            net_flow=buy_volume - sell_volume,
            buy_trade_count=random.randint(50, 200),
            sell_trade_count=random.randint(50, 200),
            flow_direction=flow_direction
        )
        
        return fund_flow
    
    async def fetch_oi_data(self, symbol: str) -> Optional[OISignal]:
        """
        Generate mock OI data
        """
        import random
        from .models import SignalDirection
        
        # Simulate OI change
        magnitude = random.uniform(0, 20)  # 0-20% change
        direction = SignalDirection.BULLISH if random.random() > 0.5 else SignalDirection.BEARISH
        
        oi_signal = OISignal(
            symbol=symbol,
            timestamp=datetime.now(),
            magnitude=magnitude,
            direction=direction,
            source="mock"
        )
        
        return oi_signal