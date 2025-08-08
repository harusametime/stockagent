#!/usr/bin/env python3
"""
Test P&L tracking functionality
"""

from backtesting import BacktestingEngine
from trading_algorithms import TradingAlgorithms
import pandas as pd
from datetime import datetime

def test_pnl_tracking():
    """Test the P&L tracking functionality"""
    
    print("="*60)
    print("P&L TRACKING TEST")
    print("="*60)
    
    # Test parameters
    symbols = ['1579.T', '1360.T']
    start_date = '2023-01-01'
    end_date = '2025-08-05'
    
    # Initialize backtesting engine with P&L tracking
    engine = BacktestingEngine(
        initial_capital=1000000,
        transaction_cost=0.002,
        slippage=0.001,
        stop_loss=0.05,
        take_profit=0.15
    )
    
    # Test optimized pairs trading
    def optimized_pairs_strategy(data, current_prices):
        return TradingAlgorithms.pairs_trading_strategy(
            data, current_prices, 
            correlation_threshold=0.6, 
            z_score_threshold=2.5
        )
    
    print("📊 Running backtest with P&L tracking...")
    result = engine.run_backtest(
        trading_algorithm=optimized_pairs_strategy,
        symbols=symbols,
        start_date=start_date,
        end_date=end_date
    )
    
    # Display P&L results
    print(f"\n💰 P&L ANALYSIS:")
    print(f"Initial Capital: ¥{result['initial_capital']:,.0f}")
    print(f"Final Portfolio Value: ¥{result['final_value']:,.0f}")
    print(f"Total Return: {result['total_return']:.2f}%")
    print(f"Max Drawdown: {result['max_drawdown']:.2f}%")
    
    print(f"\n📈 REALIZED P&L:")
    print(f"Realized P&L: ¥{result['realized_pnl']:,.0f}")
    print(f"Total Trades P&L: ¥{result['total_trades_pnl']:,.0f}")
    print(f"Winning Trades: {result['winning_trades']}")
    print(f"Losing Trades: {result['losing_trades']}")
    print(f"Win Rate: {result['win_rate']:.1f}%")
    
    # Analyze individual trades
    if result['trade_history']:
        trades_df = pd.DataFrame(result['trade_history'])
        
        print(f"\n📋 TRADE ANALYSIS:")
        print(f"Total Trades: {len(trades_df)}")
        
        # Separate buy and sell trades
        buy_trades = trades_df[trades_df['action'] == 'BUY']
        sell_trades = trades_df[trades_df['action'] == 'SELL']
        
        print(f"Buy Trades: {len(buy_trades)}")
        print(f"Sell Trades: {len(sell_trades)}")
        
        if not sell_trades.empty:
            profitable_trades = sell_trades[sell_trades['pnl'] > 0]
            losing_trades = sell_trades[sell_trades['pnl'] < 0]
            
            print(f"\n💹 PROFITABLE TRADES:")
            print(f"Count: {len(profitable_trades)}")
            if len(profitable_trades) > 0:
                print(f"Average P&L: ¥{profitable_trades['pnl'].mean():,.0f}")
                print(f"Best Trade: ¥{profitable_trades['pnl'].max():,.0f}")
            
            print(f"\n📉 LOSING TRADES:")
            print(f"Count: {len(losing_trades)}")
            if len(losing_trades) > 0:
                print(f"Average P&L: ¥{losing_trades['pnl'].mean():,.0f}")
                print(f"Worst Trade: ¥{losing_trades['pnl'].min():,.0f}")
        
        # Show some sample trades
        print(f"\n📝 SAMPLE TRADES:")
        sample_trades = sell_trades.head(5) if len(sell_trades) > 0 else trades_df.head(5)
        for idx, trade in sample_trades.iterrows():
            print(f"{trade['date'].strftime('%Y-%m-%d')} | {trade['symbol']} | {trade['action']} | "
                  f"¥{trade['price']:,.0f} | P&L: ¥{trade.get('pnl', 0):,.0f}")
    
    # Portfolio value analysis with P&L
    if result['portfolio_values']:
        portfolio_df = pd.DataFrame(result['portfolio_values'])
        
        print(f"\n📊 PORTFOLIO ANALYSIS:")
        print(f"Starting Value: ¥{portfolio_df['portfolio_value'].iloc[0]:,.0f}")
        print(f"Ending Value: ¥{portfolio_df['portfolio_value'].iloc[-1]:,.0f}")
        
        if 'realized_pnl' in portfolio_df.columns:
            print(f"Final Realized P&L: ¥{portfolio_df['realized_pnl'].iloc[-1]:,.0f}")
            print(f"Final Unrealized P&L: ¥{portfolio_df['unrealized_pnl'].iloc[-1]:,.0f}")
            print(f"Final Total P&L: ¥{portfolio_df['total_pnl'].iloc[-1]:,.0f}")
        
        # Calculate P&L contribution to total return
        total_pnl_contribution = result['realized_pnl'] / result['initial_capital'] * 100
        print(f"P&L Contribution to Return: {total_pnl_contribution:.2f}%")
    
    return result

if __name__ == "__main__":
    test_pnl_tracking() 