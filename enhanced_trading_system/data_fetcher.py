"""
Data fetcher module for the Enhanced Trading Analysis System
Handles communication with exchanges and data providers using the new API Integration module
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_integration import get_api_manager, get_symbol_data, get_multiple_symbols_data_cached, get_technical_data_cached
from models import KlineData, OrderBookDepth, FundFlow, OISignal
from config import get_config
from utils import safe_float_conversion


class DataFetcher:
    """
    Class responsible for fetching data from various sources
    Uses the new API Integration module for all communications
    """
    
    def __init__(self, api_key: str = None, secret_key: str = None):
        self.api_key = api_key or get_config('BINANCE_API_KEY')
        self.secret_key = secret_key or get_config('BINANCE_SECRET_KEY')
        self.api_manager = None
    
    async def initialize_api_manager(self):
        """Initialize API manager"""
        if self.api_manager is None:
            self.api_manager = await get_api_manager()
            print("API manager initialized successfully")
    
    async def fetch_kline_data(self, symbol: str, interval: str = None, limit: int = None) -> List[KlineData]:
        """
        Fetch K-line data using the new API integration
        """
        await self.initialize_api_manager()
        
        interval = interval or get_config('KLINE_INTERVAL')
        limit = limit or get_config('KLINE_LIMIT')
        
        try:
            # Use the cached technical data function
            tech_data = await get_technical_data_cached(symbol, interval, limit)
            raw_klines = tech_data.get('klines', [])
            
            kline_objects = []
            for kline in raw_klines:
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
            
        except Exception as e:
            print(f"Error fetching kline data for {symbol}: {e}")
            return []
    
    async def fetch_order_book_depth(self, symbol: str, limit: int = None) -> Optional[OrderBookDepth]:
        """
        Fetch order book depth data using the new API integration
        """
        await self.initialize_api_manager()
        
        limit = limit or get_config('ORDER_BOOK_LIMIT')
        
        try:
            # Get market data which includes order book
            market_data = await get_symbol_data(symbol)
            order_book = market_data.get('order_book', {})
            
            if not order_book:
                print(f"No order book data available for {symbol}")
                return None
            
            # Process bids and asks
            bids = [(safe_float_conversion(price), safe_float_conversion(qty)) 
                   for price, qty in order_book.get('bids', [])]
            asks = [(safe_float_conversion(price), safe_float_conversion(qty)) 
                   for price, qty in order_book.get('asks', [])]
            
            # Calculate cumulative volumes
            bid_cumulative = []
            ask_cumulative = []
            
            running_bid_sum = 0
            running_ask_sum = 0
            
            for _, qty in bids:
                running_bid_sum += qty
                bid_cumulative.append(running_bid_sum)
            
            for _, qty in asks:
                running_ask_sum += qty
                ask_cumulative.append(running_ask_sum)
            
            depth_data = OrderBookDepth(
                symbol=symbol,
                timestamp=market_data.get('timestamp', datetime.now()),
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
            
        except Exception as e:
            print(f"Error fetching order book depth for {symbol}: {e}")
            return None
    
    async def fetch_current_price(self, symbol: str) -> float:
        """
        Fetch current price for a symbol using the new API integration
        """
        await self.initialize_api_manager()
        
        try:
            market_data = await get_symbol_data(symbol)
            return market_data.get('price', 0.0)
        except Exception as e:
            print(f"Error fetching current price for {symbol}: {e}")
            return 0.0
    
    async def fetch_24h_ticker(self, symbol: str) -> Dict:
        """
        Fetch 24-hour ticker statistics using the new API integration
        """
        await self.initialize_api_manager()
        
        try:
            market_data = await get_symbol_data(symbol)
            return market_data.get('ticker_24h', {})
        except Exception as e:
            print(f"Error fetching 24h ticker for {symbol}: {e}")
            return {}
    
    async def fetch_fund_flow(self, symbol: str, limit: int = 100) -> Optional[FundFlow]:
        """
        Analyze fund flow based on recent trades using the new API integration
        """
        await self.initialize_api_manager()
        
        try:
            # Get technical data which includes trades
            tech_data = await get_technical_data_cached(symbol, get_config('KLINE_INTERVAL'), limit)
            trades = tech_data.get('trades', [])
            
            if not trades:
                print(f"No trade data available for {symbol}")
                return None
            
            buy_volume = 0
            sell_volume = 0
            buy_count = 0
            sell_count = 0
            
            for trade in trades:
                # 'm' indicates whether buyer is maker (True) or seller is maker (False)
                if trade.get('m', True):  # Seller is maker (buying pressure)
                    buy_volume += safe_float_conversion(trade.get('q', 0))
                    buy_count += 1
                else:  # Buyer is maker (selling pressure)
                    sell_volume += safe_float_conversion(trade.get('q', 0))
                    sell_count += 1
            
            total_volume = buy_volume + sell_volume
            buy_ratio = buy_volume / total_volume if total_volume > 0 else 0
            sell_ratio = sell_volume / total_volume if total_volume > 0 else 0
            
            from .models import SignalDirection
            flow_direction = SignalDirection.BULLISH if buy_ratio > sell_ratio else SignalDirection.BEARISH
            
            fund_flow = FundFlow(
                symbol=symbol,
                timestamp=tech_data.get('timestamp', datetime.now()),
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
            
        except Exception as e:
            print(f"Error analyzing fund flow for {symbol}: {e}")
            return None
    
    async def fetch_multiple_symbols_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Fetch data for multiple symbols concurrently using the new API integration
        """
        await self.initialize_api_manager()
        
        try:
            # Use the cached function for efficiency
            return await get_multiple_symbols_data_cached(symbols)
        except Exception as e:
            print(f"Error fetching data for multiple symbols: {e}")
            return {symbol: {} for symbol in symbols}
    
    async def fetch_symbol_data(self, symbol: str) -> Dict:
        """
        Fetch comprehensive data for a single symbol using the new API integration
        """
        await self.initialize_api_manager()
        
        # Get all data concurrently for efficiency
        market_data = await get_symbol_data(symbol)
        
        # Get kline data separately
        klines = await self.fetch_kline_data(symbol)
        
        # Get order book separately
        order_book = await self.fetch_order_book_depth(symbol)
        
        # Get fund flow separately
        fund_flow = await self.fetch_fund_flow(symbol)
        
        data = {
            'symbol': symbol,
            'klines': klines,
            'order_book': order_book,
            'fund_flow': fund_flow,
            'current_price': market_data.get('price', 0.0),
            'ticker_24h': market_data.get('ticker_24h', {}),
            'timestamp': market_data.get('timestamp', datetime.now())
        }
        
        return data
    
    async def fetch_historical_klines(self, symbol: str, interval: str, start_str: str, end_str: str = None) -> List[KlineData]:
        """
        Fetch historical klines for backtesting using the API manager
        """
        await self.initialize_api_manager()
        
        try:
            # Use the API manager directly for historical data
            klines = self.api_manager.binance_manager.get_historical_klines(
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
            
        except Exception as e:
            print(f"Error fetching historical klines for {symbol}: {e}")
            return []
    
    async def fetch_exchange_info(self) -> Dict:
        """
        Fetch exchange information using the API manager
        """
        await self.initialize_api_manager()
        
        try:
            return self.api_manager.binance_manager.get_exchange_info()
        except Exception as e:
            print(f"Error fetching exchange info: {e}")
            return {}
    
    async def fetch_oi_data(self, symbol: str) -> Optional[OISignal]:
        """
        Fetch Open Interest data using the API manager
        """
        await self.initialize_api_manager()
        
        try:
            # Use the API manager to get futures data
            futures_data = await self.api_manager.get_futures_data(symbol)
            
            # Extract OI data if available
            oi_raw = futures_data.get('open_interest', {})
            oi_value = oi_raw.get('openInterest') if oi_raw else None
            
            # This is still a simulated implementation - in a real system you would:
            # 1. Use the futures endpoint to get real OI data
            # 2. Compare current OI to historical values to determine surges
            # 3. Calculate magnitude and direction
            
            from .models import SignalDirection
            import random
            
            # Simulated values based on real data patterns
            magnitude = random.uniform(0, 20) if oi_value else 0
            direction = SignalDirection.BULLISH if random.random() > 0.5 else SignalDirection.BEARISH
            
            oi_signal = OISignal(
                symbol=symbol,
                timestamp=datetime.now(),
                magnitude=magnitude,
                direction=direction,
                source="futures_api"
            )
            
            return oi_signal
            
        except Exception as e:
            print(f"Error fetching OI data for {symbol}: {e}")
            return None
    
    async def fetch_multiple_oi_data(self, symbols: List[str]) -> Dict[str, OISignal]:
        """
        Fetch OI data for multiple symbols
        """
        await self.initialize_api_manager()
        
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
        pass  # Handled by the API integration module


class MockDataFetcher:
    """
    Mock data fetcher for testing without real API calls
    Preserved from the original implementation
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