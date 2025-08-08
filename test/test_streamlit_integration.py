#!/usr/bin/env python3
"""
Test Streamlit integration for range_bound strategy
"""

from backtesting import BacktestingEngine
from trading_algorithms import STRATEGIES, TradingAlgorithms
import pandas as pd
from datetime import datetime

def test_streamlit_integration():
    """Test how Streamlit app would call the range_bound strategy"""
    
    print("="*60)
    print("STREAMLIT INTEGRATION TEST")
    print("="*60)
    
    # Test parameters
    symbols = ['1579.T', '1360.T']
    start_date = '2023-01-01'
    end_date = '2025-08-05'
    
    # Check if range_bound is in STRATEGIES
    print(f"📋 Available strategies: {list(STRATEGIES.keys())}")
    
    if 'range_bound' not in STRATEGIES:
        print("❌ ERROR: range_bound not found in STRATEGIES!")
        return
    
    print("✅ range_bound found in STRATEGIES")
    
    # Test 1: Direct strategy call (like Streamlit would do)
    print(f"\n🧪 TEST 1: Direct strategy call")
    
    engine = BacktestingEngine(
        initial_capital=1000000,
        transaction_cost=0.002,
        slippage=0.001,
        stop_loss=0.0,
        take_profit=0.0
    )
    
    # Default parameters (like Streamlit defaults)
    strategy_params = {
        'lookback_period': 60,
        'range_threshold': 0.15,
        'oversold_percentile': 20,
        'overbought_percentile': 80,
        'position_size': 0.20,
        'no_stop_loss': True
    }
    
    print(f"📊 Strategy parameters: {strategy_params}")
    
    result1 = engine.run_backtest(
        trading_algorithm=STRATEGIES['range_bound'],
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        **strategy_params
    )
    
    print(f"📈 RESULT 1:")
    print(f"Final Value: ¥{result1['final_value']:,.0f}")
    print(f"Total Return: {result1['total_return']:.2f}%")
    print(f"Total Trades: {result1['total_trades']}")
    
    # Test 2: Manual strategy call (like our test script)
    print(f"\n🧪 TEST 2: Manual strategy call")
    
    def manual_range_bound_strategy(data, current_prices):
        return TradingAlgorithms.range_bound_strategy(
            data, current_prices,
            lookback_period=60,
            range_threshold=0.15,
            oversold_percentile=20,
            overbought_percentile=80,
            position_size=0.20,
            no_stop_loss=True
        )
    
    result2 = engine.run_backtest(
        trading_algorithm=manual_range_bound_strategy,
        symbols=symbols,
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"📈 RESULT 2:")
    print(f"Final Value: ¥{result2['final_value']:,.0f}")
    print(f"Total Return: {result2['total_return']:.2f}%")
    print(f"Total Trades: {result2['total_trades']}")
    
    # Compare results
    print(f"\n🔍 COMPARISON:")
    print(f"Result 1 (STRATEGIES): ¥{result1['final_value']:,.0f} ({result1['total_return']:.2f}%)")
    print(f"Result 2 (Manual): ¥{result2['final_value']:,.0f} ({result2['total_return']:.2f}%)")
    
    if abs(result1['total_return'] - result2['total_return']) < 0.1:
        print("✅ Results match - Streamlit integration should work!")
    else:
        print("❌ Results don't match - there's an issue!")
    
    return result1, result2

if __name__ == "__main__":
    test_streamlit_integration() 