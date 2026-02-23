#!/usr/bin/env python3
"""
Monitoring script for the Enhanced Trading Analysis System
Runs continuous analysis and displays results
"""

import asyncio
import time
import logging
from datetime import datetime
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core_engine import EnhancedTradingSystem
from oi_radar_integration import OISpikeRadarIntegration


async def run_monitoring():
    """
    Run continuous monitoring of the trading system
    """
    print("=" * 80)
    print("🚀 ENHANCED TRADING ANALYSIS SYSTEM - MONITORING MODE")
    print("Running continuous analysis with integrated OI Spike + Technical Indicators")
    print("=" * 80)
    
    # Initialize the trading system
    trading_system = EnhancedTradingSystem()
    
    # Define symbols to monitor (top liquid pairs)
    symbols = [
        'BTCUSDT', 
        'ETHUSDT', 
        'SOLUSDT'
    ]
    
    print(f"\n🔍 Monitoring {len(symbols)} symbols:")
    for symbol in symbols:
        print(f"   • {symbol}")
    
    print("\n📊 Starting continuous analysis (updates every 30 seconds)...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running analysis...")
            
            try:
                # Generate comprehensive trading signal panel
                signal_panel = await trading_system.generate_trading_signal_panel(symbols)
                
                if signal_panel:
                    print(f"\n📋 LATEST SIGNALS:")
                    print("-" * 60)
                    
                    for signal in signal_panel:
                        symbol = signal['symbol']
                        rec = signal['recommendation']
                        conf = signal['confidence_level']
                        price = signal.get('current_price', 'N/A')
                        comp_score = signal['composite_score']
                        
                        print(f"• {symbol:8} | {rec:12} | Conf: {conf:5.1f}% | Score: {comp_score:+.3f} | Price: {price}")
                        
                        # Show key technical indicators if available
                        tech_ind = signal.get('technical_indicators', {})
                        if tech_ind:
                            rsi = tech_ind.get('rsi', 'N/A')
                            if rsi != 'N/A':
                                print(f"    RSI: {rsi:.2f}")
                        
                        # Show risk management if available
                        risk_mgmt = signal.get('risk_management', {})
                        if risk_mgmt.get('stop_loss'):
                            sl = risk_mgmt['stop_loss']
                            tp = risk_mgmt['take_profit']
                            print(f"    Risk Mgmt: SL {sl} | TP {tp}")
                
                    # Summary
                    total_analyzed = len(signal_panel)
                    buy_signals = len([s for s in signal_panel if 'BUY' in s['recommendation']])
                    sell_signals = len([s for s in signal_panel if 'SELL' in s['recommendation']])
                    hold_signals = len([s for s in signal_panel if s['recommendation'] == 'HOLD'])
                    
                    print(f"\n📈 Summary: {total_analyzed} analyzed | {buy_signals} buys | {sell_signals} sells | {hold_signals} holds")
                else:
                    print("⚠️  No signals generated (may be due to API limitations)")
            
            except Exception as e:
                print(f"⚠️  Error during analysis: {e}")
                import traceback
                traceback.print_exc()
            
            print("-" * 80)
            
            # Wait before next analysis
            await asyncio.sleep(30)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Monitoring stopped by user at {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_monitoring())