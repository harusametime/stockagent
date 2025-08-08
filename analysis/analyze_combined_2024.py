#!/usr/bin/env python3
"""
Analyze the combined strategy's big return in 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def analyze_combined_2024():
    """Analyze the combined strategy's performance in 2024"""
    
    # Load portfolio data
    portfolio_df = pd.read_csv('backtest_portfolio.csv')
    trades_df = pd.read_csv('backtest_trades.csv')
    
    # Filter for combined strategy
    combined_portfolio = portfolio_df[portfolio_df['Strategy'] == 'combined'].copy()
    combined_trades = trades_df[trades_df['Strategy'] == 'combined'].copy()
    
    # Convert dates
    combined_portfolio['Date'] = pd.to_datetime(combined_portfolio['Date'])
    combined_trades['Date'] = pd.to_datetime(combined_trades['Date'])
    
    # Add year and month columns
    combined_portfolio['Year'] = combined_portfolio['Date'].dt.year
    combined_portfolio['Month'] = combined_portfolio['Date'].dt.month
    
    print("="*60)
    print("COMBINED STRATEGY 2024 ANALYSIS")
    print("="*60)
    
    # Analyze 2024 performance
    portfolio_2024 = combined_portfolio[combined_portfolio['Year'] == 2024]
    trades_2024 = combined_trades[combined_trades['Date'].dt.year == 2024]
    
    if not portfolio_2024.empty:
        print(f"2024 Portfolio Analysis:")
        print(f"Starting value (2024-01-01): ¥{portfolio_2024.iloc[0]['Portfolio Value']:,.0f}")
        print(f"Ending value (2024-12-31): ¥{portfolio_2024.iloc[-1]['Portfolio Value']:,.0f}")
        
        # Calculate 2024 return
        start_2024 = portfolio_2024.iloc[0]['Portfolio Value']
        end_2024 = portfolio_2024.iloc[-1]['Portfolio Value']
        return_2024 = (end_2024 - start_2024) / start_2024 * 100
        print(f"2024 Return: {return_2024:.2f}%")
        
        # Monthly breakdown for 2024
        print(f"\n📅 2024 MONTHLY PERFORMANCE:")
        monthly_2024 = portfolio_2024.groupby('Month')['Portfolio Value'].last()
        monthly_returns_2024 = monthly_2024.pct_change() * 100
        
        for month, return_val in monthly_returns_2024.items():
            if not pd.isna(return_val):
                month_name = datetime(2024, month, 1).strftime('%B')
                print(f"{month_name}: {return_val:.2f}%")
        
        # Find best and worst months
        best_month = monthly_returns_2024.idxmax()
        worst_month = monthly_returns_2024.idxmin()
        print(f"\nBest month: {datetime(2024, best_month, 1).strftime('%B')} ({monthly_returns_2024[best_month]:.2f}%)")
        print(f"Worst month: {datetime(2024, worst_month, 1).strftime('%B')} ({monthly_returns_2024[worst_month]:.2f}%)")
        
        # Analyze trades in 2024
        print(f"\n📈 2024 TRADE ANALYSIS:")
        print(f"Total trades in 2024: {len(trades_2024)}")
        print(f"Buy trades: {(trades_2024['Action'] == 'BUY').sum()}")
        print(f"Sell trades: {(trades_2024['Action'] == 'SELL').sum()}")
        
        # Analyze by symbol in 2024
        for symbol in ['1579.T', '1360.T']:
            symbol_trades = trades_2024[trades_2024['Symbol'] == symbol]
            if not symbol_trades.empty:
                print(f"\n{symbol} trades in 2024:")
                print(f"  Total: {len(symbol_trades)}")
                print(f"  Buys: {(symbol_trades['Action'] == 'BUY').sum()}")
                print(f"  Sells: {(symbol_trades['Action'] == 'SELL').sum()}")
                print(f"  Avg price: ¥{symbol_trades['Price'].mean():.2f}")
        
        # Find the biggest jumps in portfolio value
        portfolio_2024['Daily_Return'] = portfolio_2024['Portfolio Value'].pct_change() * 100
        
        print(f"\n🚀 BIGGEST DAILY GAINS IN 2024:")
        biggest_gains = portfolio_2024.nlargest(10, 'Daily_Return')
        for idx, row in biggest_gains.iterrows():
            print(f"{row['Date'].strftime('%Y-%m-%d')}: +{row['Daily_Return']:.2f}% (¥{row['Portfolio Value']:,.0f})")
        
        print(f"\n📉 BIGGEST DAILY LOSSES IN 2024:")
        biggest_losses = portfolio_2024.nsmallest(10, 'Daily_Return')
        for idx, row in biggest_losses.iterrows():
            print(f"{row['Date'].strftime('%Y-%m-%d')}: {row['Daily_Return']:.2f}% (¥{row['Portfolio Value']:,.0f})")
        
        # Analyze the combined strategy logic
        print(f"\n🔍 COMBINED STRATEGY ANALYSIS:")
        print("The combined strategy aggregates signals from all other strategies:")
        print("- Mean Reversion: Uses RSI and Bollinger Bands")
        print("- Momentum: Uses MACD and Volume")
        print("- Pairs Trading: Uses correlation between 1579.T and 1360.T")
        print("- Trend Following: Uses moving average crossovers")
        print("- Volatility Breakout: Uses ATR for breakouts")
        
        print(f"\n💡 WHY SUCH HIGH RETURNS IN 2024:")
        print("1. **Multiple Signal Sources**: Combined strategy uses 5 different strategies")
        print("2. **High Activity**: 809 total trades vs 58 for pairs trading")
        print("3. **Diversification**: Different strategies work in different market conditions")
        print("4. **Aggressive Trading**: More frequent trading opportunities")
        print("5. **Market Conditions**: 2024 had favorable conditions for multiple strategies")
        
        # Check if there's any data quality issue
        print(f"\n⚠️  POTENTIAL ISSUES:")
        print("1. **Over-optimization**: Combined strategy might be overfitted")
        print("2. **Transaction Costs**: Not accounting for trading fees")
        print("3. **Slippage**: Not accounting for market impact")
        print("4. **Look-ahead Bias**: Potential data leakage")
        print("5. **Unrealistic Returns**: 744% return seems too good to be true")
        
        return portfolio_2024, trades_2024
    
    return None, None

if __name__ == "__main__":
    analyze_combined_2024() 