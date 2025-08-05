#!/usr/bin/env python3
"""
Debug price data issue - check actual prices vs trading prices
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from backtesting import BacktestingEngine
from trading_algorithms import TradingAlgorithms

def debug_price_data():
    """Debug the price data issue"""
    
    print("="*60)
    print("PRICE DATA DEBUG")
    print("="*60)
    
    # Test symbols
    symbols = ['1579.T', '1360.T']
    
    # Check specific date
    target_date = '2024-07-01'
    
    print(f"📊 Checking prices for {target_date}")
    print("-" * 40)
    
    for symbol in symbols:
        print(f"\n🔍 {symbol}:")
        
        # Get data from yfinance
        ticker = yf.Ticker(symbol)
        data = ticker.history(start='2024-07-01', end='2024-07-02')
        
        if not data.empty:
            # Just show the first available data
            first_data = data.iloc[0]
            date_str = data.index[0].strftime('%Y-%m-%d')
            
            print(f"Date: {date_str}")
            print(f"Open: ¥{first_data['Open']:.2f}")
            print(f"High: ¥{first_data['High']:.2f}")
            print(f"Low: ¥{first_data['Low']:.2f}")
            print(f"Close: ¥{first_data['Close']:.2f}")
            print(f"Volume: {first_data['Volume']:,.0f}")
        else:
            print("❌ No data found")
    
    # Check a range of dates
    print(f"\n📈 Checking price range for July 2024:")
    print("-" * 40)
    
    for symbol in symbols:
        print(f"\n🔍 {symbol} - July 2024:")
        
        ticker = yf.Ticker(symbol)
        data = ticker.history(start='2024-07-01', end='2024-07-31')
        
        if not data.empty:
            print(f"Data points: {len(data)}")
            print(f"Price range: ¥{data['Close'].min():.2f} - ¥{data['Close'].max():.2f}")
            print(f"Average price: ¥{data['Close'].mean():.2f}")
            print(f"First day (2024-07-01): ¥{data.iloc[0]['Close']:.2f}")
            print(f"Last day: ¥{data.iloc[-1]['Close']:.2f}")
        else:
            print("❌ No data found")
    
    # Test backtesting engine data fetching
    print(f"\n🧪 Testing BacktestingEngine data fetching:")
    print("-" * 40)
    
    engine = BacktestingEngine(initial_capital=1000000)
    
    # Get historical data
    data = engine.get_historical_data(symbols, '2024-07-01', '2024-07-31')
    
    for symbol in symbols:
        if symbol in data:
            df = data[symbol]
            print(f"\n🔍 {symbol} - BacktestingEngine data:")
            print(f"Data points: {len(df)}")
            print(f"Date range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
            print(f"Price range: ¥{df['Close'].min():.2f} - ¥{df['Close'].max():.2f}")
            print(f"First day (2024-07-01): ¥{df.iloc[0]['Close']:.2f}")
            print(f"Last day: ¥{df.iloc[-1]['Close']:.2f}")
            
            # Check for any obvious data issues
            if df['Close'].max() > 10000:  # Suspiciously high prices
                print("⚠️ WARNING: Suspiciously high prices detected!")
                high_prices = df[df['Close'] > 10000]
                print(f"High price dates: {len(high_prices)}")
                for date, row in high_prices.head().iterrows():
                    print(f"  {date.strftime('%Y-%m-%d')}: ¥{row['Close']:.2f}")
        else:
            print(f"❌ No data for {symbol}")
    
    # Test actual trading prices
    print(f"\n💰 Testing actual trading prices:")
    print("-" * 40)
    
    # Run a small backtest to see what prices are used
    def test_strategy(data, current_prices):
        signals = []
        for symbol in symbols:
            if symbol in current_prices:
                print(f"Current price for {symbol}: ¥{current_prices[symbol]:.2f}")
                signals.append({
                    'symbol': symbol,
                    'action': 'BUY',
                    'quantity': 100,
                    'reason': 'Test trade'
                })
        return signals
    
    try:
        result = engine.run_backtest(
            trading_algorithm=test_strategy,
            symbols=symbols,
            start_date='2024-07-01',
            end_date='2024-07-05'
        )
        
        if result['trade_history']:
            print(f"\n📋 Trade history:")
            for trade in result['trade_history'][:5]:  # Show first 5 trades
                print(f"  {trade['date'].strftime('%Y-%m-%d')} | {trade['symbol']} | {trade['action']} | ¥{trade['price']:.2f}")
        else:
            print("No trades executed")
            
    except Exception as e:
        print(f"❌ Error in backtest: {str(e)}")
    
    return data

if __name__ == "__main__":
    debug_price_data() 