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

# Import correct classes from api_integration
from api_integration import BinanceAPIManager, APIIntegrationManager
from oi_radar_integration import OISpikeRadarIntegration
from technical_calculator import TechnicalIndicatorCalculator
from config import DEFAULT_CONFIG
DEFAULT_RISK_PER_TRADE = DEFAULT_CONFIG['MAX_RISK_PER_TRADE']

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
        self.binance_api = BinanceAPIManager(api_key, secret_key)
        self.oi_radar = OISpikeRadarIntegration()
        self.indicator_calc = TechnicalIndicatorCalculator()
        self.order_book_depth = {}
        self.kline_data = {}
        self.technical_indicators = {}
        self.oi_signals = {}
        self.risk_management = RiskManagement()
        
    async def get_technical_indicators(self, symbol: str, interval: str = '5m') -> Dict:
        """
        Get real-time technical indicators (RSI, MACD, Bollinger Bands, Moving Averages)
        """
        try:
            # Get klines for calculation
            klines = await self.binance_api.get_kline_data(symbol, interval, 100)
            
            if not klines:
                logger.warning(f"No kline data available for {symbol}")
                return {}
            
            closes = [k['close'] for k in klines]
            highs = [k['high'] for k in klines]
            lows = [k['low'] for k in klines]
            
            # Calculate technical indicators
            rsi = self.indicator_calc.calculate_rsi(closes)
            macd = self.indicator_calc.calculate_macd(closes)
            bollinger_bands = self.indicator_calc.calculate_bollinger_bands(closes)
            moving_averages = self.indicator_calc.calculate_moving_averages(closes)
            
            indicators = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'rsi': rsi,
                'macd': macd,
                'bollinger_bands': bollinger_bands,
                'moving_averages': moving_averages
            }
            
            self.technical_indicators[symbol] = indicators
            return indicators
            
        except Exception as e:
            logger.error(f"Error getting technical indicators for {symbol}: {e}")
            return {}

    async def get_kline_data(self, symbol: str, interval: str = '5m', limit: int = 100) -> List:
        """
        Get 5-minute K-line data
        """
        try:
            klines = await self.binance_api.get_kline_data(symbol, interval, limit)
            self.kline_data[symbol] = klines
            return klines
            
        except Exception as e:
            logger.error(f"Error getting kline data for {symbol}: {e}")
            return []

    async def get_order_book_depth(self, symbol: str, limit: int = 100) -> Dict:
        """
        Get real-time order book depth data
        """
        try:
            order_book = await self.binance_api.get_order_book_async(symbol, limit)
            
            if not order_book:
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

    async def analyze_fund_flow(self, symbol: str, interval: str = '5m', limit: int = 100) -> Dict:
        """
        Analyze fund flow based on trade data
        """
        try:
            # Get kline data to analyze volume patterns
            klines = await self.binance_api.get_kline_data(symbol, interval, limit)
            
            if not klines:
                return {}
            
            # Simple fund flow analysis based on volume and price direction
            buy_volume = 0
            sell_volume = 0
            
            for kline in klines:
                if kline['close'] >= kline['open']:  # Bullish candle
                    buy_volume += kline['volume']
                else:  # Bearish candle
                    sell_volume += kline['volume']
            
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
                'flow_direction': 'BULLISH' if buy_ratio > sell_ratio else 'BEARISH'
            }
            
            return fund_flow
            
        except Exception as e:
            logger.error(f"Error analyzing fund flow for {symbol}: {e}")
            return {}

    async def integrate_with_oi_signals(self, symbol: str, oi_signals: List[Dict]) -> Dict:
        """
        Integrate technical indicators with OI (Open Interest) surge signals
        """
        try:
            # Find OI signal for this specific symbol
            symbol_oi_signal = None
            for signal in oi_signals:
                if signal.get('symbol') == symbol:
                    symbol_oi_signal = signal
                    break
            
            # Get technical data
            tech_data = self.technical_indicators.get(symbol, {})
            kline_data = self.kline_data.get(symbol, [])
            
            if not tech_data or not kline_data:
                logger.warning(f"No technical data available for {symbol}")
                return {}
            
            # Calculate composite score based on all factors
            current_price = tech_data.get('moving_averages', {}).get('current_price', 0)
            rsi = tech_data.get('rsi', 50)  # Default to neutral
            macd = tech_data.get('macd', {}).get('macd', 0)
            bb_data = tech_data.get('bollinger_bands', {})
            
            # Calculate BB position
            if bb_data:
                bb_upper = bb_data.get('upper', 0)
                bb_lower = bb_data.get('lower', 0)
                bb_middle = bb_data.get('middle', 0)
                
                if bb_upper != bb_lower:
                    bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
                    bb_position = max(0, min(1, bb_position))  # Clamp between 0 and 1
                else:
                    bb_position = 0.5
            else:
                bb_position = 0.5
            
            # Calculate trend based on moving averages
            ma_data = tech_data.get('moving_averages', {})
            trend_score = self._calculate_trend_score(ma_data, current_price)
            
            # Incorporate OI signals if available
            oi_magnitude = symbol_oi_signal.get('score', 0) if symbol_oi_signal else 0
            # Determine direction based on score or other indicators in the signal
            oi_direction = 'BULLISH' if symbol_oi_signal and symbol_oi_signal.get('direction', '').upper() in ['UP', 'BULLISH', 'LONG'] else 'BEARISH'
            
            # Calculate individual component scores
            rsi_score = self._calculate_rsi_score(rsi)
            macd_score = 1 if macd > 0 else -1 if macd < 0 else 0
            bb_score = self._calculate_bb_score(bb_position)
            oi_score = self._calculate_oi_score(oi_magnitude, oi_direction)
            
            # Weighted composite score
            # Using weights based on reliability and historical performance
            composite_score = (
                0.25 * rsi_score +      # 25% weight to RSI
                0.20 * macd_score +     # 20% weight to MACD
                0.15 * bb_score +       # 15% weight to Bollinger Bands
                0.30 * oi_score +       # 30% weight to OI signals (given high importance)
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
                'oi_signals': symbol_oi_signal
            }
            
            return integrated_analysis
            
        except Exception as e:
            logger.error(f"Error integrating OI signals for {symbol}: {e}")
            return {}

    def _calculate_trend_score(self, ma_data: Dict, current_price: float) -> float:
        """
        Calculate trend score based on moving averages
        """
        if not ma_data:
            return 0
        
        ma_5 = ma_data.get('ma_5', 0)
        ma_10 = ma_data.get('ma_10', 0)
        ma_20 = ma_data.get('ma_20', 0)
        ma_50 = ma_data.get('ma_50', 0)
        
        # Trend based on MA relationships
        scores = []
        
        # Price vs MAs
        if current_price > ma_5:
            scores.append(0.3)  # Positive for price above MA5
        else:
            scores.append(-0.3)
            
        if ma_5 > ma_10:
            scores.append(0.2)  # Positive for MA5 above MA10
        else:
            scores.append(-0.2)
            
        if ma_10 > ma_20:
            scores.append(0.2)  # Positive for MA10 above MA20
        else:
            scores.append(-0.2)
            
        if ma_20 > ma_50:
            scores.append(0.3)  # Higher weight for long-term trend
        else:
            scores.append(-0.3)
        
        # Average the scores
        if scores:
            avg_score = sum(scores) / len(scores)
            # Clamp between -1 and 1
            return max(-1.0, min(1.0, avg_score))
        else:
            return 0

    def _calculate_rsi_score(self, rsi: float) -> float:
        """
        Convert RSI to a score from -1 to 1
        """
        if rsi <= 30:
            return 0.8  # Oversold, bullish
        elif rsi >= 70:
            return -0.8  # Overbought, bearish
        else:
            # Normalize between 30 and 70 to range [-0.8, 0.8]
            # 50 becomes 0 (neutral), values below 50 become positive, above 50 become negative
            if rsi < 50:
                # From 30-50 maps to 0.8 to 0
                return 0.8 * (1 - (rsi - 30) / 20)
            else:
                # From 50-70 maps to 0 to -0.8
                return -0.8 * ((rsi - 50) / 20)

    def _calculate_bb_score(self, bb_position: float) -> float:
        """
        Calculate score based on Bollinger Band position
        """
        if bb_position <= 0.2:
            return 0.8  # Below lower band, oversold
        elif bb_position >= 0.8:
            return -0.8  # Above upper band, overbought
        elif 0.45 <= bb_position <= 0.55:
            return 0  # Around middle, neutral
        else:
            # Score based on distance from middle (0.5), scaled appropriately
            dist_from_mid = bb_position - 0.5
            # Scale to range [-0.7, 0.7] excluding the extremes
            return -dist_from_mid * 1.4  # Multiplied by 1.4 to scale from [-0.35, 0.35] to [-0.49, 0.49]

    def _calculate_oi_score(self, magnitude: float, direction: str) -> float:
        """
        Calculate score based on OI signals
        """
        # Normalize magnitude (assuming max meaningful magnitude is around 10)
        normalized_magnitude = min(1.0, magnitude / 3.5)  # Adjust divisor based on typical scores
        
        if direction.upper() in ['BULLISH', 'UP', 'LONG']:
            return normalized_magnitude
        elif direction.upper() in ['BEARISH', 'DOWN', 'SHORT']:
            return -normalized_magnitude
        else:
            return 0

    def _generate_recommendation(self, composite_score: float) -> str:
        """
        Generate recommendation based on composite score
        """
        if composite_score >= 0.6:
            return 'STRONG_BUY'
        elif composite_score >= 0.3:
            return 'BUY'
        elif composite_score >= -0.3:
            return 'HOLD'
        elif composite_score >= -0.6:
            return 'SELL'
        else:
            return 'STRONG_SELL'

    def calculate_dynamic_stop_loss_take_profit(
        self, 
        entry_price: float, 
        position_type: str, 
        volatility: float,
        risk_percentage: float = DEFAULT_RISK_PER_TRADE * 100
    ) -> Dict:
        """
        Calculate dynamic stop-loss and take-profit levels
        """
        return self.risk_management.calculate_stop_loss_take_profit(
            entry_price, position_type, volatility, risk_percentage
        )

    async def generate_trading_signal_panel(self, symbols: List[str]) -> List[Dict]:
        """
        Generate real-time trading signal panel
        """
        signal_panel = []
        
        # Get OI signals once for all symbols
        oi_signals = await self.oi_radar.get_latest_signals()
        
        for symbol in symbols:
            # Get all required data
            await self.get_technical_indicators(symbol)
            await self.get_kline_data(symbol)
            await self.get_order_book_depth(symbol)
            fund_flow = await self.analyze_fund_flow(symbol)
            
            # Integrate all data
            integrated_analysis = await self.integrate_with_oi_signals(symbol, oi_signals)
            
            if integrated_analysis:
                # Add fund flow data
                integrated_analysis['fund_flow'] = fund_flow
                
                # Calculate volatility for risk management
                klines = self.kline_data.get(symbol, [])
                if klines:
                    prices = [k['close'] for k in klines]
                    avg_price = sum(prices) / len(prices) if prices else 1
                    volatility = (np.std(prices) / avg_price) * 100 if avg_price > 0 else 2.5
                else:
                    volatility = 2.5  # Default volatility percentage
                
                # Calculate risk management parameters based on recommendation
                current_price = integrated_analysis['technical_indicators'].get(
                    'moving_averages', {}
                ).get('current_price', 0)
                
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
                    risk_params = {'stop_loss': None, 'take_profit': None, 'risk_percentage': 0}
                
                integrated_analysis['risk_management'] = risk_params
                integrated_analysis['volatility'] = volatility
                integrated_analysis['current_price'] = current_price
                
                signal_panel.append(integrated_analysis)
        
        return signal_panel


class RiskManagement:
    """
    Risk management module with dynamic stop-loss and take-profit calculations
    """

    def __init__(self, max_risk_per_trade: float = DEFAULT_RISK_PER_TRADE):
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
        # Higher volatility = wider stops to avoid premature exits
        vol_factor = 1 + (volatility / 20)  # Increase stop distance with volatility
        adjusted_risk = risk_percentage * vol_factor

        if position_type.upper() == 'LONG':
            # For long positions: stop loss below entry, take profit above entry
            stop_loss_distance = adjusted_risk
            take_profit_distance = adjusted_risk * 2  # 1:2 risk-reward ratio
            
            stop_loss = entry_price * (1 - stop_loss_distance / 100)
            take_profit = entry_price * (1 + take_profit_distance / 100)

        elif position_type.upper() == 'SHORT':
            # For short positions: stop loss above entry, take profit below entry
            stop_loss_distance = adjusted_risk
            take_profit_distance = adjusted_risk * 2  # 1:2 risk-reward ratio
            
            stop_loss = entry_price * (1 + stop_loss_distance / 100)
            take_profit = entry_price * (1 - take_profit_distance / 100)
        else:
            raise ValueError("Position type must be 'LONG' or 'SHORT'")

        # Ensure stop loss is appropriate side for position
        if position_type.upper() == 'LONG':
            stop_loss = min(stop_loss, entry_price * 0.999)  # Ensure slightly below entry
        else:  # SHORT
            stop_loss = max(stop_loss, entry_price * 1.001)  # Ensure slightly above entry

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
    
    # Example symbols to analyze
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
    
    print("Starting Enhanced Trading Analysis...")
    
    # Generate trading signal panel
    signal_panel = await trading_system.generate_trading_signal_panel(symbols)
    
    print("\n=== ENHANCED TRADING SIGNAL PANEL ===")
    for signal in signal_panel:
        symbol = signal['symbol']
        comp_score = signal['composite_score']
        recommendation = signal['recommendation']
        confidence = signal['confidence_level']
        current_price = signal.get('current_price', 'N/A')
        
        print(f"\nSymbol: {symbol}")
        print(f"Current Price: {current_price}")
        print(f"Composite Score: {comp_score:.3f}")
        print(f"Recommendation: {recommendation}")
        print(f"Confidence Level: {confidence:.1f}%")
        
        # Show key technical indicators
        tech_ind = signal['technical_indicators']
        if tech_ind:
            rsi = tech_ind.get('rsi', 'N/A')
            print(f"RSI: {rsi:.2f}")
            
            ma_data = tech_ind.get('moving_averages', {})
            if ma_data:
                ma_5 = ma_data.get('ma_5', 'N/A')
                ma_20 = ma_data.get('ma_20', 'N/A')
                print(f"MA5: {ma_5}, MA20: {ma_20}")
        
        # Show risk management
        risk_mgmt = signal.get('risk_management', {})
        if risk_mgmt:
            sl = risk_mgmt.get('stop_loss', 'N/A')
            tp = risk_mgmt.get('take_profit', 'N/A')
            risk_pct = risk_mgmt.get('risk_percentage', 'N/A')
            print(f"Suggested Stop Loss: {sl}")
            print(f"Suggested Take Profit: {tp}")
            print(f"Risk Percentage: {risk_pct}%")
        
        # Show volatility
        volatility = signal.get('volatility', 'N/A')
        print(f"Volatility: {volatility:.2f}%")
    
    # Close connections
    await trading_system.binance_api.close()
    await trading_system.oi_radar.close()
    
    print("\nAnalysis complete!")


if __name__ == "__main__":
    asyncio.run(main())