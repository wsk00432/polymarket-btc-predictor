#!/usr/bin/env python3
"""
Enhanced Trading Analysis System
Complete system to integrate OI Spike Radar with technical indicators for better trading decisions
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List

from .core_engine import EnhancedTradingSystem
from .api_integration import OISpikeRadarIntegration
from .config import LOG_LEVEL, LOG_FILE

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def run_enhanced_analysis():
    """
    Run the enhanced trading analysis system
    """
    print("=" * 80)
    print("🚀 ENHANCED TRADING ANALYSIS SYSTEM")
    print("Integrating OI Spike Detection with Technical Indicators for 5-min Scalping")
    print("=" * 80)
    
    # Initialize the trading system
    # Note: Without API keys, the system will work with simulated data where possible
    trading_system = EnhancedTradingSystem()
    
    # Define symbols to analyze (top liquid pairs)
    symbols = [
        'BTCUSDT', 
        'ETHUSDT', 
        'SOLUSDT', 
        'XRPUSDT', 
        'ADAUSDT',
        'DOGEUSDT',
        'DOTUSDT',
        'AVAXUSDT'
    ]
    
    print(f"\n🔍 Analyzing {len(symbols)} symbols with integrated data sources...")
    print("• OI Spike Radar signals")
    print("• Technical indicators (RSI, MACD, Bollinger Bands, Moving Averages)")
    print("• Order book depth analysis")
    print("• Fund flow analysis")
    print("• Risk management calculations")
    
    try:
        # Generate comprehensive trading signal panel
        signal_panel = await trading_system.generate_trading_signal_panel(symbols)
        
        print(f"\n📋 ANALYSIS RESULTS:")
        print("-" * 80)
        
        # Sort by confidence level to highlight highest conviction trades
        sorted_signals = sorted(signal_panel, key=lambda x: x['confidence_level'], reverse=True)
        
        strong_signals = []
        moderate_signals = []
        weak_signals = []
        
        for signal in sorted_signals:
            if signal['confidence_level'] >= 60:
                strong_signals.append(signal)
            elif signal['confidence_level'] >= 30:
                moderate_signals.append(signal)
            else:
                weak_signals.append(signal)
        
        # Display strong signals first
        if strong_signals:
            print("\n🔥 HIGH CONFIDENCE SIGNALS (>60%):")
            print("-" * 50)
            for signal in strong_signals:
                symbol = signal['symbol']
                rec = signal['recommendation']
                conf = signal['confidence_level']
                price = signal['current_price']
                comp_score = signal['composite_score']
                
                print(f"• {symbol:8} | {rec:12} | Conf: {conf:5.1f}% | Score: {comp_score:+.3f} | Price: ${price:.4f}")
                
                # Show key metrics
                tech_ind = signal['technical_indicators']
                rsi = tech_ind.get('rsi', 0)
                ma_data = tech_ind.get('moving_averages', {})
                ma_5 = ma_data.get('ma_5', 0)
                ma_20 = ma_data.get('ma_20', 0)
                
                print(f"    RSI: {rsi:.2f} | MA5: {ma_5:.4f} | MA20: {ma_20:.4f}")
                
                # Show risk management
                risk_mgmt = signal['risk_management']
                if risk_mgmt['stop_loss']:
                    sl = risk_mgmt['stop_loss']
                    tp = risk_mgmt['take_profit']
                    risk_pct = risk_mgmt['risk_percentage']
                    print(f"    Risk Mgmt: SL ${sl:.4f} | TP ${tp:.4f} | Risk: {risk_pct:.2f}%")
        
        # Display moderate signals
        if moderate_signals:
            print("\n💡 MODERATE CONFIDENCE SIGNALS (30-60%):")
            print("-" * 50)
            for signal in moderate_signals:
                symbol = signal['symbol']
                rec = signal['recommendation']
                conf = signal['confidence_level']
                price = signal['current_price']
                comp_score = signal['composite_score']
                
                print(f"• {symbol:8} | {rec:12} | Conf: {conf:5.1f}% | Score: {comp_score:+.3f} | Price: ${price:.4f}")
        
        # Display weak signals (for awareness)
        if weak_signals:
            print("\n📊 LOW CONFIDENCE SIGNALS (<30%):")
            print("-" * 50)
            for signal in weak_signals:
                symbol = signal['symbol']
                rec = signal['recommendation']
                conf = signal['confidence_level']
                price = signal['current_price']
                comp_score = signal['composite_score']
                
                print(f"• {symbol:8} | {rec:12} | Conf: {conf:5.1f}% | Score: {comp_score:+.3f} | Price: ${price:.4f}")
        
        # Summary statistics
        print(f"\n📈 SYSTEM STATISTICS:")
        print("-" * 30)
        total_analyzed = len(signal_panel)
        buy_signals = len([s for s in signal_panel if 'BUY' in s['recommendation']])
        sell_signals = len([s for s in signal_panel if 'SELL' in s['recommendation']])
        hold_signals = len([s for s in signal_panel if s['recommendation'] == 'HOLD'])
        
        print(f"Total analyzed: {total_analyzed}")
        print(f"Buy signals: {buy_signals}")
        print(f"Sell signals: {sell_signals}")
        print(f"Hold signals: {hold_signals}")
        print(f"High confidence (>60%): {len(strong_signals)}")
        print(f"Moderate confidence (30-60%): {len(moderate_signals)}")
        
        # Show top opportunities
        print(f"\n🎯 TOP OPPORTUNITIES FOR 5-MIN SCALPING:")
        print("-" * 50)
        
        # Filter for scalping-appropriate signals (moderate+ confidence)
        scalp_opportunities = [s for s in signal_panel if s['confidence_level'] >= 30]
        
        for signal in scalp_opportunities[:5]:  # Top 5
            symbol = signal['symbol']
            rec = signal['recommendation']
            conf = signal['confidence_level']
            current_price = signal['current_price']
            volatility = signal['volatility']
            
            # Get technical details
            tech_ind = signal['technical_indicators']
            rsi = tech_ind.get('rsi', 0)
            bb_data = tech_ind.get('bollinger_bands', {})
            bb_pos = (current_price - bb_data.get('lower', current_price)) / max(0.0001, (bb_data.get('upper', current_price) - bb_data.get('lower', current_price))) if bb_data else 0.5
            
            print(f"\n{symbol} ({rec}):")
            print(f"  • Confidence: {conf:.1f}%, Volatility: {volatility:.2f}%")
            print(f"  • Current Price: ${current_price:.4f}, RSI: {rsi:.2f}")
            print(f"  • BB Position: {bb_pos:.2f} (0=bottom, 1=top)")
            
            # Risk management details
            risk_mgmt = signal['risk_management']
            if risk_mgmt['stop_loss']:
                sl = risk_mgmt['stop_loss']
                tp = risk_mgmt['take_profit']
                print(f"  • Risk Mgmt: Stop-Loss=${sl:.4f}, Take-Profit=${tp:.4f}")
    
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        print(f"⚠️ Error during analysis: {e}")
    
    finally:
        # Clean up connections
        try:
            await trading_system.binance_api.close()
            await trading_system.oi_radar.close()
        except:
            pass  # Ignore cleanup errors
    
    print(f"\n✅ Enhanced Trading Analysis Complete!")
    print(f"System has integrated OI Spike signals with technical indicators")
    print(f"Ready for 5-minute scalping with proper risk management.")


def display_system_features():
    """
    Display the features of the enhanced trading system
    """
    print("\n🛠️  ENHANCED SYSTEM FEATURES:")
    print("-" * 40)
    print("✓ OI Spike Radar Integration")
    print("✓ Real-time Technical Indicators (RSI, MACD, BB, MA)")
    print("✓ Order Book Depth Analysis")
    print("✓ Fund Flow Analysis")
    print("✓ Composite Scoring Algorithm")
    print("✓ Dynamic Risk Management")
    print("✓ 5-Minute Scalping Optimized")
    print("✓ Confidence Level Assessment")
    print("✓ Automated Stop-Loss/Take-Profit")


async def main():
    """
    Main entry point
    """
    display_system_features()
    await run_enhanced_analysis()


if __name__ == "__main__":
    asyncio.run(main())