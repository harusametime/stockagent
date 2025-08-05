#!/usr/bin/env python3
"""
Test P&L visualization functionality
"""

from backtesting import BacktestingEngine
from trading_algorithms import TradingAlgorithms
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

def test_pnl_visualization():
    """Test P&L visualization with sample data"""
    
    print("="*60)
    print("P&L VISUALIZATION TEST")
    print("="*60)
    
    # Test parameters
    symbols = ['1579.T', '1360.T']
    start_date = '2023-01-01'
    end_date = '2025-08-05'
    
    # Initialize backtesting engine
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
    
    print("📊 Running backtest with P&L visualization...")
    result = engine.run_backtest(
        trading_algorithm=optimized_pairs_strategy,
        symbols=symbols,
        start_date=start_date,
        end_date=end_date
    )
    
    # Test portfolio data structure
    portfolio_df = pd.DataFrame(result['portfolio_values'])
    print(f"\n📈 PORTFOLIO DATA STRUCTURE:")
    print(f"Columns: {list(portfolio_df.columns)}")
    print(f"Rows: {len(portfolio_df)}")
    
    # Check P&L columns exist
    pnl_columns = ['realized_pnl', 'unrealized_pnl', 'total_pnl']
    for col in pnl_columns:
        if col in portfolio_df.columns:
            print(f"✅ {col}: Available")
            print(f"   Range: {portfolio_df[col].min():.0f} to {portfolio_df[col].max():.0f}")
        else:
            print(f"❌ {col}: Missing")
    
    # Test trade data structure
    if result['trade_history']:
        trades_df = pd.DataFrame(result['trade_history'])
        print(f"\n📋 TRADE DATA STRUCTURE:")
        print(f"Columns: {list(trades_df.columns)}")
        print(f"Total trades: {len(trades_df)}")
        
        # Check P&L columns in trades
        if 'pnl' in trades_df.columns:
            sell_trades = trades_df[trades_df['action'] == 'SELL']
            if len(sell_trades) > 0:
                print(f"✅ P&L data available for {len(sell_trades)} sell trades")
                print(f"   P&L range: {sell_trades['pnl'].min():.0f} to {sell_trades['pnl'].max():.0f}")
                print(f"   Profitable trades: {(sell_trades['pnl'] > 0).sum()}")
                print(f"   Losing trades: {(sell_trades['pnl'] < 0).sum()}")
            else:
                print("⚠️ No sell trades to analyze P&L")
        else:
            print("❌ P&L column missing from trade history")
    
    # Test chart creation
    print(f"\n📊 TESTING CHART CREATION:")
    
    # Portfolio and P&L chart
    fig = go.Figure()
    
    # Portfolio Value (primary y-axis)
    fig.add_trace(go.Scatter(
        x=portfolio_df['date'],
        y=portfolio_df['portfolio_value'],
        mode='lines',
        name='Portfolio Value',
        line=dict(color='blue', width=2),
        yaxis='y'
    ))
    
    # Realized P&L (secondary y-axis)
    if 'realized_pnl' in portfolio_df.columns:
        fig.add_trace(go.Scatter(
            x=portfolio_df['date'],
            y=portfolio_df['realized_pnl'],
            mode='lines',
            name='Realized P&L',
            line=dict(color='green', width=2, dash='dash'),
            yaxis='y2'
        ))
        print("✅ Realized P&L chart trace added")
    
    # Unrealized P&L (secondary y-axis)
    if 'unrealized_pnl' in portfolio_df.columns:
        fig.add_trace(go.Scatter(
            x=portfolio_df['date'],
            y=portfolio_df['unrealized_pnl'],
            mode='lines',
            name='Unrealized P&L',
            line=dict(color='orange', width=2, dash='dot'),
            yaxis='y2'
        ))
        print("✅ Unrealized P&L chart trace added")
    
    # Total P&L (secondary y-axis)
    if 'total_pnl' in portfolio_df.columns:
        fig.add_trace(go.Scatter(
            x=portfolio_df['date'],
            y=portfolio_df['total_pnl'],
            mode='lines',
            name='Total P&L',
            line=dict(color='red', width=2),
            yaxis='y2'
        ))
        print("✅ Total P&L chart trace added")
    
    # Update layout
    fig.update_layout(
        title="Portfolio Value and P&L Over Time",
        xaxis_title="Date",
        yaxis=dict(
            title="Portfolio Value (¥)",
            side="left",
            showgrid=True
        ),
        yaxis2=dict(
            title="P&L (¥)",
            side="right",
            overlaying="y",
            showgrid=False
        ),
        height=500
    )
    
    print("✅ Chart layout configured successfully")
    print(f"✅ Chart has {len(fig.data)} traces")
    
    # Test P&L distribution chart
    if result['trade_history']:
        trades_df = pd.DataFrame(result['trade_history'])
        sell_trades = trades_df[trades_df['action'] == 'SELL']
        
        if len(sell_trades) > 0 and 'pnl' in sell_trades.columns:
            fig_pnl = go.Figure()
            fig_pnl.add_trace(go.Histogram(
                x=sell_trades['pnl'],
                nbinsx=20,
                name='Trade P&L',
                marker_color='lightblue'
            ))
            fig_pnl.add_vline(x=0, line_dash="dash", line_color="red", 
                             annotation_text="Break-even")
            fig_pnl.update_layout(
                title="Distribution of Trade P&L",
                xaxis_title="P&L (¥)",
                yaxis_title="Number of Trades",
                height=300
            )
            print("✅ P&L distribution chart created successfully")
        else:
            print("⚠️ Cannot create P&L distribution chart - no sell trades with P&L data")
    
    print(f"\n🎯 VISUALIZATION TEST COMPLETE!")
    print("The P&L visualization should work correctly in the Streamlit app.")
    
    return result

if __name__ == "__main__":
    test_pnl_visualization() 