#!/usr/bin/env python3
"""
Test the price fix for 1579.T
"""

from backtesting import BacktestingEngine
import pandas as pd

def test_price_fix():
    """Test the price fix for 1579.T"""
    
    print("="*60)
    print("PRICE FIX TEST")
    print("="*60)
    
    # Test parameters
    symbols = ['1579.T', '1360.T']
    start_date = '2024-07-01'
    end_date = '2024-07-31'
    
    # Initialize backtesting engine
    engine = BacktestingEngine(initial_capital=1000000)
    
    # Get historical data (should apply the fix)
    print("📊 Fetching historical data...")
    data = engine.get_historical_data(symbols, start_date, end_date)
    
    for symbol in symbols:
        if symbol in data:
            df = data[symbol]
            print(f"\n🔍 {symbol}:")
            print(f"Data points: {len(df)}")
            print(f"Price range: ¥{df['Close'].min():.2f} - ¥{df['Close'].max():.2f}")
            print(f"Average price: ¥{df['Close'].mean():.2f}")
            print(f"First day: ¥{df.iloc[0]['Close']:.2f}")
            print(f"Last day: ¥{df.iloc[-1]['Close']:.2f}")
            
            # Check if prices look reasonable
            if symbol == '1579.T':
                if df['Close'].mean() > 100:
                    print("✅ 1579.T prices look correct (around ¥300)")
                else:
                    print("❌ 1579.T prices still look wrong")
        else:
            print(f"❌ No data for {symbol}")
    
    # Test a small backtest to see if trading works correctly
    print(f"\n🧪 Testing backtest with fixed prices...")
    
    def simple_test_strategy(data, current_prices):
        signals = []
        for symbol in symbols:
            if symbol in current_prices:
                price = current_prices[symbol]
                print(f"  {symbol}: ¥{price:.2f}")
                if price > 0:
                    quantity = int(100000 / price)  # Buy ¥100k worth
                    signals.append({
                        'symbol': symbol,
                        'action': 'BUY',
                        'quantity': quantity,
                        'reason': 'Test trade'
                    })
        return signals
    
    try:
        result = engine.run_backtest(
            trading_algorithm=simple_test_strategy,
            symbols=symbols,
            start_date=start_date,
            end_date='2024-07-05'
        )
        
        print(f"\n📈 Backtest Results:")
        print(f"Final Value: ¥{result['final_value']:,.0f}")
        print(f"Total Return: {result['total_return']:.2f}%")
        print(f"Total Trades: {result['total_trades']}")
        
        if result['trade_history']:
            print(f"\n📋 Sample Trades:")
            for trade in result['trade_history'][:3]:
                print(f"  {trade['date'].strftime('%Y-%m-%d')} | {trade['symbol']} | {trade['action']} | ¥{trade['price']:.2f} | Qty: {trade['quantity']}")
        
    except Exception as e:
        print(f"❌ Error in backtest: {str(e)}")
    
    return data

if __name__ == "__main__":
    test_price_fix() 