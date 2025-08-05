#!/usr/bin/env python3
"""
Test script for backtesting engine with trading algorithms
"""

from backtesting import BacktestingEngine
from trading_algorithms import STRATEGIES
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

def main():
    # Initialize backtesting engine
    engine = BacktestingEngine(initial_capital=1000000)  # ¥1M initial capital
    
    # Define symbols and date range
    symbols = ['1579.T', '1360.T']
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')  # 1 year of data
    
    print(f"Testing backtesting engine with symbols: {symbols}")
    print(f"Date range: {start_date} to {end_date}")
    print(f"Initial capital: ¥{engine.initial_capital:,.0f}")
    print("\n" + "="*50)
    
    # Test each strategy
    results = {}
    
    for strategy_name, strategy_func in STRATEGIES.items():
        print(f"\nTesting strategy: {strategy_name}")
        print("-" * 30)
        
        try:
            # Run backtest
            result = engine.run_backtest(
                trading_algorithm=strategy_func,
                symbols=symbols,
                start_date=start_date,
                end_date=end_date
            )
            
            # Store results
            results[strategy_name] = result
            
            # Print summary
            print(f"Final Value: ¥{result['final_value']:,.0f}")
            print(f"Total Return: {result['total_return']:.2f}%")
            print(f"Max Drawdown: {result['max_drawdown']:.2f}%")
            print(f"Total Trades: {result['total_trades']}")
            
        except Exception as e:
            print(f"Error testing {strategy_name}: {str(e)}")
            continue
    
    # Compare all strategies
    print("\n" + "="*50)
    print("STRATEGY COMPARISON")
    print("="*50)
    
    comparison_data = []
    for strategy_name, result in results.items():
        comparison_data.append({
            'Strategy': strategy_name,
            'Final Value': result['final_value'],
            'Total Return (%)': result['total_return'],
            'Max Drawdown (%)': result['max_drawdown'],
            'Total Trades': result['total_trades']
        })
    
    df_comparison = pd.DataFrame(comparison_data)
    print(df_comparison.to_string(index=False))
    
    # Plot results for the best performing strategy
    if results:
        best_strategy = max(results.keys(), key=lambda x: results[x]['total_return'])
        print(f"\nBest performing strategy: {best_strategy}")
        print(f"Return: {results[best_strategy]['total_return']:.2f}%")
        
        # Plot the best strategy
        engine.plot_results(results[best_strategy])
    
    # Save detailed results to CSV
    if results:
        detailed_results = []
        for strategy_name, result in results.items():
            for trade in result['trade_history']:
                detailed_results.append({
                    'Strategy': strategy_name,
                    'Date': trade['date'],
                    'Symbol': trade['symbol'],
                    'Action': trade['action'],
                    'Quantity': trade['quantity'],
                    'Price': trade['price'],
                    'Reason': trade.get('reason', 'N/A')
                })
        
        df_trades = pd.DataFrame(detailed_results)
        df_trades.to_csv('backtest_trades.csv', index=False)
        print(f"\nDetailed trade history saved to 'backtest_trades.csv'")
        
        # Save portfolio values
        portfolio_data = []
        for strategy_name, result in results.items():
            for pv in result['portfolio_values']:
                portfolio_data.append({
                    'Strategy': strategy_name,
                    'Date': pv['date'],
                    'Portfolio Value': pv['portfolio_value'],
                    'Cash': pv['cash']
                })
        
        df_portfolio = pd.DataFrame(portfolio_data)
        df_portfolio.to_csv('backtest_portfolio.csv', index=False)
        print(f"Portfolio values saved to 'backtest_portfolio.csv'")

if __name__ == "__main__":
    main() 