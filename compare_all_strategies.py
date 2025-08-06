#!/usr/bin/env python3
"""
Comprehensive strategy comparison with corrected price data
"""

from backtesting import BacktestingEngine
from trading_algorithms import STRATEGIES, TradingAlgorithms
import pandas as pd
from datetime import datetime

def compare_all_strategies():
    """Compare all trading strategies with corrected price data"""
    
    print("="*80)
    print("COMPREHENSIVE STRATEGY COMPARISON")
    print("="*80)
    
    # Test parameters
    symbols = ['1579.T', '1360.T']
    start_date = '2023-01-01'
    end_date = '2025-08-05'
    
    # Strategy configurations
    strategy_configs = {
        'mean_reversion': {
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'bb_std_multiplier': 2.0
        },
        'momentum': {
            'macd_threshold': 0.0,
            'volume_threshold': 1.5
        },
        'pairs_trading': {
            'correlation_threshold': 0.7,
            'z_score_threshold': 2.0
        },
        'trend_following': {
            'short_window': 10,
            'long_window': 30
        },
        'volatility_breakout': {
            'atr_period': 14,
            'breakout_multiplier': 2.0
        },
        'range_bound': {
            'lookback_period': 60,
            'range_threshold': 0.15,
            'oversold_percentile': 20,
            'overbought_percentile': 80,
            'position_size': 0.20,
            'no_stop_loss': True
        },
        'combined': {
            'max_position_size': 0.15,
            'transaction_cost': 0.002
        }
    }
    
    results = {}
    
    for strategy_name in STRATEGIES.keys():
        print(f"\n📊 Testing: {strategy_name.upper()}")
        print("-" * 50)
        
        # Initialize backtesting engine
        if strategy_name == "range_bound":
            # No stop-loss for range-bound strategy
            engine = BacktestingEngine(
                initial_capital=1000000,
                transaction_cost=0.002,
                slippage=0.001,
                stop_loss=0.0,
                take_profit=0.0
            )
        else:
            # Standard settings for other strategies
            engine = BacktestingEngine(
                initial_capital=1000000,
                transaction_cost=0.002,
                slippage=0.001,
                stop_loss=0.05,
                take_profit=0.15
            )
        
        # Get strategy parameters
        params = strategy_configs.get(strategy_name, {})
        
        try:
            result = engine.run_backtest(
                trading_algorithm=STRATEGIES[strategy_name],
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                **params
            )
            
            results[strategy_name] = result
            
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
            
        except Exception as e:
            print(f"❌ Error testing {strategy_name}: {str(e)}")
            results[strategy_name] = None
    
    # Create comparison table
    print(f"\n" + "="*80)
    print("STRATEGY COMPARISON RESULTS")
    print("="*80)
    
    comparison_data = []
    for name, result in results.items():
        if result is not None:
            comparison_data.append({
                'Strategy': name.replace('_', ' ').title(),
                'Final Value': result['final_value'],
                'Total Return (%)': result['total_return'],
                'Max Drawdown (%)': result['max_drawdown'],
                'Total Trades': result['total_trades'],
                'Realized P&L': result.get('realized_pnl', 0),
                'Win Rate (%)': result.get('win_rate', 0)
            })
    
    if comparison_data:
        df_comparison = pd.DataFrame(comparison_data)
        
        # Sort by total return
        df_comparison = df_comparison.sort_values('Total Return (%)', ascending=False)
        
        print(df_comparison.to_string(index=False))
        
        # Find best and worst performers
        best_strategy = df_comparison.iloc[0]
        worst_strategy = df_comparison.iloc[-1]
        
        print(f"\n🏆 BEST PERFORMER:")
        print(f"Strategy: {best_strategy['Strategy']}")
        print(f"Return: {best_strategy['Total Return (%)']:.2f}%")
        print(f"Final Value: ¥{best_strategy['Final Value']:,.0f}")
        print(f"Win Rate: {best_strategy['Win Rate (%)']:.1f}%")
        
        print(f"\n📉 WORST PERFORMER:")
        print(f"Strategy: {worst_strategy['Strategy']}")
        print(f"Return: {worst_strategy['Total Return (%)']:.2f}%")
        print(f"Final Value: ¥{worst_strategy['Final Value']:,.0f}")
        print(f"Win Rate: {worst_strategy['Win Rate (%)']:.1f}%")
        
        # Calculate risk-adjusted metrics
        print(f"\n📊 RISK-ADJUSTED METRICS:")
        for _, row in df_comparison.iterrows():
            if row['Max Drawdown (%)'] != 0:
                sharpe_ratio = row['Total Return (%)'] / abs(row['Max Drawdown (%)'])
                print(f"{row['Strategy']}: Sharpe Ratio = {sharpe_ratio:.2f}")
        
        print(f"\n💡 KEY INSIGHTS:")
        print("1. **Price correction** significantly impacted all results")
        print("2. **Transaction costs** have major impact on returns")
        print("3. **Risk management** is crucial for consistent performance")
        print("4. **Market conditions** affect strategy effectiveness")
        print("5. **Position sizing** and **timing** are critical")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        print("1. **Focus on risk management** - limit drawdowns")
        print("2. **Consider transaction costs** - they add up quickly")
        print("3. **Diversify strategies** - don't rely on one approach")
        print("4. **Monitor market conditions** - adapt to changing environments")
        print("5. **Use realistic expectations** - single-digit returns are normal")
    
    return results

if __name__ == "__main__":
    compare_all_strategies() 