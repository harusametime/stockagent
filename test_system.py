#!/usr/bin/env python3
"""
Comprehensive test script for the trading system
"""

import sys
import traceback
from datetime import datetime, timedelta

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        import yfinance as yf
        print("✅ yfinance imported successfully")
    except ImportError as e:
        print(f"❌ yfinance import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    try:
        from backtesting import BacktestingEngine
        print("✅ BacktestingEngine imported successfully")
    except ImportError as e:
        print(f"❌ BacktestingEngine import failed: {e}")
        return False
    
    try:
        from trading_algorithms import STRATEGIES
        print("✅ Trading algorithms imported successfully")
    except ImportError as e:
        print(f"❌ Trading algorithms import failed: {e}")
        return False
    
    try:
        from live_trading import LiveTradingAgent
        print("✅ LiveTradingAgent imported successfully")
    except ImportError as e:
        print(f"❌ LiveTradingAgent import failed: {e}")
        return False
    
    return True

def test_data_fetching():
    """Test data fetching from Yahoo Finance"""
    print("\nTesting data fetching...")
    
    try:
        import yfinance as yf
        
        # Test fetching data for our ETFs
        symbols = ['1579.T', '1360.T']
        
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='5d')
            
            if not hist.empty:
                print(f"✅ Successfully fetched data for {symbol}")
                print(f"   Latest price: ¥{hist['Close'].iloc[-1]:.2f}")
            else:
                print(f"❌ No data available for {symbol}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Data fetching failed: {e}")
        return False

def test_backtesting():
    """Test backtesting engine"""
    print("\nTesting backtesting engine...")
    
    try:
        from backtesting import BacktestingEngine
        from trading_algorithms import STRATEGIES
        
        # Initialize engine
        engine = BacktestingEngine(initial_capital=1000000)
        
        # Test with a short period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Test mean reversion strategy
        result = engine.run_backtest(
            trading_algorithm=STRATEGIES['mean_reversion'],
            symbols=['1579.T', '1360.T'],
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        print(f"✅ Backtesting completed successfully")
        print(f"   Initial Capital: ¥{result['initial_capital']:,.0f}")
        print(f"   Final Value: ¥{result['final_value']:,.0f}")
        print(f"   Total Return: {result['total_return']:.2f}%")
        print(f"   Total Trades: {result['total_trades']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backtesting failed: {e}")
        traceback.print_exc()
        return False

def test_trading_algorithms():
    """Test trading algorithms"""
    print("\nTesting trading algorithms...")
    
    try:
        from trading_algorithms import STRATEGIES
        import pandas as pd
        import numpy as np
        
        # Create sample data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        sample_data = {
            '1579.T': pd.DataFrame({
                'Open': np.random.randn(len(dates)).cumsum() + 100,
                'High': np.random.randn(len(dates)).cumsum() + 102,
                'Low': np.random.randn(len(dates)).cumsum() + 98,
                'Close': np.random.randn(len(dates)).cumsum() + 100,
                'Volume': np.random.randint(1000, 10000, len(dates))
            }, index=dates),
            '1360.T': pd.DataFrame({
                'Open': np.random.randn(len(dates)).cumsum() + 200,
                'High': np.random.randn(len(dates)).cumsum() + 202,
                'Low': np.random.randn(len(dates)).cumsum() + 198,
                'Close': np.random.randn(len(dates)).cumsum() + 200,
                'Volume': np.random.randint(1000, 10000, len(dates))
            }, index=dates)
        }
        
        # Calculate technical indicators for sample data
        from backtesting import BacktestingEngine
        engine = BacktestingEngine()
        for symbol in sample_data:
            sample_data[symbol] = engine.calculate_technical_indicators(sample_data[symbol])
        
        current_prices = {'1579.T': 105.0, '1360.T': 205.0}
        
        # Test each strategy
        for strategy_name, strategy_func in STRATEGIES.items():
            try:
                signals = strategy_func(sample_data, current_prices)
                print(f"✅ {strategy_name}: Generated {len(signals)} signals")
            except Exception as e:
                print(f"❌ {strategy_name}: Failed - {e}")
                traceback.print_exc()
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Trading algorithms test failed: {e}")
        return False

def test_live_trading_setup():
    """Test live trading setup (without actual API calls)"""
    print("\nTesting live trading setup...")
    
    try:
        from live_trading import LiveTradingAgent
        
        # Initialize agent
        agent = LiveTradingAgent(initial_capital=1000000)
        
        print("✅ LiveTradingAgent initialized successfully")
        print(f"   Initial Capital: ¥{agent.initial_capital:,.0f}")
        print(f"   Positions: {agent.positions}")
        
        # Test data fetching
        data = agent.get_current_data(['1579.T', '1360.T'], lookback_days=10)
        
        if data:
            print(f"✅ Successfully fetched current data for {len(data)} symbols")
        else:
            print("⚠️ No current data available (this is normal if market is closed)")
        
        return True
        
    except Exception as e:
        print(f"❌ Live trading setup failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running comprehensive system tests...")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Data Fetching Test", test_data_fetching),
        ("Trading Algorithms Test", test_trading_algorithms),
        ("Backtesting Test", test_backtesting),
        ("Live Trading Setup Test", test_live_trading_setup)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Set up your .env file with KabusAPI credentials")
        print("2. Run: python test_backtesting.py")
        print("3. Run: streamlit run app.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 