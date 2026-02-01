"""
Demo script for Enhanced Trading Analysis System
Demonstrates the integration of multiple data sources for improved trading signals
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def simulate_binance_data(symbol: str) -> Dict:
    """
    Simulate Binance API data since we may not have API keys
    """
    import random
    
    # Simulate realistic market data
    base_price = {
        'BTCUSDT': 45000,
        'ETHUSDT': 2800,
        'SOLUSDT': 150,
        'XRPUSDT': 0.55,
        'ADAUSDT': 0.45
    }.get(symbol, 100)
    
    # Add some random fluctuation
    current_price = base_price * (1 + (random.uniform(-0.05, 0.05)))
    
    # Generate simulated kline data (last 100 5-min candles)
    klines = []
    temp_price = current_price * 0.98  # Start slightly lower
    for i in range(100):
        open_price = temp_price
        change = random.uniform(-0.02, 0.03)  # -2% to +3% change
        close_price = open_price * (1 + change)
        high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.02))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.02))
        
        klines.append({
            'open_time': int(datetime.now().timestamp()) - (99-i)*300,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': random.uniform(100, 1000)
        })
        
        temp_price = close_price
    
    # Simulate order book
    bid_price = current_price * 0.999
    ask_price = current_price * 1.001
    
    order_book = {
        'bids': [[round(bid_price * (1 - i*0.0001), 4), round(random.uniform(1, 10), 2)] for i in range(20)],
        'asks': [[round(ask_price * (1 + i*0.0001), 4), round(random.uniform(1, 10), 2)] for i in range(20)]
    }
    
    return {
        'current_price': current_price,
        'klines': klines,
        'order_book': order_book,
        'symbol': symbol
    }


def calculate_technical_indicators(klines: List[Dict]) -> Dict:
    """
    Calculate technical indicators from kline data
    """
    import numpy as np
    import pandas as pd
    
    closes = [k['close'] for k in klines]
    highs = [k['high'] for k in klines]
    lows = [k['low'] for k in klines]
    
    # Calculate RSI
    def calculate_rsi(prices, period=14):
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = np.zeros_like(gains)
        avg_losses = np.zeros_like(losses)
        
        avg_gains[0:period] = np.mean(gains[0:period])
        avg_losses[0:period] = np.mean(losses[0:period])
        
        for i in range(period, len(gains)):
            avg_gains[i] = (avg_gains[i-1] * (period-1) + gains[i]) / period
            avg_losses[i] = (avg_losses[i-1] * (period-1) + losses[i]) / period
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        return rsi[-1] if len(rsi) > 0 else 50
    
    # Calculate MACD
    def calculate_macd(prices, fast=12, slow=26, signal=9):
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
    
    # Calculate Bollinger Bands
    def calculate_bollinger_bands(prices, period=20, std_dev=2):
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
    
    # Calculate Moving Averages
    def calculate_moving_averages(prices, periods=[5, 10, 20, 50]):
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
    
    rsi = calculate_rsi(closes)
    macd = calculate_macd(closes)
    bollinger_bands = calculate_bollinger_bands(closes)
    moving_averages = calculate_moving_averages(closes)
    
    return {
        'rsi': rsi,
        'macd': macd,
        'bollinger_bands': bollinger_bands,
        'moving_averages': moving_averages,
        'current_price': closes[-1]
    }


def get_mock_oi_signals(symbols: List[str]) -> List[Dict]:
    """
    Mock OI (Open Interest) signals similar to what our radar would detect
    """
    import random
    
    oi_signals = []
    
    for symbol in symbols:
        # Randomly decide if there's an OI signal for this symbol
        if random.random() > 0.7:  # 30% chance of signal
            direction = random.choice(['UP', 'DOWN'])
            score = round(random.uniform(2.5, 4.0), 1)  # Scores similar to our radar
            
            oi_signals.append({
                'symbol': symbol,
                'score': score,
                'direction': direction,
                'timestamp': datetime.now().isoformat(),
                'reasons': ['vol_spike', 'oi_zscore'] if random.random() > 0.5 else ['vol_spike']
            })
    
    return oi_signals


def integrate_analysis(symbol: str, tech_indicators: Dict, oi_signals: List[Dict]) -> Dict:
    """
    Integrate technical indicators with OI signals to generate trading recommendation
    """
    # Find OI signal for this symbol
    symbol_oi_signal = None
    for signal in oi_signals:
        if signal.get('symbol') == symbol:
            symbol_oi_signal = signal
            break
    
    # Extract values
    current_price = tech_indicators.get('current_price', 0)
    rsi = tech_indicators.get('rsi', 50)
    macd = tech_indicators.get('macd', {}).get('macd', 0)
    bb_data = tech_indicators.get('bollinger_bands', {})
    
    # Calculate BB position
    if bb_data:
        bb_upper = bb_data.get('upper', 0)
        bb_lower = bb_data.get('lower', 0)
        
        if bb_upper != bb_lower:
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
            bb_position = max(0, min(1, bb_position))  # Clamp between 0 and 1
        else:
            bb_position = 0.5
    else:
        bb_position = 0.5
    
    # Calculate trend score from moving averages
    ma_data = tech_indicators.get('moving_averages', {})
    ma_5 = ma_data.get('ma_5', 0)
    ma_20 = ma_data.get('ma_20', 0)
    
    if current_price > ma_5 > ma_20:
        trend_score = 0.6  # Bullish trend
    elif current_price < ma_5 < ma_20:
        trend_score = -0.6  # Bearish trend
    elif ma_5 > ma_20:
        trend_score = 0.3  # Mildly bullish
    elif ma_5 < ma_20:
        trend_score = -0.3  # Mildly bearish
    else:
        trend_score = 0  # Neutral
    
    # Incorporate OI signals if available
    oi_magnitude = symbol_oi_signal.get('score', 0) if symbol_oi_signal else 0
    oi_direction = symbol_oi_signal.get('direction', 'NEUTRAL') if symbol_oi_signal else 'NEUTRAL'
    
    # Calculate individual component scores
    # RSI score: bullish when oversold (<30), bearish when overbought (>70)
    if rsi < 30:
        rsi_score = 0.8  # Very bullish (oversold)
    elif rsi > 70:
        rsi_score = -0.8  # Very bearish (overbought)
    elif 40 <= rsi <= 60:
        rsi_score = 0  # Neutral
    else:
        # Between 30-40 (slightly bullish) or 60-70 (slightly bearish)
        rsi_score = 0.4 if rsi < 50 else -0.4
    
    # MACD score
    macd_score = 1 if macd > 0.001 else -1 if macd < -0.001 else 0
    
    # Bollinger Band score: bullish when near/below lower band, bearish when near/above upper band
    if bb_position < 0.2:
        bb_score = 0.7  # Near lower band - bullish
    elif bb_position > 0.8:
        bb_score = -0.7  # Near upper band - bearish
    elif 0.4 <= bb_position <= 0.6:
        bb_score = 0  # Middle - neutral
    else:
        # Between neutral and bands - mild signals
        bb_score = 0.3 if bb_position < 0.5 else -0.3
    
    # OI score: weighted heavily as our primary signal
    if oi_direction == 'UP':
        oi_score = min(1.0, oi_magnitude / 4.0)  # Normalize to 0-1 range
    elif oi_direction == 'DOWN':
        oi_score = -min(1.0, oi_magnitude / 4.0)
    else:
        oi_score = 0
    
    # Weighted composite score
    # OI signals get highest weight as they're our primary edge
    composite_score = (
        0.35 * oi_score +      # 35% weight to OI signals
        0.25 * rsi_score +     # 25% weight to RSI
        0.20 * bb_score +      # 20% weight to Bollinger Bands
        0.10 * macd_score +    # 10% weight to MACD
        0.10 * trend_score     # 10% weight to trend
    )
    
    # Generate recommendation
    if composite_score >= 0.6:
        recommendation = 'STRONG_BUY'
    elif composite_score >= 0.3:
        recommendation = 'BUY'
    elif composite_score >= -0.3:
        recommendation = 'HOLD'
    elif composite_score >= -0.6:
        recommendation = 'SELL'
    else:
        recommendation = 'STRONG_SELL'
    
    # Calculate risk management
    # Simple calculation based on recommendation
    volatility_estimate = abs(rsi - 50) / 50 + 0.02  # Base volatility estimate
    
    if 'BUY' in recommendation:
        # For long positions
        stop_loss_pct = 2.0 * volatility_estimate  # 2% of estimated volatility
        take_profit_pct = stop_loss_pct * 2  # 1:2 risk-reward ratio
        
        stop_loss = round(current_price * (1 - stop_loss_pct), 6)
        take_profit = round(current_price * (1 + take_profit_pct), 6)
    elif 'SELL' in recommendation:
        # For short positions
        stop_loss_pct = 2.0 * volatility_estimate
        take_profit_pct = stop_loss_pct * 2
        
        stop_loss = round(current_price * (1 + stop_loss_pct), 6)
        take_profit = round(current_price * (1 - take_profit_pct), 6)
    else:
        # For HOLD, no specific stop loss/take profit
        stop_loss = None
        take_profit = None
    
    return {
        'symbol': symbol,
        'current_price': current_price,
        'composite_score': round(composite_score, 3),
        'recommendation': recommendation,
        'confidence_level': round(abs(composite_score) * 100, 1),
        'technical_indicators': tech_indicators,
        'oi_signal': symbol_oi_signal,
        'risk_management': {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'estimated_volatility': round(volatility_estimate * 100, 2)
        }
    }


async def main():
    """
    Main demo function
    """
    print("=" * 70)
    print("🚀 ENHANCED TRADING ANALYSIS SYSTEM - DEMO")
    print("Integrating OI Spike Detection with Technical Indicators")
    print("=" * 70)
    
    # Define symbols to analyze
    symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT']
    
    # Get mock OI signals
    oi_signals = get_mock_oi_signals(symbols)
    
    print(f"\n📊 Found {len(oi_signals)} OI signals from our radar:")
    for signal in oi_signals:
        print(f"   • {signal['symbol']}: {signal['direction']} (Score: {signal['score']})")
    
    print(f"\n📈 Analyzing {len(symbols)} symbols...")
    
    # Analyze each symbol
    results = []
    for symbol in symbols:
        print(f"\n--- Analyzing {symbol} ---")
        
        # Get simulated market data
        market_data = await simulate_binance_data(symbol)
        
        # Calculate technical indicators
        tech_indicators = calculate_technical_indicators(market_data['klines'])
        
        # Integrate with OI signals
        analysis = integrate_analysis(symbol, tech_indicators, oi_signals)
        
        results.append(analysis)
        
        # Display results
        print(f"Current Price: ${analysis['current_price']:.4f}")
        print(f"Composite Score: {analysis['composite_score']}")
        print(f"Recommendation: {analysis['recommendation']}")
        print(f"Confidence: {analysis['confidence_level']}%")
        
        if analysis['oi_signal']:
            oi_score = analysis['oi_signal']['score']
            oi_direction = analysis['oi_signal']['direction']
            print(f"OI Signal: {oi_direction} (Strength: {oi_score})")
        
        print(f"RSI: {tech_indicators['rsi']:.2f}")
        
        # Show risk management
        risk_mgmt = analysis['risk_management']
        if risk_mgmt['stop_loss']:
            print(f"Stop Loss: ${risk_mgmt['stop_loss']}")
            print(f"Take Profit: ${risk_mgmt['take_profit']}")
        print(f"Estimated Volatility: {risk_mgmt['estimated_volatility']}%")
    
    print(f"\n🎯 SUMMARY OF RECOMMENDATIONS:")
    print("-" * 40)
    
    # Sort by confidence level
    sorted_results = sorted(results, key=lambda x: x['confidence_level'], reverse=True)
    
    for analysis in sorted_results:
        if analysis['recommendation'] != 'HOLD':
            print(f"{analysis['symbol']:8} | {analysis['recommendation']:12} | "
                  f"Conf: {analysis['confidence_level']:4}% | Price: ${analysis['current_price']:.4f}")
    
    print("\n💡 NOTES:")
    print("• This demo integrates OI spike signals with technical indicators")
    print("• OI signals are given highest weight as they represent market sentiment shifts")
    print("• Risk management includes dynamic stop-loss and take-profit levels")
    print("• Confidence is calculated based on signal strength alignment")
    
    print("\n✅ Demo completed successfully!")
    print("The full system would connect to live APIs and provide real-time analysis.")


if __name__ == "__main__":
    asyncio.run(main())