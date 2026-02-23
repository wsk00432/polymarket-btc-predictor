"""
Example usage of the Enhanced Trading Analysis System
Demonstrates integration of all components with real API connectivity
"""

import asyncio
import json
from datetime import datetime

from .trading_system import EnhancedTradingSystem
from .api_integration import get_api_manager, get_symbol_data, get_multiple_symbols_data_cached
from .config import get_config, validate_config
from .utils import generate_signal_summary


async def example_basic_usage():
    """
    Example of basic usage of the trading system
    """
    print("=== BASIC USAGE EXAMPLE ===")
    
    # Initialize the trading system
    trading_system = EnhancedTradingSystem()
    await trading_system.initialize_async_client()
    
    # Define symbols to analyze
    symbols = ['BTCUSDT', 'ETHUSDT']
    
    # Example OI signals (would come from your OI detection system)
    oi_signals = {
        'BTCUSDT': {
            'magnitude': 12.5,
            'direction': 'BULLISH',
            'timestamp': datetime.now().isoformat()
        },
        'ETHUSDT': {
            'magnitude': 7.2,
            'direction': 'BEARISH',
            'timestamp': datetime.now().isoformat()
        }
    }
    
    print(f"Analyzing symbols: {symbols}")
    
    # Generate trading signals
    signals = await trading_system.generate_trading_signal_panel(symbols, oi_signals)
    
    print("\nGenerated Signals:")
    for signal in signals:
        if signal:  # Check if signal is not empty
            summary = generate_signal_summary(signal)
            print(f"  {summary}")
    
    print("\nBasic usage example completed.\n")


async def example_detailed_analysis():
    """
    Example of detailed analysis with individual component usage
    """
    print("=== DETAILED ANALYSIS EXAMPLE ===")
    
    # Get API manager directly
    api_manager = await get_api_manager()
    
    symbol = 'BTCUSDT'
    print(f"Performing detailed analysis for {symbol}")
    
    # Get comprehensive market data
    market_data = await get_symbol_data(symbol)
    print(f"Current price: {market_data.get('price', 'N/A')}")
    
    # Get technical indicators
    trading_system = EnhancedTradingSystem()
    await trading_system.initialize_async_client()
    
    tech_indicators = await trading_system.get_technical_indicators(symbol)
    if tech_indicators:
        print(f"RSI: {tech_indicators.get('rsi', 'N/A')}")
        print(f"Current price: {tech_indicators['moving_averages'].get('current_price', 'N/A')}")
    
    # Get order book depth
    order_book = await trading_system.get_order_book_depth(symbol)
    if order_book:
        print(f"Bid volume: {order_book.bid_volume}")
        print(f"Ask volume: {order_book.ask_volume}")
        print(f"Spread: {order_book.spread_percentage:.4f}%")
    
    print("\nDetailed analysis example completed.\n")


async def example_multi_symbol_monitoring():
    """
    Example of monitoring multiple symbols simultaneously
    """
    print("=== MULTI-SYMBOL MONITORING EXAMPLE ===")
    
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT']
    
    # Get data for all symbols at once
    all_data = await get_multiple_symbols_data_cached(symbols)
    
    print("Market data for monitored symbols:")
    for symbol in symbols:
        data = all_data.get(symbol, {})
        price = data.get('price', 'N/A')
        ticker_24h = data.get('ticker_24h', {})
        price_change = ticker_24h.get('priceChangePercent', 'N/A')
        
        print(f"  {symbol}: ${price} ({price_change}%)")
    
    # Generate comprehensive signals for all symbols
    trading_system = EnhancedTradingSystem()
    await trading_system.initialize_async_client()
    
    # Create mock OI signals for this example
    oi_signals = {}
    for symbol in symbols:
        import random
        oi_signals[symbol] = {
            'magnitude': random.uniform(5, 15),
            'direction': 'BULLISH' if random.random() > 0.5 else 'BEARISH',
            'timestamp': datetime.now().isoformat()
        }
    
    signals = await trading_system.generate_trading_signal_panel(symbols, oi_signals)
    
    print("\nTrading Signals:")
    for signal in signals:
        if signal:
            summary = generate_signal_summary(signal)
            print(f"  {summary}")
    
    print("\nMulti-symbol monitoring example completed.\n")


async def example_risk_management():
    """
    Example demonstrating the risk management features
    """
    print("=== RISK MANAGEMENT EXAMPLE ===")
    
    trading_system = EnhancedTradingSystem()
    await trading_system.initialize_async_client()
    
    symbol = 'BTCUSDT'
    
    # Get current price
    market_data = await get_symbol_data(symbol)
    current_price = market_data.get('price', 0)
    
    print(f"Current {symbol} price: ${current_price}")
    
    # Demonstrate dynamic stop-loss and take-profit calculation
    # For a LONG position with 2% risk and current market volatility
    risk_params = trading_system.calculate_dynamic_stop_loss_take_profit(
        entry_price=current_price,
        position_type='LONG',
        volatility=3.5  # Example volatility %
    )
    
    print(f"Suggested stop-loss: ${risk_params['stop_loss']}")
    print(f"Suggested take-profit: ${risk_params['take_profit']}")
    print(f"Risk percentage: {risk_params['risk_percentage']}%")
    print(f"Risk-reward ratio: {risk_params['risk_reward_ratio']}:1")
    
    print("\nRisk management example completed.\n")


async def example_comprehensive_workflow():
    """
    Complete workflow example combining all system components
    """
    print("=== COMPREHENSIVE WORKFLOW EXAMPLE ===")
    
    # Initialize components
    trading_system = EnhancedTradingSystem()
    await trading_system.initialize_async_client()
    
    # Define universe of symbols to monitor
    symbols = get_config('DEFAULT_SYMBOLS', ['BTCUSDT', 'ETHUSDT'])
    print(f"Monitoring universe: {symbols[:5]}...")  # Show first 5
    
    # Step 1: Get latest market data
    print("\n1. Fetching market data...")
    market_data = await get_multiple_symbols_data_cached(symbols[:5])  # Limit for example
    
    # Step 2: Analyze technicals for each symbol
    print("2. Analyzing technical indicators...")
    technical_data = {}
    for symbol in symbols[:5]:
        tech = await trading_system.get_technical_indicators(symbol)
        technical_data[symbol] = tech
    
    # Step 3: Perform fund flow analysis
    print("3. Analyzing fund flows...")
    fund_flow_data = {}
    for symbol in symbols[:5]:
        flow = await trading_system.analyze_fund_flow(symbol)
        fund_flow_data[symbol] = flow
    
    # Step 4: Generate integrated signals (with mock OI signals)
    print("4. Generating integrated signals...")
    oi_signals = {}
    for symbol in symbols[:5]:
        import random
        oi_signals[symbol] = {
            'magnitude': random.uniform(3, 20),
            'direction': 'BULLISH' if random.random() > 0.4 else 'BEARISH',
            'timestamp': datetime.now().isoformat()
        }
    
    signals = await trading_system.generate_trading_signal_panel(symbols[:5], oi_signals)
    
    # Step 5: Display results
    print("5. Results:")
    print("-" * 80)
    for signal in signals:
        if signal:
            summary = generate_signal_summary(signal)
            print(f"  {summary}")
    
    print("-" * 80)
    print("\nComprehensive workflow example completed.\n")


async def run_all_examples():
    """
    Run all examples sequentially
    """
    print("ENHANCED TRADING ANALYSIS SYSTEM - INTEGRATION EXAMPLES")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        await example_basic_usage()
        await example_detailed_analysis()
        await example_multi_symbol_monitoring()
        await example_risk_management()
        await example_comprehensive_workflow()
        
        print("=" * 60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error during examples: {e}")
        import traceback
        traceback.print_exc()
    
    # Cleanup
    from .api_integration import cleanup_api_resources
    await cleanup_api_resources()


if __name__ == "__main__":
    # Validate configuration first
    if not validate_config():
        print("Configuration validation failed!")
    else:
        print("Configuration validated successfully.")
    
    # Run examples
    asyncio.run(run_all_examples())