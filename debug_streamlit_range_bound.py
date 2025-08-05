#!/usr/bin/env python3
"""
Debug script to test range_bound strategy with Streamlit app parameters
"""

from backtesting import BacktestingEngine
from trading_algorithms import TradingAlgorithms
import pandas as pd
from datetime import datetime

def debug_streamlit_range_bound():
    """Test range_bound strategy with default Streamlit parameters"""
    
    print("="*60)
    print("DEBUG: STREAMLIT RANGE-BOUND STRATEGY")
    print("="*60)
    
    # Test parameters (default Streamlit values)
    symbols = ['1579.T', '1360.T']
    start_date = '2023-01-01'
    end_date = '2025-08-05'
    
    # Default Streamlit parameters
    lookback_period = 60
    range_threshold = 0.15
    oversold_percentile = 20
    overbought_percentile = 80
    position_size = 0.20
    
    print(f"📊 Testing with Streamlit default parameters:")
    print(f"Lookback Period: {lookback_period} days")
    print(f"Range Threshold: {range_threshold:.1%}")
    print(f"Oversold Percentile: {oversold_percentile}%")
    print(f"Overbought Percentile: {overbought_percentile}%")
    print(f"Position Size: {position_size:.1%}")
    
    # Initialize backtesting engine with NO stop-loss
    engine = BacktestingEngine(
        initial_capital=1000000,
        transaction_cost=0.002,
        slippage=0.001,
        stop_loss=0.0,  # NO STOP LOSS for range-bound strategy
        take_profit=0.0  # NO TAKE PROFIT
    )
    
    def range_bound_strategy(data, current_prices):
        return TradingAlgorithms.range_bound_strategy(
            data, current_prices,
            lookback_period=lookback_period,
            range_threshold=range_threshold,
            oversold_percentile=oversold_percentile,
            overbought_percentile=overbought_percentile,
            position_size=position_size,
            no_stop_loss=True
        )
    
    print(f"\n🚀 Running backtest...")
    result = engine.run_backtest(
        trading_algorithm=range_bound_strategy,
        symbols=symbols,
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"\n📈 RESULTS:")
    print(f"Final Value: ¥{result['final_value']:,.0f}")
    print(f"Total Return: {result['total_return']:.2f}%")
    print(f"Max Drawdown: {result['max_drawdown']:.2f}%")
    print(f"Total Trades: {result['total_trades']}")
    print(f"Realized P&L: ¥{result.get('realized_pnl', 0):,.0f}")
    print(f"Win Rate: {result.get('win_rate', 0):.1f}%")
    
    # Analyze trades
    if result['trade_history']:
        trades_df = pd.DataFrame(result['trade_history'])
        buy_trades = trades_df[trades_df['action'] == 'BUY']
        sell_trades = trades_df[trades_df['action'] == 'SELL']
        
        print(f"\n📋 TRADE ANALYSIS:")
        print(f"Buy Trades: {len(buy_trades)}")
        print(f"Sell Trades: {len(sell_trades)}")
        
        if len(sell_trades) > 0 and 'pnl' in sell_trades.columns:
            profitable_trades = sell_trades[sell_trades['pnl'] > 0]
            losing_trades = sell_trades[sell_trades['pnl'] < 0]
            
            print(f"Profitable Trades: {len(profitable_trades)}")
            print(f"Losing Trades: {len(losing_trades)}")
            
            if len(profitable_trades) > 0:
                print(f"Average Profit: ¥{profitable_trades['pnl'].mean():,.0f}")
            if len(losing_trades) > 0:
                print(f"Average Loss: ¥{losing_trades['pnl'].mean():,.0f}")
    
    # Check if strategy is being called correctly
    print(f"\n🔍 DEBUG INFO:")
    print(f"Strategy function: {range_bound_strategy.__name__}")
    print(f"Available strategies: {list(TradingAlgorithms.STRATEGIES.keys()) if hasattr(TradingAlgorithms, 'STRATEGIES') else 'Not found'}")
    
    return result

if __name__ == "__main__":
    debug_streamlit_range_bound() 