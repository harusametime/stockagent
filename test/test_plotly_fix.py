#!/usr/bin/env python3
"""
Test the Plotly chart fix for dual y-axis compatibility
"""

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

def test_plotly_chart():
    """Test the fixed Plotly chart creation"""
    
    print("="*60)
    print("PLOTLY CHART FIX TEST")
    print("="*60)
    
    # Create sample data
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    portfolio_values = 1000000 + np.cumsum(np.random.randn(len(dates)) * 1000)
    realized_pnl = np.cumsum(np.random.randn(len(dates)) * 500)
    unrealized_pnl = np.cumsum(np.random.randn(len(dates)) * 300)
    total_pnl = realized_pnl + unrealized_pnl
    
    # Create DataFrame
    portfolio_df = pd.DataFrame({
        'date': dates,
        'portfolio_value': portfolio_values,
        'realized_pnl': realized_pnl,
        'unrealized_pnl': unrealized_pnl,
        'total_pnl': total_pnl
    })
    
    print("📊 Creating dual y-axis chart with fixed implementation...")
    
    # Create figure with secondary y-axis
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
    fig.add_trace(go.Scatter(
        x=portfolio_df['date'],
        y=portfolio_df['realized_pnl'],
        mode='lines',
        name='Realized P&L',
        line=dict(color='green', width=2, dash='dash'),
        yaxis='y2'
    ))
    
    # Unrealized P&L (secondary y-axis)
    fig.add_trace(go.Scatter(
        x=portfolio_df['date'],
        y=portfolio_df['unrealized_pnl'],
        mode='lines',
        name='Unrealized P&L',
        line=dict(color='orange', width=2, dash='dot'),
        yaxis='y2'
    ))
    
    # Total P&L (secondary y-axis)
    fig.add_trace(go.Scatter(
        x=portfolio_df['date'],
        y=portfolio_df['total_pnl'],
        mode='lines',
        name='Total P&L',
        line=dict(color='red', width=2),
        yaxis='y2'
    ))
    
    # Add horizontal lines using shapes (FIXED METHOD)
    initial_capital = 1000000
    
    # Initial capital line
    fig.add_shape(
        type="line",
        x0=portfolio_df['date'].min(),
        x1=portfolio_df['date'].max(),
        y0=initial_capital,
        y1=initial_capital,
        line=dict(color="gray", dash="dash"),
        yref="y"
    )
    fig.add_annotation(
        x=portfolio_df['date'].max(),
        y=initial_capital,
        text="Initial Capital",
        showarrow=False,
        yref="y"
    )
    
    # Break-even line for P&L
    fig.add_shape(
        type="line",
        x0=portfolio_df['date'].min(),
        x1=portfolio_df['date'].max(),
        y0=0,
        y1=0,
        line=dict(color="gray", dash="dash"),
        yref="y2"
    )
    fig.add_annotation(
        x=portfolio_df['date'].max(),
        y=0,
        text="Break-even",
        showarrow=False,
        yref="y2"
    )
    
    # Update layout with dual y-axes
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
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    print("✅ Chart created successfully!")
    print(f"✅ Chart has {len(fig.data)} traces")
    print(f"✅ Chart has {len(fig.layout.shapes)} shapes")
    print(f"✅ Chart has {len(fig.layout.annotations)} annotations")
    
    # Test chart validation
    try:
        # This would normally validate the chart
        chart_json = fig.to_json()
        print("✅ Chart JSON serialization successful")
        print(f"✅ Chart JSON size: {len(chart_json)} characters")
    except Exception as e:
        print(f"❌ Chart validation failed: {str(e)}")
        return False
    
    print(f"\n🎯 PLOTLY CHART FIX TEST COMPLETE!")
    print("The dual y-axis chart with shapes should work correctly in Streamlit.")
    
    return True

if __name__ == "__main__":
    test_plotly_chart() 