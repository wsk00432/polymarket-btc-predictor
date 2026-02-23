"""
Main application for the Enhanced Trading Analysis System
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trading_system import EnhancedTradingSystem
from data_fetcher import DataFetcher, MockDataFetcher
from config import get_config, validate_config
from models import TradingSignal, TradingSignalPanel
from utils import setup_logging, generate_signal_summary
from backtester import run_sample_backtest


class TradingApp:
    """
    Main application class that orchestrates the enhanced trading system
    """
    
    def __init__(self, use_mock_data: bool = False):
        # Validate configuration
        if not validate_config():
            raise ValueError("Configuration validation failed")
        
        # Setup logging
        log_file = get_config('LOG_FILE')
        log_level = get_config('LOG_LEVEL')
        self.logger = setup_logging(log_file, log_level)
        
        # Initialize data fetcher
        if use_mock_data or get_config('SIMULATION_MODE'):
            self.data_fetcher = MockDataFetcher()
            self.logger.info("Using mock data fetcher for simulation")
        else:
            self.data_fetcher = DataFetcher()
            self.logger.info("Using real data fetcher")
        
        # Initialize trading system
        api_key = get_config('BINANCE_API_KEY')
        secret_key = get_config('BINANCE_SECRET_KEY')
        
        if api_key and secret_key:
            self.trading_system = EnhancedTradingSystem(api_key, secret_key)
            self.logger.info("Trading system initialized with API credentials")
        else:
            self.trading_system = EnhancedTradingSystem()
            self.logger.info("Trading system initialized without API credentials")
        
        self.running = False
        self.last_update_times = {}
    
    async def initialize(self):
        """
        Initialize the application components
        """
        self.logger.info("Initializing Enhanced Trading Analysis System")
        
        # Initialize async clients if needed
        await self.trading_system.initialize_async_client()
        
        self.logger.info("Application initialization complete")
    
    async def update_market_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Update market data for specified symbols
        """
        self.logger.info(f"Updating market data for {len(symbols)} symbols")
        
        # Fetch comprehensive data for all symbols
        symbol_data = await self.data_fetcher.fetch_multiple_symbols_data(symbols)
        
        # Store timestamps for tracking
        for symbol in symbols:
            self.last_update_times[symbol] = datetime.now()
        
        self.logger.info(f"Market data updated for {len([s for s in symbols if symbol_data.get(s, {})])} symbols")
        return symbol_data
    
    async def get_real_time_signals(self, symbols: List[str], oi_signals: Dict = None) -> TradingSignalPanel:
        """
        Generate real-time trading signals for specified symbols
        """
        self.logger.info(f"Generating real-time signals for {len(symbols)} symbols")
        
        # Update market data first
        market_data = await self.update_market_data(symbols)
        
        # Generate signal panel using the trading system
        signal_panel = await self.trading_system.generate_trading_signal_panel(symbols, oi_signals)
        
        # Create TradingSignalPanel object
        panel = TradingSignalPanel(
            timestamp=datetime.now(),
            signals=signal_panel,
            market_conditions={}  # Could include overall market conditions
        )
        
        self.logger.info(f"Generated {len(signal_panel)} trading signals")
        return panel
    
    async def run_continuous_monitoring(self, symbols: List[str], update_interval: int = None):
        """
        Run continuous monitoring of specified symbols
        """
        update_interval = update_interval or get_config('DATA_UPDATE_INTERVAL')
        
        self.logger.info(f"Starting continuous monitoring for {symbols}")
        self.running = True
        
        try:
            while self.running:
                try:
                    # Generate and display signals
                    panel = await self.get_real_time_signals(symbols)
                    
                    # Display summary of signals
                    print(f"\n{'='*60}")
                    print(f"REAL-TIME TRADING SIGNAL PANEL - {panel.timestamp}")
                    print(f"{'='*60}")
                    
                    for signal in panel.signals:
                        summary = generate_signal_summary(signal)
                        print(summary)
                    
                    print(f"{'='*60}")
                    
                    # Wait for next update
                    await asyncio.sleep(update_interval)
                    
                except Exception as e:
                    self.logger.error(f"Error during continuous monitoring: {e}")
                    await asyncio.sleep(5)  # Wait 5 seconds before retrying
                    
        except KeyboardInterrupt:
            self.logger.info("Continuous monitoring interrupted by user")
        finally:
            self.running = False
            self.logger.info("Continuous monitoring stopped")
    
    async def run_backtest_mode(self):
        """
        Run backtesting mode to evaluate strategies
        """
        self.logger.info("Running backtest mode")
        
        # Run the sample backtest
        results = await run_sample_backtest()
        
        self.logger.info("Backtest completed")
        return results
    
    async def export_signals(self, panel: TradingSignalPanel, filename: str = None):
        """
        Export trading signals to a file
        """
        if filename is None:
            filename = f"trading_signals_{int(datetime.now().timestamp())}.json"
        
        # Convert panel to dictionary
        panel_dict = panel.to_dict()
        
        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(panel_dict, f, indent=2, default=str)
        
        self.logger.info(f"Signals exported to {filename}")
    
    async def run_dashboard(self, symbols: List[str]):
        """
        Run a simple dashboard interface
        """
        self.logger.info("Starting trading dashboard")
        
        print("\n" + "="*80)
        print("ENHANCED TRADING ANALYSIS SYSTEM DASHBOARD")
        print("="*80)
        print(f"Monitoring symbols: {', '.join(symbols)}")
        print(f"Update interval: {get_config('DATA_UPDATE_INTERVAL')} seconds")
        print("Press Ctrl+C to exit")
        print("="*80)
        
        try:
            while True:
                # Get fresh signals
                panel = await self.get_real_time_signals(symbols)
                
                # Clear screen (simple approach)
                print("\033[2J\033[H")  # ANSI escape codes to clear screen
                
                # Print header
                print("\n" + "="*80)
                print(f"TRADING SIGNAL DASHBOARD - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*80)
                
                # Print each signal with formatting
                for signal in panel.signals:
                    print(f"\n🎯 SYMBOL: {signal.symbol}")
                    print(f"   Recommendation: {signal.recommendation.value:<12} | "
                          f"Score: {signal.composite_score:>6.3f} | "
                          f"Confidence: {signal.confidence_level:>5.1f}%")
                    
                    # Add technical details
                    if signal.technical_indicators:
                        ti = signal.technical_indicators
                        print(f"   Price: {ti.moving_averages.get('current_price', 'N/A'):>10.2f} | "
                              f"RSI: {ti.rsi:>5.2f}")
                    
                    # Add risk management
                    if signal.risk_management:
                        rm = signal.risk_management
                        if rm.stop_loss:
                            print(f"   Stop Loss: {rm.stop_loss:>10.2f}", end="")
                        if rm.take_profit:
                            print(f" | Take Profit: {rm.take_profit:>10.2f}")
                        else:
                            print()  # New line if no take profit
                    
                    # Add brief description
                    rec = signal.recommendation.value
                    if 'BUY' in rec:
                        desc = " Bullish momentum detected"
                    elif 'SELL' in rec:
                        desc = " Bearish momentum detected"
                    else:
                        desc = " Neutral market conditions"
                    print(f"   💡 {desc}")
                
                print("\n" + "="*80)
                print(f"Last updated: {datetime.now().strftime('%H:%M:%S')} | "
                      f"Next update in {get_config('DATA_UPDATE_INTERVAL')} seconds")
                
                # Wait before next update
                await asyncio.sleep(get_config('DATA_UPDATE_INTERVAL'))
                
        except KeyboardInterrupt:
            print("\nDashboard stopped by user.")
        except Exception as e:
            self.logger.error(f"Error in dashboard: {e}")
    
    async def close(self):
        """
        Clean up resources
        """
        self.data_fetcher.close()
        self.running = False
        self.logger.info("Application closed")


async def main():
    """
    Main entry point for the application
    """
    # Initialize the app with mock data (set to False to use real data)
    app = TradingApp(use_mock_data=True)
    
    try:
        # Initialize components
        await app.initialize()
        
        # Define symbols to monitor
        symbols = get_config('DEFAULT_SYMBOLS', ['BTCUSDT', 'ETHUSDT'])
        
        # Example OI signals (in a real system, these would come from your OI detection system)
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
        
        print("Choose mode:")
        print("1. Real-time signal panel")
        print("2. Dashboard view")
        print("3. Backtest mode")
        print("4. Single update")
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == '1':
            # Generate one-time signal panel
            panel = await app.get_real_time_signals(symbols, oi_signals)
            for signal in panel.signals:
                summary = generate_signal_summary(signal)
                print(summary)
        elif choice == '2':
            # Run dashboard
            await app.run_dashboard(symbols)
        elif choice == '3':
            # Run backtest
            await app.run_backtest_mode()
        elif choice == '4':
            # Single update with detailed output
            panel = await app.get_real_time_signals(symbols, oi_signals)
            await app.export_signals(panel)
            print(f"Signals generated and exported to file")
            for signal in panel.signals:
                print(generate_signal_summary(signal))
        else:
            print("Invalid choice. Running single update by default.")
            panel = await app.get_real_time_signals(symbols, oi_signals)
            for signal in panel.signals:
                print(generate_signal_summary(signal))
    
    except Exception as e:
        print(f"Error running application: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await app.close()


if __name__ == "__main__":
    asyncio.run(main())