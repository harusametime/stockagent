#!/usr/bin/env python3
"""
Test the range-bound trading strategy for Nikkei 225 ETFs
"""

from backtesting import BacktestingEngine
from trading_algorithms import TradingAlgorithms
import pandas as pd
import numpy as np
from datetime import datetime

def test_range_bound_strategy():
    """Test the range-bound strategy with different parameters"""
    
    print("="*60)
    print("RANGE-BOUND STRATEGY TEST")
    print("="*60)
    
    # Test parameters
    symbols = ['1579.T', '1360.T']
    start_date = '2023-01-01'
    end_date = '2025-08-05'
    
    # Test different range-bound configurations
    configs = [
        {
            'name': 'Conservative Range-Bound',
            'lookback_period': 60,
            'range_threshold': 0.15,
            'oversold_percentile': 20,
            'overbought_percentile': 80,
            'position_size': 0.2
        },
        {
            'name': 'Aggressive Range-Bound',
            'lookback_period': 30,
            'range_threshold': 0.20,
            'oversold_percentile': 15,
            'overbought_percentile': 85,
            'position_size': 0.25
        },
        {
            'name': 'Patient Range-Bound',
            'lookback_period': 90,
            'range_threshold': 0.12,
            'oversold_percentile': 25,
            'overbought_percentile': 75,
            'position_size': 0.15
        }
    ]
    
    results = {}
    
    for config in configs:
        print(f"\n📊 Testing: {config['name']}")
        print("-" * 40)
        
        # Initialize backtesting engine with NO stop-loss for range-bound strategy
        engine = BacktestingEngine(
            initial_capital=1000000,
            transaction_cost=0.002,
            slippage=0.001,
            stop_loss=0.0,  # NO STOP LOSS for range-bound strategy
            take_profit=0.0  # NO TAKE PROFIT - let it run
        )
        
        def range_bound_strategy(data, current_prices):
            return TradingAlgorithms.range_bound_strategy(
                data, current_prices,
                lookback_period=config['lookback_period'],
                range_threshold=config['range_threshold'],
                oversold_percentile=config['oversold_percentile'],
                overbought_percentile=config['overbought_percentile'],
                position_size=config['position_size'],
                no_stop_loss=True
            )
        
        result = engine.run_backtest(
            trading_algorithm=range_bound_strategy,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date
        )
        
        results[config['name']] = result
        
        print(f"Final Value: ¥{result['final_value']:,.0f}")
        print(f"Total Return: {result['total_return']:.2f}%")
        print(f"Max Drawdown: {result['max_drawdown']:.2f}%")
        print(f"Total Trades: {result['total_trades']}")
        print(f"Realized P&L: ¥{result.get('realized_pnl', 0):,.0f}")
        print(f"Win Rate: {result.get('win_rate', 0):.1f}%")
        
        # Analyze trade patterns
        if result['trade_history']:
            trades_df = pd.DataFrame(result['trade_history'])
            buy_trades = trades_df[trades_df['action'] == 'BUY']
            sell_trades = trades_df[trades_df['action'] == 'SELL']
            
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
    
    # Compare results
    print(f"\n" + "="*60)
    print("RANGE-BOUND STRATEGY COMPARISON")
    print("="*60)
    
    comparison_data = []
    for name, result in results.items():
        comparison_data.append({
            'Strategy': name,
            'Final Value': result['final_value'],
            'Total Return (%)': result['total_return'],
            'Max Drawdown (%)': result['max_drawdown'],
            'Total Trades': result['total_trades'],
            'Realized P&L': result.get('realized_pnl', 0),
            'Win Rate (%)': result.get('win_rate', 0)
        })
    
    df_comparison = pd.DataFrame(comparison_data)
    print(df_comparison.to_string(index=False))
    
    print(f"\n💡 RANGE-BOUND STRATEGY INSIGHTS:")
    print("1. **No Stop-Losses**: Designed to hold through temporary dips")
    print("2. **Range Detection**: Automatically detects range-bound vs trending markets")
    print("3. **Percentile-Based**: Buys at range lows, sells at range highs")
    print("4. **Patience**: Waits for proper entry/exit points")
    print("5. **Nikkei-Specific**: Optimized for Nikkei 225's range-bound behavior")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    print("1. **Use Conservative settings** for stable returns")
    print("2. **Monitor range detection** - ensure it's identifying ranges correctly")
    print("3. **Consider position sizing** - larger positions in confirmed ranges")
    print("4. **Patience is key** - don't panic during temporary dips")
    print("5. **Combine with fundamental analysis** for better entry timing")
    
    return results

if __name__ == "__main__":
    test_range_bound_strategy() 