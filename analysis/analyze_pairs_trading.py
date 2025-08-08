#!/usr/bin/env python3
"""
Detailed analysis of pairs_trading strategy performance
"""

from backtesting import BacktestingEngine
from trading_algorithms import TradingAlgorithms
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def analyze_pairs_trading():
    """Run detailed analysis of pairs_trading strategy"""
    
    # Initialize backtesting engine
    engine = BacktestingEngine(initial_capital=1000000)  # ¥1M initial capital
    
    # Define symbols and date range
    symbols = ['1579.T', '1360.T']
    start_date = '2023-01-01'
    end_date = '2025-08-05'
    
    print("="*60)
    print("PAIRS TRADING STRATEGY ANALYSIS")
    print("="*60)
    print(f"Date Range: {start_date} to {end_date}")
    print(f"Symbols: {symbols}")
    print(f"Initial Capital: ¥{engine.initial_capital:,.0f}")
    print("="*60)
    
    # Run backtest
    result = engine.run_backtest(
        trading_algorithm=TradingAlgorithms.pairs_trading_strategy,
        symbols=symbols,
        start_date=start_date,
        end_date=end_date
    )
    
    # Print basic results
    print(f"\n📊 BASIC RESULTS:")
    print(f"Final Value: ¥{result['final_value']:,.0f}")
    print(f"Total Return: {result['total_return']:.2f}%")
    print(f"Max Drawdown: {result['max_drawdown']:.2f}%")
    print(f"Total Trades: {result['total_trades']}")
    
    # Analyze trade history
    trades_df = pd.DataFrame(result['trade_history'])
    
    if not trades_df.empty:
        print(f"\n📈 TRADE ANALYSIS:")
        print(f"Total trades: {len(trades_df)}")
        print(f"Buy trades: {(trades_df['action'] == 'BUY').sum()}")
        print(f"Sell trades: {(trades_df['action'] == 'SELL').sum()}")
        print(f"Average trade price: ¥{trades_df['price'].mean():.2f}")
        print(f"Average trade quantity: {trades_df['quantity'].mean():.0f}")
        
        # Analyze by symbol
        for symbol in ['1579.T', '1360.T']:
            symbol_trades = trades_df[trades_df['symbol'] == symbol]
            if not symbol_trades.empty:
                print(f"\n{symbol} trades:")
                print(f"  Total: {len(symbol_trades)}")
                print(f"  Buys: {(symbol_trades['action'] == 'BUY').sum()}")
                print(f"  Sells: {(symbol_trades['action'] == 'SELL').sum()}")
                print(f"  Avg price: ¥{symbol_trades['price'].mean():.2f}")
        
        # Monthly performance based on portfolio values
        portfolio_df = pd.DataFrame(result['portfolio_values'])
        portfolio_df['date'] = pd.to_datetime(portfolio_df['date'])
        portfolio_df['month'] = portfolio_df['date'].dt.to_period('M')
        
        # Calculate monthly returns
        monthly_portfolio = portfolio_df.groupby('month')['portfolio_value'].last()
        monthly_returns = monthly_portfolio.pct_change() * 100
        
        print(f"\n📅 MONTHLY PERFORMANCE:")
        print(f"Best month: {monthly_returns.idxmax()} ({monthly_returns.max():.2f}%)")
        print(f"Worst month: {monthly_returns.idxmin()} ({monthly_returns.min():.2f}%)")
        print(f"Average monthly return: {monthly_returns.mean():.2f}%")
        print(f"Positive months: {(monthly_returns > 0).sum()}/{len(monthly_returns)}")
        
        # Correlation analysis
        print(f"\n🔗 CORRELATION ANALYSIS:")
        # Get the actual data used in backtest
        data = engine.get_historical_data(symbols, start_date, end_date)
        if len(data) == 2:
            df1 = data['1579.T']
            df2 = data['1360.T']
            
            # Calculate rolling correlation
            correlation = df1['Close'].rolling(window=30).corr(df2['Close'])
            print(f"Average correlation: {correlation.mean():.3f}")
            print(f"Correlation range: {correlation.min():.3f} to {correlation.max():.3f}")
            print(f"Days with high correlation (>0.8): {(correlation > 0.8).sum()}")
            print(f"Days with low correlation (<-0.8): {(correlation < -0.8).sum()}")
    
    # Portfolio value analysis
    portfolio_df = pd.DataFrame(result['portfolio_values'])
    portfolio_df['date'] = pd.to_datetime(portfolio_df['date'])
    
    print(f"\n💰 PORTFOLIO ANALYSIS:")
    print(f"Starting value: ¥{portfolio_df['portfolio_value'].iloc[0]:,.0f}")
    print(f"Ending value: ¥{portfolio_df['portfolio_value'].iloc[-1]:,.0f}")
    print(f"Peak value: ¥{portfolio_df['portfolio_value'].max():,.0f}")
    print(f"Lowest value: ¥{portfolio_df['portfolio_value'].min():,.0f}")
    
    # Calculate drawdown periods
    portfolio_df['peak'] = portfolio_df['portfolio_value'].expanding().max()
    portfolio_df['drawdown'] = (portfolio_df['portfolio_value'] - portfolio_df['peak']) / portfolio_df['peak'] * 100
    
    print(f"Number of drawdown periods: {(portfolio_df['drawdown'] < -5).sum()}")
    print(f"Average drawdown duration: {portfolio_df[portfolio_df['drawdown'] < -5].shape[0]} days")
    
    # Suggestions for improvement
    print(f"\n💡 SUGGESTIONS FOR IMPROVEMENT:")
    print("1. **Correlation Threshold**: Current default is 0.7, try 0.6-0.8 range")
    print("2. **Z-Score Threshold**: Current default is 2.0, try 1.5-2.5 range")
    print("3. **Position Sizing**: Implement dynamic position sizing based on volatility")
    print("4. **Stop Loss**: Add stop-loss mechanisms to limit downside")
    print("5. **Take Profit**: Implement take-profit levels")
    print("6. **Risk Management**: Add maximum position limits")
    print("7. **Market Regime Detection**: Avoid trading during high volatility periods")
    print("8. **Transaction Costs**: Consider impact of trading fees and slippage")
    
    # Test different parameters
    print(f"\n🔬 PARAMETER OPTIMIZATION TEST:")
    test_correlations = [0.6, 0.7, 0.8]
    test_z_scores = [1.5, 2.0, 2.5]
    
    best_return = result['total_return']
    best_params = {'correlation_threshold': 0.7, 'z_score_threshold': 2.0}
    
    for corr in test_correlations:
        for z_score in test_z_scores:
            try:
                # Create custom strategy with different parameters
                def custom_pairs_strategy(data, current_prices):
                    return TradingAlgorithms.pairs_trading_strategy(data, current_prices, 
                                               correlation_threshold=corr, 
                                               z_score_threshold=z_score)
                
                test_result = engine.run_backtest(
                    trading_algorithm=custom_pairs_strategy,
                    symbols=symbols,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if test_result['total_return'] > best_return:
                    best_return = test_result['total_return']
                    best_params = {'correlation_threshold': corr, 'z_score_threshold': z_score}
                
                print(f"Corr={corr}, Z={z_score}: {test_result['total_return']:.2f}%")
                
            except Exception as e:
                print(f"Error with Corr={corr}, Z={z_score}: {str(e)}")
    
    print(f"\n🏆 BEST PARAMETERS FOUND:")
    print(f"Correlation Threshold: {best_params['correlation_threshold']}")
    print(f"Z-Score Threshold: {best_params['z_score_threshold']}")
    print(f"Best Return: {best_return:.2f}%")
    
    return result

if __name__ == "__main__":
    analyze_pairs_trading() 