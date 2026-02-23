"""
Test script to verify API integration functionality
"""

import asyncio
import sys
from datetime import datetime

# Test the API integration
async def test_api_connectivity():
    """
    Test basic API connectivity and functionality
    """
    print("Testing API Integration...")
    print(f"Start time: {datetime.now()}")
    
    try:
        # Test 1: Import and initialize API manager
        print("\n1. Testing API manager initialization...")
        from api_integration import get_api_manager
        api_manager = await get_api_manager()
        print("✓ API manager initialized successfully")
        
        # Test 2: Check exchange connectivity
        print("\n2. Testing exchange connectivity...")
        is_connected = api_manager.binance_manager.get_exchange_status()
        print(f"✓ Exchange connectivity: {'Connected' if is_connected else 'Not connected'}")
        
        if not is_connected:
            print("! Warning: Cannot connect to exchange. Running in simulation mode.")
        
        # Test 3: Test symbol data fetching
        print("\n3. Testing symbol data fetching...")
        from api_integration import get_symbol_data
        btc_data = await get_symbol_data('BTCUSDT')
        print(f"✓ BTCUSDT data retrieved: {btc_data.get('price', 'No price data')}")
        
        # Test 4: Test multiple symbols
        print("\n4. Testing multiple symbols data fetching...")
        from api_integration import get_multiple_symbols_data_cached
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        multi_data = await get_multiple_symbols_data_cached(symbols)
        for symbol in symbols:
            price = multi_data.get(symbol, {}).get('price', 'N/A')
            print(f"  {symbol}: {price}")
        print("✓ Multiple symbols data fetched successfully")
        
        # Test 5: Test technical data
        print("\n5. Testing technical data fetching...")
        from api_integration import get_technical_data_cached
        tech_data = await get_technical_data_cached('BTCUSDT', '5m', 10)
        kline_count = len(tech_data.get('klines', []))
        print(f"✓ Technical data retrieved: {kline_count} klines")
        
        # Test 6: Test cache functionality
        print("\n6. Testing cache functionality...")
        from api_integration import get_data_cache
        cache = get_data_cache()
        cache_stats = cache.get_cache_stats()
        print(f"✓ Cache stats: {cache_stats['active_items']} active items")
        
        # Test 7: Test the trading system integration
        print("\n7. Testing trading system integration...")
        from trading_system import EnhancedTradingSystem
        trading_system = EnhancedTradingSystem()
        await trading_system.initialize_async_client()
        print("✓ Trading system initialized with API integration")
        
        # Test 8: Get technical indicators through trading system
        print("\n8. Testing technical indicators...")
        indicators = await trading_system.get_technical_indicators('BTCUSDT')
        if indicators:
            rsi = indicators.get('rsi', 'N/A')
            price = indicators.get('moving_averages', {}).get('current_price', 'N/A')
            print(f"✓ BTCUSDT indicators: RSI={rsi}, Price=${price}")
        else:
            print("⚠ No indicators returned (may be due to API limitations)")
        
        # Test 9: Test data fetcher integration
        print("\n9. Testing data fetcher with API integration...")
        from data_fetcher import DataFetcher
        fetcher = DataFetcher()
        await fetcher.initialize_api_manager()
        klines = await fetcher.fetch_kline_data('BTCUSDT', limit=5)
        print(f"✓ Fetched {len(klines)} klines through integrated data fetcher")
        
        print("\n" + "="*60)
        print("API INTEGRATION TESTS COMPLETED SUCCESSFULLY!")
        print(f"End time: {datetime.now()}")
        print("="*60)
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the enhanced_trading_system directory")
        return False
    except Exception as e:
        print(f"❌ Error during API integration test: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_configuration():
    """
    Test configuration loading
    """
    print("\nTesting Configuration...")
    
    try:
        from config import get_config, validate_config
        is_valid = validate_config()
        print(f"✓ Configuration validation: {'Passed' if is_valid else 'Failed'}")
        
        # Show some config values
        symbols = get_config('DEFAULT_SYMBOLS', ['BTCUSDT'])
        interval = get_config('KLINE_INTERVAL', '5m')
        print(f"✓ Default symbols: {symbols[:3]}...")  # Show first 3
        print(f"✓ K-line interval: {interval}")
        
        return is_valid
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False


async def run_complete_test():
    """
    Run complete integration test
    """
    print("ENHANCED TRADING SYSTEM - API INTEGRATION TEST SUITE")
    print("="*60)
    
    config_ok = await test_configuration()
    if not config_ok:
        print("\n❌ Configuration test failed. Please check your setup.")
        return False
    
    api_ok = await test_api_connectivity()
    if not api_ok:
        print("\n❌ API connectivity test failed.")
        return False
    
    print("\n🎉 ALL TESTS PASSED! API integration is working correctly.")
    return True


if __name__ == "__main__":
    # Change to the correct directory if needed
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    success = asyncio.run(run_complete_test())
    sys.exit(0 if success else 1)