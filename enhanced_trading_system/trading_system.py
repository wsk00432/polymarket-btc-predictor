"""
Enhanced Trading Analysis System
Integrating multiple data sources and indicators for comprehensive market analysis
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import numpy as np

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import from our new API integration module
from api_integration import get_api_manager, get_symbol_data, get_technical_data_cached
from config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnhancedTradingSystem:
    """
    Main class for the enhanced trading analysis system
    Integrates multiple data sources and provides comprehensive analysis
    """
    
    def __init__(self, api_key: str = None, secret_key: str = None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.api_manager = None
        self.order_book_depth = {}
        self.kline_data = {}
        self.technical_indicators = {}
        self.oi_signals = {}
        self.risk_management = RiskManagement()
    
    async def initialize_async_client(self):
        """Initialize API manager"""
        self.api_manager = await get_api_manager()
        logger.info("API manager initialized successfully")
    
    async def get_technical_indicators(self, symbol: str, interval: str = None) -> Dict:
        """
        Get real-time technical indicators (RSI, MACD, Bollinger Bands, Moving Averages)
        """
        try:
            if interval is None:
                interval = get_config('KLINE_INTERVAL', '5m')
            
            # Get technical data from API integration
            tech_data = await get_technical_data_cached(symbol, interval, 100)
            klines = tech_data.get('klines', [])
            
            if not klines:
                logger.warning(f"No kline data available for {symbol}")
                return {}
            
            closes = [float(k[4]) for k in klines]
            highs = [float(k[2]) for k in klines]
            lows = [float(k[3]) for k in klines]
            
            df = pd.DataFrame({
                'close': closes,
                'high': highs,
                'low': lows
            })
            
            # Calculate RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # Calculate MACD
            exp1 = df['close'].ewm(span=12).mean()
            exp2 = df['close'].ewm(span=26).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9).mean()
            histogram = macd - signal
            
            # Calculate Bollinger Bands
            sma_20 = df['close'].rolling(window=20).mean()
            std_dev = df['close'].rolling(window=20).std()
            upper_band = sma_20 + (std_dev * 2)
            lower_band = sma_20 - (std_dev * 2)
            
            # Calculate Moving Averages
            ma_5 = df['close'].rolling(window=5).mean()
            ma_10 = df['close'].rolling(window=10).mean()
            ma_20 = df['close'].rolling(window=20).mean()
            ma_50 = df['close'].rolling(window=50).mean()
            
            indicators = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'rsi': rsi.iloc[-1],
                'macd': {
                    'macd': macd.iloc[-1],
                    'signal': signal.iloc[-1],
                    'histogram': histogram.iloc[-1]
                },
                'bollinger_bands': {
                    'upper': upper_band.iloc[-1],
                    'middle': sma_20.iloc[-1],
                    'lower': lower_band.iloc[-1],
                    'current_price': df['close'].iloc[-1]
                },
                'moving_averages': {
                    'ma_5': ma_5.iloc[-1],
                    'ma_10': ma_10.iloc[-1],
                    'ma_20': ma_20.iloc[-1],
                    'ma_50': ma_50.iloc[-1],
                    'current_price': df['close'].iloc[-1]
                }
            }
            
            self.technical_indicators[symbol] = indicators
            return indicators
            
        except Exception as e:
            logger.error(f"Error getting technical indicators for {symbol}: {e}")
            return {}
    
    async def get_kline_data(self, symbol: str, interval: str = None, limit: int = None) -> List:
        """
        Get 5-minute K-line data
        """
        try:
            if interval is None:
                interval = get_config('KLINE_INTERVAL', '5m')
            if limit is None:
                limit = get_config('KLINE_LIMIT', 100)
            
            # Get technical data from API integration
            tech_data = await get_technical_data_cached(symbol, interval, limit)
            raw_klines = tech_data.get('klines', [])
            
            formatted_klines = []
            for kline in raw_klines:
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
            
            self.kline_data[symbol] = formatted_klines
            return formatted_klines
            
        except Exception as e:
            logger.error(f"Error getting kline data for {symbol}: {e}")
            return []
    
    async def get_order_book_depth(self, symbol: str, limit: int = None) -> Dict:
        """
        Get real-time order book depth data
        """
        try:
            if limit is None:
                limit = get_config('ORDER_BOOK_LIMIT', 100)
            
            # Get market data which includes order book
            market_data = await get_symbol_data(symbol)
            order_book = market_data.get('order_book', {})
            
            if not order_book:
                logger.warning(f"No order book data available for {symbol}")
                return {}
            
            # Process bids and asks
            bids = [(float(price), float(qty)) for price, qty in order_book['bids']]
            asks = [(float(price), float(qty)) for price, qty in order_book['asks']]
            
            # Calculate cumulative volumes
            bid_cumulative = np.cumsum([qty for _, qty in bids])
            ask_cumulative = np.cumsum([qty for _, qty in asks])
            
            depth_data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'bids': [{'price': price, 'quantity': qty} for price, qty in bids[:20]],
                'asks': [{'price': price, 'quantity': qty} for price, qty in asks[:20]],
                'bid_volume': sum([qty for _, qty in bids]),
                'ask_volume': sum([qty for _, qty in asks]),
                'bid_cumulative': bid_cumulative[:20].tolist() if len(bid_cumulative) > 0 else [],
                'ask_cumulative': ask_cumulative[:20].tolist() if len(ask_cumulative) > 0 else [],
                'spread': (asks[0][0] - bids[0][0]) if bids and asks else 0,
                'spread_percentage': ((asks[0][0] - bids[0][0]) / bids[0][0] * 100) if bids and asks else 0
            }
            
            self.order_book_depth[symbol] = depth_data
            return depth_data
            
        except Exception as e:
            logger.error(f"Error getting order book depth for {symbol}: {e}")
            return {}
    
    async def analyze_fund_flow(self, symbol: str, interval: str = None, limit: int = None) -> Dict:
        """
        Analyze fund flow based on trade data
        """
        try:
            if limit is None:
                limit = 100
            
            # Get technical data which includes trades
            tech_data = await get_technical_data_cached(symbol, interval, limit)
            trades = tech_data.get('trades', [])
            
            if not trades:
                logger.warning(f"No trade data available for {symbol}")
                return {}
            
            buy_volume = 0
            sell_volume = 0
            buy_count = 0
            sell_count = 0
            
            for trade in trades:
                if trade.get('m', True):  # Buyer is maker (sell order filled)
                    sell_volume += float(trade.get('q', 0))
                    sell_count += 1
                else:  # Seller is maker (buy order filled)
                    buy_volume += float(trade.get('q', 0))
                    buy_count += 1
            
            total_volume = buy_volume + sell_volume
            buy_ratio = buy_volume / total_volume if total_volume > 0 else 0
            sell_ratio = sell_volume / total_volume if total_volume > 0 else 0
            
            fund_flow = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'buy_volume': buy_volume,
                'sell_volume': sell_volume,
                'total_volume': total_volume,
                'buy_ratio': buy_ratio,
                'sell_ratio': sell_ratio,
                'net_flow': buy_volume - sell_volume,
                'buy_trade_count': buy_count,
                'sell_trade_count': sell_count,
                'flow_direction': 'BULLISH' if buy_ratio > sell_ratio else 'BEARISH'
            }
            
            return fund_flow
            
        except Exception as e:
            logger.error(f"Error analyzing fund flow for {symbol}: {e}")
            return {}
    
    def integrate_with_oi_signals(self, symbol: str, oi_signals: Dict) -> Dict:
        """
        Integrate technical indicators with OI (Open Interest) surge signals
        """
        try:
            # Combine technical indicators with OI signals
            tech_data = self.technical_indicators.get(symbol, {})
            kline_data = self.kline_data.get(symbol, [])
            
            if not tech_data or not kline_data:
                logger.warning(f"No technical data available for {symbol}")
                return {}
            
            # Calculate composite score based on all factors
            current_price = tech_data.get('moving_averages', {}).get('current_price', 0)
            rsi = tech_data.get('rsi', 50)  # Default to neutral
            macd = tech_data.get('macd', {}).get('macd', 0)
            bb_position = self._calculate_bb_position(
                current_price, 
                tech_data.get('bollinger_bands', {})
            )
            
            # Calculate trend based on moving averages
            ma_data = tech_data.get('moving_averages', {})
            trend_score = self._calculate_trend_score(ma_data)
            
            # Incorporate OI signals
            oi_magnitude = oi_signals.get('magnitude', 0) if oi_signals else 0
            oi_direction = oi_signals.get('direction', 'NEUTRAL') if oi_signals else 'NEUTRAL'
            
            # Composite scoring
            rsi_score = self._calculate_rsi_score(rsi)
            macd_score = 1 if macd > 0 else -1 if macd < 0 else 0
            bb_score = self._calculate_bb_score(bb_position)
            oi_score = self._calculate_oi_score(oi_magnitude, oi_direction)
            
            # Weighted composite score
            composite_score = (
                0.25 * rsi_score +      # 25% weight to RSI
                0.20 * macd_score +     # 20% weight to MACD
                0.20 * bb_score +       # 20% weight to Bollinger Bands
                0.25 * oi_score +       # 25% weight to OI signals
                0.10 * trend_score      # 10% weight to trend
            )
            
            integrated_analysis = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'composite_score': composite_score,
                'score_components': {
                    'rsi_score': rsi_score,
                    'macd_score': macd_score,
                    'bb_score': bb_score,
                    'oi_score': oi_score,
                    'trend_score': trend_score
                },
                'recommendation': self._generate_recommendation(composite_score),
                'confidence_level': abs(composite_score) * 100,
                'technical_indicators': tech_data,
                'oi_signals': oi_signals
            }
            
            return integrated_analysis
            
        except Exception as e:
            logger.error(f"Error integrating OI signals for {symbol}: {e}")
            return {}
    
    def _calculate_bb_position(self, current_price: float, bb_data: Dict) -> float:
        """Calculate position of current price relative to Bollinger Bands"""
        if not bb_data:
            return 0.5  # Neutral
        
        upper = bb_data.get('upper', 0)
        middle = bb_data.get('middle', 0)
        lower = bb_data.get('lower', 0)
        
        if upper == lower:  # Avoid division by zero
            return 0.5
        
        # Position from 0 (below lower band) to 1 (above upper band)
        position = (current_price - lower) / (upper - lower)
        return max(0, min(1, position))
    
    def _calculate_trend_score(self, ma_data: Dict) -> float:
        """Calculate trend score based on moving averages"""
        if not ma_data:
            return 0
        
        current_price = ma_data.get('current_price', 0)
        ma_5 = ma_data.get('ma_5', 0)
        ma_20 = ma_data.get('ma_20', 0)
        ma_50 = ma_data.get('ma_50', 0)
        
        # Trend based on MA relationships
        score = 0
        if current_price > ma_5 > ma_20 > ma_50:
            score = 0.8  # Strong bullish
        elif current_price > ma_5 and ma_5 > ma_20:
            score = 0.5  # Mild bullish
        elif current_price < ma_5 < ma_20 < ma_50:
            score = -0.8  # Strong bearish
        elif current_price < ma_5 and ma_5 < ma_20:
            score = -0.5  # Mild bearish
        else:
            score = 0  # Neutral
        
        return score
    
    def _calculate_rsi_score(self, rsi: float) -> float:
        """Convert RSI to a score from -1 to 1"""
        if rsi < 30:
            return 0.8  # Oversold, bullish
        elif rsi > 70:
            return -0.8  # Overbought, bearish
        else:
            # Normalize between 30 and 70
            normalized = (rsi - 50) / 20  # Result between -1 and 1
            return -normalized  # Invert so higher RSI is bearish
    
    def _calculate_bb_score(self, bb_position: float) -> float:
        """Calculate score based on Bollinger Band position"""
        if bb_position < 0.2:
            return 0.8  # Below lower band, oversold
        elif bb_position > 0.8:
            return -0.8  # Above upper band, overbought
        else:
            # Score based on distance from middle (0.5)
            dist_from_mid = bb_position - 0.5
            return -dist_from_mid * 2  # Scale to -1 to 1
    
    def _calculate_oi_score(self, magnitude: float, direction: str) -> float:
        """Calculate score based on OI signals"""
        base_score = min(1.0, magnitude / 100)  # Normalize magnitude
        
        if direction == 'BULLISH':
            return base_score
        elif direction == 'BEARISH':
            return -base_score
        else:
            return 0
    
    def _generate_recommendation(self, composite_score: float) -> str:
        """Generate recommendation based on composite score"""
        if composite_score >= 0.7:
            return 'STRONG_BUY'
        elif composite_score >= 0.3:
            return 'BUY'
        elif composite_score >= -0.3:
            return 'HOLD'
        elif composite_score >= -0.7:
            return 'SELL'
        else:
            return 'STRONG_SELL'
    
    def calculate_dynamic_stop_loss_take_profit(
        self, 
        entry_price: float, 
        position_type: str, 
        volatility: float,
        risk_percentage: float = 2.0
    ) -> Dict:
        """
        Calculate dynamic stop-loss and take-profit levels
        """
        return self.risk_management.calculate_stop_loss_take_profit(
            entry_price, position_type, volatility, risk_percentage
        )
    
    async def generate_trading_signal_panel(self, symbols: List[str], oi_signals: Dict = None) -> List[Dict]:
        """
        Generate real-time trading signal panel
        """
        signal_panel = []
        
        for symbol in symbols:
            # Get all required data
            await self.get_technical_indicators(symbol)
            await self.get_kline_data(symbol)
            await self.get_order_book_depth(symbol)
            fund_flow = await self.analyze_fund_flow(symbol)
            
            # Get specific OI signal for this symbol if available
            symbol_oi_signal = oi_signals.get(symbol) if oi_signals else None
            
            # Integrate all data
            integrated_analysis = self.integrate_with_oi_signals(symbol, symbol_oi_signal)
            
            # Add additional metrics
            if integrated_analysis:
                # Add fund flow data
                integrated_analysis['fund_flow'] = fund_flow
                
                # Add risk management suggestions
                current_price = integrated_analysis['technical_indicators'].get(
                    'moving_averages', {}
                ).get('current_price', entry_price)
                
                # Calculate volatility for risk management
                klines = self.kline_data.get(symbol, [])
                if klines:
                    prices = [k['close'] for k in klines]
                    volatility = np.std(prices) / np.mean(prices) * 100
                else:
                    volatility = 2.5  # Default volatility percentage
                
                # Calculate stop loss and take profit based on recommendation
                recommendation = integrated_analysis['recommendation']
                if 'BUY' in recommendation:
                    risk_params = self.calculate_dynamic_stop_loss_take_profit(
                        current_price, 'LONG', volatility
                    )
                elif 'SELL' in recommendation:
                    risk_params = self.calculate_dynamic_stop_loss_take_profit(
                        current_price, 'SHORT', volatility
                    )
                else:
                    risk_params = {'stop_loss': None, 'take_profit': None}
                
                integrated_analysis['risk_management'] = risk_params
                integrated_analysis['volatility'] = volatility
                
                signal_panel.append(integrated_analysis)
        
        return signal_panel


class RiskManagement:
    """
    Risk management module with dynamic stop-loss and take-profit calculations
    """
    
    def __init__(self, max_risk_per_trade: float = 0.02):  # 2% max risk per trade
        self.max_risk_per_trade = max_risk_per_trade
    
    def calculate_stop_loss_take_profit(
        self, 
        entry_price: float, 
        position_type: str,  # 'LONG' or 'SHORT'
        volatility: float,   # Percentage volatility
        risk_percentage: float = None
    ) -> Dict:
        """
        Calculate dynamic stop-loss and take-profit levels based on volatility and risk tolerance
        """
        if risk_percentage is None:
            risk_percentage = self.max_risk_per_trade * 100  # Convert to percentage
        
        # Adjust risk based on volatility
        adjusted_risk = risk_percentage * (1 + volatility / 10)  # Increase risk with higher volatility
        
        if position_type.upper() == 'LONG':
            # For long positions: stop loss below entry, take profit above entry
            stop_loss_pct = adjusted_risk
            take_profit_pct = adjusted_risk * 2  # 1:2 risk-reward ratio
            
            stop_loss = entry_price * (1 - stop_loss_pct / 100)
            take_profit = entry_price * (1 + take_profit_pct / 100)
            
        elif position_type.upper() == 'SHORT':
            # For short positions: stop loss above entry, take profit below entry
            stop_loss_pct = adjusted_risk
            take_profit_pct = adjusted_risk * 2  # 1:2 risk-reward ratio
            
            stop_loss = entry_price * (1 + stop_loss_pct / 100)
            take_profit = entry_price * (1 - take_profit_pct / 100)
        else:
            raise ValueError("Position type must be 'LONG' or 'SHORT'")
        
        # Apply volatility adjustment
        vol_factor = 1 + (volatility / 20)  # Increase stops based on volatility
        if position_type.upper() == 'LONG':
            stop_loss = entry_price - (entry_price - stop_loss) * vol_factor
            take_profit = entry_price + (take_profit - entry_price) * vol_factor
        else:  # SHORT
            stop_loss = entry_price + (stop_loss - entry_price) * vol_factor
            take_profit = entry_price - (entry_price - take_profit) * vol_factor
        
        # Ensure stop loss is appropriate side for position
        if position_type.upper() == 'LONG':
            stop_loss = min(stop_loss, entry_price * 0.99)  # Ensure below entry
        else:  # SHORT
            stop_loss = max(stop_loss, entry_price * 1.01)  # Ensure above entry
        
        return {
            'stop_loss': round(stop_loss, 8),
            'take_profit': round(take_profit, 8),
            'risk_percentage': round(adjusted_risk, 4),
            'risk_reward_ratio': 2.0  # Fixed 1:2 ratio
        }


async def main():
    """
    Example usage of the Enhanced Trading System
    """
    # Initialize system (without API keys for demo)
    trading_system = EnhancedTradingSystem()
    
    # Initialize the API manager
    await trading_system.initialize_async_client()
    
    # Example symbols to analyze
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    
    # Example OI signals (these would come from your existing OI detection system)
    oi_signals = {
        'BTCUSDT': {
            'magnitude': 15.5,
            'direction': 'BULLISH',
            'timestamp': datetime.now().isoformat()
        },
        'ETHUSDT': {
            'magnitude': 8.2,
            'direction': 'BEARISH',
            'timestamp': datetime.now().isoformat()
        }
    }
    
    print("Starting Enhanced Trading Analysis...")
    
    # Generate trading signal panel
    signal_panel = await trading_system.generate_trading_signal_panel(symbols, oi_signals)
    
    print("\n=== ENHANCED TRADING SIGNAL PANEL ===")
    for signal in signal_panel:
        symbol = signal['symbol']
        comp_score = signal['composite_score']
        recommendation = signal['recommendation']
        confidence = signal['confidence_level']
        
        print(f"\nSymbol: {symbol}")
        print(f"Composite Score: {comp_score:.3f}")
        print(f"Recommendation: {recommendation}")
        print(f"Confidence Level: {confidence:.1f}%")
        
        # Show key technical indicators
        tech_ind = signal['technical_indicators']
        if tech_ind:
            rsi = tech_ind.get('rsi', 'N/A')
            current_price = tech_ind.get('moving_averages', {}).get('current_price', 'N/A')
            print(f"Current Price: {current_price}")
            print(f"RSI: {rsi:.2f}")
        
        # Show risk management
        risk_mgmt = signal.get('risk_management', {})
        if risk_mgmt:
            sl = risk_mgmt.get('stop_loss', 'N/A')
            tp = risk_mgmt.get('take_profit', 'N/A')
            print(f"Suggested Stop Loss: {sl}")
            print(f"Suggested Take Profit: {tp}")
    
    print("\nAnalysis complete!")


if __name__ == "__main__":
    asyncio.run(main())