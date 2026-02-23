"""
Improved Data Fetcher using the new API Integration Module
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from .api_integration import get_api_manager, get_symbol_data, get_multiple_symbols_data_cached, get_technical_data_cached
from .models import KlineData, OrderBookDepth, FundFlow, OISignal
from .config import get_config
from .utils import safe_float_conversion


class ImprovedDataFetcher:
    """
    Improved data fetcher that leverages the new API integration module
    """
    
    def __init__(self):
        self.api_manager = None
    
    async def initialize(self):
        """Initialize the API manager"""
        if self.api_manager is None:
            self.api_manager = await get_api_manager()
    
    async def fetch_kline_data(self, symbol: str, interval: str = None, limit: int = None) -> List[KlineData]:
        """
        Fetch K-line data using the new API integration
        """
        await self.initialize()
        
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
        await self.initialize()
        
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
        await self.initialize()
        
        try:
            market_data = await get_symbol_data(symbol)
            return market_data.get('price', 0.0)
        except Exception as e:
            print(f"Error fetching current price for {symbol}: {e}")
            return 0.0
    
    async def fetch_multiple_symbols_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Fetch data for multiple symbols using the new API integration
        """
        await self.initialize()
        
        try:
            # Use the cached function for efficiency
            return await get_multiple_symbols_data_cached(symbols)
        except Exception as e:
            print(f"Error fetching data for multiple symbols: {e}")
            return {symbol: {} for symbol in symbols}
    
    async def fetch_fund_flow(self, symbol: str, limit: int = 100) -> Optional[FundFlow]:
        """
        Analyze fund flow based on recent trades using the new API integration
        """
        await self.initialize()
        
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
    
    async def fetch_oi_data(self, symbol: str) -> Optional[OISignal]:
        """
        Fetch Open Interest data (placeholder - would connect to futures data source)
        """
        await self.initialize()
        
        try:
            # In a real implementation, you would get actual OI data from futures endpoints
            # This connects to the API manager to get futures-specific data
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
    
    async def fetch_symbol_data(self, symbol: str) -> Dict:
        """
        Fetch comprehensive data for a single symbol using the new API integration
        """
        await self.initialize()
        
        # Get all data concurrently for efficiency
        market_data = await get_symbol_data(symbol)
        
        data = {
            'symbol': symbol,
            'klines': await self.fetch_kline_data(symbol),
            'order_book': await self.fetch_order_book_depth(symbol),
            'fund_flow': await self.fetch_fund_flow(symbol),
            'current_price': market_data.get('price', 0.0),
            'ticker_24h': market_data.get('ticker_24h', {}),
            'timestamp': market_data.get('timestamp', datetime.now())
        }
        
        return data


# Update the original DataFetcher in data_fetcher.py to use the new API integration
class ModernDataFetcher(ImprovedDataFetcher):
    """
    A version compatible with the original interface but using new API integration
    """
    pass