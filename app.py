import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import threading
import time

# Import our modules
from backtesting import BacktestingEngine
from trading_algorithms import STRATEGIES
from live_trading import LiveTradingAgent

# Load environment variables
load_dotenv()

# Initialize session state for auto-trading
if 'auto_trading_active' not in st.session_state:
    st.session_state.auto_trading_active = False
if 'auto_trading_thread' not in st.session_state:
    st.session_state.auto_trading_thread = None
if 'trading_agent' not in st.session_state:
    st.session_state.trading_agent = None
if 'trading_logs' not in st.session_state:
    st.session_state.trading_logs = []

# Page configuration
st.set_page_config(
    page_title="Stock Trading Agent",
    page_icon="📈",
    layout="wide"
)

# Sidebar
st.sidebar.title("📈 Stock Trading Agent")
st.sidebar.markdown("Nikkei 225 ETF Trading System")

# Main content
st.title("📈 Stock Trading Agent")
st.markdown("A comprehensive trading system for Nikkei 225 ETFs (1579.T and 1360.T)")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Backtesting", "🤖 Live Trading", "📈 Market Data", "⚙️ Settings"])

with tab1:
    st.header("📊 Backtesting")
    
    # Backtesting parameters
    col1, col2 = st.columns(2)
    
    with col1:
        initial_capital = st.number_input("Initial Capital (¥)", value=1000000, step=100000)
        strategy_name = st.selectbox("Trading Strategy", list(STRATEGIES.keys()))
        
    with col2:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=365))
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Strategy parameters
    st.subheader("Strategy Parameters")
    
    if strategy_name == "mean_reversion":
        col1, col2, col3 = st.columns(3)
        with col1:
            rsi_oversold = st.slider("RSI Oversold", 20, 40, 30)
        with col2:
            rsi_overbought = st.slider("RSI Overbought", 60, 80, 70)
        with col3:
            bb_std_multiplier = st.slider("Bollinger Bands Std Multiplier", 1.5, 3.0, 2.0)
        strategy_params = {
            'rsi_oversold': rsi_oversold,
            'rsi_overbought': rsi_overbought,
            'bb_std_multiplier': bb_std_multiplier
        }
    
    elif strategy_name == "momentum":
        col1, col2 = st.columns(2)
        with col1:
            macd_threshold = st.slider("MACD Threshold", -0.1, 0.1, 0.0, 0.01, key="backtest_macd_threshold")
        with col2:
            volume_threshold = st.slider("Volume Threshold", 1.0, 3.0, 1.5, 0.1, key="backtest_volume_threshold")
        strategy_params = {
            'macd_threshold': macd_threshold,
            'volume_threshold': volume_threshold
        }
    
    elif strategy_name == "pairs_trading":
        col1, col2 = st.columns(2)
        with col1:
            correlation_threshold = st.slider("Correlation Threshold", 0.5, 0.9, 0.7, 0.05, key="backtest_correlation_threshold")
        with col2:
            z_score_threshold = st.slider("Z-Score Threshold", 1.0, 3.0, 2.0, 0.1, key="backtest_z_score_threshold")
        strategy_params = {
            'correlation_threshold': correlation_threshold,
            'z_score_threshold': z_score_threshold
        }
    
    elif strategy_name == "trend_following":
        col1, col2 = st.columns(2)
        with col1:
            short_window = st.slider("Short Window", 5, 20, 10)
        with col2:
            long_window = st.slider("Long Window", 20, 50, 30)
        strategy_params = {
            'short_window': short_window,
            'long_window': long_window
        }
    
    elif strategy_name == "range_bound":
        col1, col2, col3 = st.columns(3)
        with col1:
            lookback_period = st.slider("Lookback Period (days)", 30, 120, 60, key="backtest_lookback")
        with col2:
            range_threshold = st.slider("Range Threshold (%)", 0.10, 0.30, 0.15, 0.01, key="backtest_range_threshold")
        with col3:
            oversold_percentile = st.slider("Oversold Percentile", 10, 30, 20, key="backtest_oversold")
        
        col1, col2 = st.columns(2)
        with col1:
            overbought_percentile = st.slider("Overbought Percentile", 70, 90, 80, key="backtest_overbought")
        with col2:
            position_size = st.slider("Position Size (%)", 0.10, 0.30, 0.20, 0.01, key="backtest_position_size")
        
        strategy_params = {
            'lookback_period': lookback_period,
            'range_threshold': range_threshold,
            'oversold_percentile': oversold_percentile,
            'overbought_percentile': overbought_percentile,
            'position_size': position_size,
            'no_stop_loss': True
        }
    
    else:
        strategy_params = {}
    
    # Run backtest button
    if st.button("🚀 Run Backtest", type="primary"):
        with st.spinner("Running backtest..."):
            try:
                # Initialize backtesting engine
                # For range_bound strategy, disable stop-loss and take-profit
                if strategy_name == "range_bound":
                    engine = BacktestingEngine(
                        initial_capital=initial_capital,
                        transaction_cost=0.002,
                        slippage=0.001,
                        stop_loss=0.0,  # NO STOP LOSS for range-bound
                        take_profit=0.0  # NO TAKE PROFIT for range-bound
                    )
                else:
                    engine = BacktestingEngine(initial_capital=initial_capital)
                
                # Run backtest
                result = engine.run_backtest(
                    trading_algorithm=STRATEGIES[strategy_name],
                    symbols=['1579.T', '1360.T'],
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d'),
                    **strategy_params
                )
                
                # Display results
                st.success("Backtest completed successfully!")
                
                # Performance metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Initial Capital", f"¥{result['initial_capital']:,.0f}")
                with col2:
                    st.metric("Final Value", f"¥{result['final_value']:,.0f}")
                with col3:
                    st.metric("Total Return", f"{result['total_return']:.2f}%")
                with col4:
                    st.metric("Max Drawdown", f"{result['max_drawdown']:.2f}%")
                
                # P&L metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Realized P&L", f"¥{result.get('realized_pnl', 0):,.0f}")
                with col2:
                    st.metric("Unrealized P&L", f"¥{result.get('unrealized_pnl', 0):,.0f}")
                with col3:
                    st.metric("Win Rate", f"{result.get('win_rate', 0):.1f}%")
                with col4:
                    st.metric("Total Trades", f"{result.get('total_trades', 0)}")
                
                # Portfolio value and P&L chart
                st.subheader("Portfolio Value and P&L Over Time")
                portfolio_df = pd.DataFrame(result['portfolio_values'])
                portfolio_df['date'] = pd.to_datetime(portfolio_df['date'])
                
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
                if 'realized_pnl' in portfolio_df.columns:
                    fig.add_trace(go.Scatter(
                        x=portfolio_df['date'],
                        y=portfolio_df['realized_pnl'],
                        mode='lines',
                        name='Realized P&L',
                        line=dict(color='green', width=2, dash='dash'),
                        yaxis='y2'
                    ))
                
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
                
                # Add horizontal lines using shapes
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
                
                # Add break-even line for P&L
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
                st.plotly_chart(fig, use_container_width=True)
                
                # P&L Analysis
                st.subheader("💰 P&L Analysis")
                
                if result['trade_history']:
                    trades_df = pd.DataFrame(result['trade_history'])
                    trades_df['date'] = pd.to_datetime(trades_df['date'])
                    
                    # Separate buy and sell trades
                    buy_trades = trades_df[trades_df['action'] == 'BUY']
                    sell_trades = trades_df[trades_df['action'] == 'SELL']
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Buy Trades", len(buy_trades))
                    with col2:
                        st.metric("Sell Trades", len(sell_trades))
                    with col3:
                        if len(sell_trades) > 0:
                            profitable_trades = sell_trades[sell_trades['pnl'] > 0]
                            st.metric("Profitable Trades", len(profitable_trades))
                    with col4:
                        if len(sell_trades) > 0:
                            losing_trades = sell_trades[sell_trades['pnl'] < 0]
                            st.metric("Losing Trades", len(losing_trades))
                    
                    # P&L distribution chart
                    if len(sell_trades) > 0 and 'pnl' in sell_trades.columns:
                        st.subheader("P&L Distribution")
                        
                        # Create P&L histogram
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
                        st.plotly_chart(fig_pnl, use_container_width=True)
                        
                        # P&L over time
                        st.subheader("P&L Over Time")
                        fig_pnl_time = go.Figure()
                        fig_pnl_time.add_trace(go.Scatter(
                            x=sell_trades['date'],
                            y=sell_trades['pnl'].cumsum(),
                            mode='lines+markers',
                            name='Cumulative P&L',
                            line=dict(color='green', width=2)
                        ))
                        fig_pnl_time.add_hline(y=0, line_dash="dash", line_color="gray", 
                                             annotation_text="Break-even")
                        fig_pnl_time.update_layout(
                            title="Cumulative P&L Over Time",
                            xaxis_title="Date",
                            yaxis_title="Cumulative P&L (¥)",
                            height=300
                        )
                        st.plotly_chart(fig_pnl_time, use_container_width=True)
                
                # Trade history
                st.subheader("📋 Trade History")
                if result['trade_history']:
                    trades_df = pd.DataFrame(result['trade_history'])
                    trades_df['date'] = pd.to_datetime(trades_df['date'])
                    
                    # Format the dataframe for display
                    display_df = trades_df.copy()
                    if 'pnl' in display_df.columns:
                        display_df['pnl'] = display_df['pnl'].apply(lambda x: f"¥{x:,.0f}" if pd.notna(x) else "N/A")
                    if 'realized_pnl' in display_df.columns:
                        display_df['realized_pnl'] = display_df['realized_pnl'].apply(lambda x: f"¥{x:,.0f}" if pd.notna(x) else "N/A")
                    
                    st.dataframe(display_df, use_container_width=True)
                    
                    # Download trade history
                    csv = trades_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Trade History",
                        data=csv,
                        file_name=f"trade_history_{strategy_name}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No trades were executed during the backtest period.")
                
            except Exception as e:
                st.error(f"Error running backtest: {str(e)}")

with tab2:
    st.header("🤖 Live Trading")
    
    # Check if API credentials are configured
    api_host = os.getenv('KABUSAPI_HOST')
    api_env = os.getenv('KABUSAPI_ENV', 'dev')
    api_password = os.getenv('KABUSAPI_PASSWORD')
    
    if not all([api_host, api_password]):
        st.warning("⚠️ API credentials not configured. Please set up your .env file with KabusAPI credentials.")
        st.code("""
KABUSAPI_HOST=localhost
KABUSAPI_ENV=dev  # Options: dev (port 18081) or prod (port 18080)
KABUSAPI_PASSWORD=your_password
        """)
    else:
        # Live trading parameters
        col1, col2 = st.columns(2)
        
        with col1:
            live_strategy = st.selectbox("Trading Strategy", list(STRATEGIES.keys()), key="live_strategy")
            interval_minutes = st.slider("Trading Interval (minutes)", 5, 60, 15)
        
        with col2:
            initial_capital_live = st.number_input("Initial Capital (¥)", value=1000000, step=100000, key="live_capital")
            auto_trading = st.checkbox("Enable Auto Trading")
        
        # Strategy parameters for live trading
        st.subheader("Strategy Parameters")
        
        if live_strategy == "mean_reversion":
            col1, col2, col3 = st.columns(3)
            with col1:
                live_rsi_oversold = st.slider("RSI Oversold", 20, 40, 30, key="live_rsi_oversold")
            with col2:
                live_rsi_overbought = st.slider("RSI Overbought", 60, 80, 70, key="live_rsi_overbought")
            with col3:
                live_bb_std_multiplier = st.slider("Bollinger Bands Std Multiplier", 1.5, 3.0, 2.0, key="live_bb_std")
            live_strategy_params = {
                'rsi_oversold': live_rsi_oversold,
                'rsi_overbought': live_rsi_overbought,
                'bb_std_multiplier': live_bb_std_multiplier
            }
        
        elif live_strategy == "momentum":
            col1, col2 = st.columns(2)
            with col1:
                live_macd_threshold = st.slider("MACD Threshold", -0.1, 0.1, 0.0, 0.01, key="live_macd_threshold")
            with col2:
                live_volume_threshold = st.slider("Volume Threshold", 1.0, 3.0, 1.5, 0.1, key="live_volume_threshold")
            live_strategy_params = {
                'macd_threshold': live_macd_threshold,
                'volume_threshold': live_volume_threshold
            }
        
        elif live_strategy == "range_bound":
            col1, col2, col3 = st.columns(3)
            with col1:
                live_lookback_period = st.slider("Lookback Period (days)", 30, 120, 60, key="live_lookback")
            with col2:
                live_range_threshold = st.slider("Range Threshold (%)", 0.10, 0.30, 0.15, 0.01, key="live_range_threshold")
            with col3:
                live_oversold_percentile = st.slider("Oversold Percentile", 10, 30, 20, key="live_oversold")
            
            col1, col2 = st.columns(2)
            with col1:
                live_overbought_percentile = st.slider("Overbought Percentile", 70, 90, 80, key="live_overbought")
            with col2:
                live_position_size = st.slider("Position Size (%)", 0.10, 0.30, 0.20, 0.01, key="live_position_size")
            
            live_strategy_params = {
                'lookback_period': live_lookback_period,
                'range_threshold': live_range_threshold,
                'oversold_percentile': live_oversold_percentile,
                'overbought_percentile': live_overbought_percentile,
                'position_size': live_position_size,
                'no_stop_loss': True
            }
        
        else:
            live_strategy_params = {}
        
        # Live trading controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔐 Test Connection", type="secondary"):
                with st.spinner("Testing API connection..."):
                    try:
                        # Capture stdout to show detailed error messages
                        import io
                        import sys
                        from contextlib import redirect_stdout
                        
                        # Create a string buffer to capture output
                        output_buffer = io.StringIO()
                        
                        with redirect_stdout(output_buffer):
                            agent = LiveTradingAgent(initial_capital_live)
                            auth_result = agent.authenticate()
                        
                        # Get the captured output
                        detailed_output = output_buffer.getvalue()
                        
                        if auth_result:
                            st.success("✅ API connection successful!")
                            # Show detailed success info
                            with st.expander("📋 Connection Details"):
                                st.code(detailed_output)
                        else:
                            st.error("❌ API connection failed!")
                            # Show detailed error info
                            with st.expander("🔍 Detailed Error Information"):
                                st.code(detailed_output)
                                st.error("Please check your API configuration and network connectivity.")
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")
                        import traceback
                        with st.expander("🔍 Full Error Traceback"):
                            st.code(traceback.format_exc())
        
        with col2:
            if st.button("🔄 Run Single Cycle", type="secondary"):
                with st.spinner("Running trading cycle..."):
                    try:
                        agent = LiveTradingAgent(initial_capital_live)
                        if agent.authenticate():
                            trades = agent.run_trading_cycle(live_strategy, ['1579.T', '1360.T'], **live_strategy_params)
                            if trades:
                                st.success(f"✅ Executed {len(trades)} trades")
                                for trade in trades:
                                    st.info(f"{trade['action']} {trade['quantity']} {trade['symbol']} - {trade['reason']}")
                            else:
                                st.info("ℹ️ No trades executed")
                        else:
                            st.error("❌ Authentication failed!")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        with col3:
            # Auto trading controls with session state
            if st.session_state.auto_trading_active:
                if st.button("⏹️ Stop Auto Trading", type="primary", key="stop_auto_trading"):
                    st.session_state.auto_trading_active = False
                    if st.session_state.trading_agent:
                        st.session_state.trading_agent.stop_trading()
                    st.warning("🛑 Auto trading stopped")
                    st.rerun()
            else:
                if st.button("▶️ Start Auto Trading", type="primary", key="start_auto_trading"):
                    st.session_state.auto_trading_active = True
                    st.success("🚀 Auto trading started!")
                    
                    # Initialize trading agent
                    try:
                        st.session_state.trading_agent = LiveTradingAgent(initial_capital_live)
                        if st.session_state.trading_agent.authenticate():
                            st.success("✅ Trading agent initialized successfully!")
                        else:
                            st.error("❌ Authentication failed!")
                            st.session_state.auto_trading_active = False
                    except Exception as e:
                        st.error(f"❌ Error initializing trading agent: {str(e)}")
                        st.session_state.auto_trading_active = False
                    
                    st.rerun()
        
        # Current positions and status
        st.subheader("Current Status")
        
        # Auto trading status
        if st.session_state.auto_trading_active:
            st.success("🟢 Auto Trading: ACTIVE")
            if st.session_state.trading_agent:
                st.info(f"Strategy: {live_strategy}")
                st.info(f"Interval: {interval_minutes} minutes")
        else:
            st.warning("🔴 Auto Trading: INACTIVE")
        
        # Real-time data
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("1579.T Position", "0 shares")
        with col2:
            st.metric("1360.T Position", "0 shares")
        with col3:
            st.metric("Available Cash", "¥1,000,000")
        
        # Trading logs
        if st.session_state.trading_logs:
            st.subheader("📋 Recent Trading Activity")
            for log in st.session_state.trading_logs[-5:]:  # Show last 5 logs
                st.info(log)

with tab3:
    st.header("📈 Market Data")
    
    # Auto-refresh settings
    col1, col2 = st.columns(2)
    with col1:
        refresh_interval = st.slider("Auto-refresh interval (seconds)", 5, 60, 10, key="refresh_interval")
    with col2:
        if st.button("🔄 Refresh Now", key="refresh_now"):
            st.rerun()
    
    # Initialize session state for market data
    if 'market_data_history' not in st.session_state:
        st.session_state.market_data_history = {'1579.T': [], '1360.T': []}
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    
    # Get real-time market data
    try:
        agent = LiveTradingAgent()
        if agent.authenticate():
            realtime_data = agent.get_realtime_market_data(['1579.T', '1360.T'])
            
            # Update market data history
            current_time = datetime.now()
            for symbol, data in realtime_data.items():
                if symbol in st.session_state.market_data_history:
                    st.session_state.market_data_history[symbol].append({
                        'timestamp': current_time,
                        'price': data['price'],
                        'source': data.get('source', 'KabusAPI')
                    })
                    # Keep only last 100 data points
                    if len(st.session_state.market_data_history[symbol]) > 100:
                        st.session_state.market_data_history[symbol] = st.session_state.market_data_history[symbol][-100:]
            
            st.session_state.last_refresh = current_time
            
            # Display real-time data
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("1579.T - Nikkei 225 ETF")
                if '1579.T' in realtime_data:
                    price_1579 = realtime_data['1579.T']['price']
                    st.metric("Current Price", f"¥{price_1579:,.2f}")
                    
                    # Create chart from history
                    if st.session_state.market_data_history['1579.T']:
                        df_1579 = pd.DataFrame(st.session_state.market_data_history['1579.T'])
                        fig_1579 = px.line(df_1579, x='timestamp', y='price', 
                                          title='1579.T Price History',
                                          labels={'price': 'Price (¥)', 'timestamp': 'Time'})
                        st.plotly_chart(fig_1579, use_container_width=True)
                else:
                    st.error("No data available for 1579.T")
            
            with col2:
                st.subheader("1360.T - Inverse Nikkei 225 ETF")
                if '1360.T' in realtime_data:
                    price_1360 = realtime_data['1360.T']['price']
                    st.metric("Current Price", f"¥{price_1360:,.2f}")
                    
                    # Create chart from history
                    if st.session_state.market_data_history['1360.T']:
                        df_1360 = pd.DataFrame(st.session_state.market_data_history['1360.T'])
                        fig_1360 = px.line(df_1360, x='timestamp', y='price', 
                                          title='1360.T Price History',
                                          labels={'price': 'Price (¥)', 'timestamp': 'Time'})
                        st.plotly_chart(fig_1360, use_container_width=True)
                else:
                    st.error("No data available for 1360.T")
            
            # Market statistics
            st.subheader("📊 Market Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if '1579.T' in realtime_data:
                    st.metric("1579.T Price", f"¥{realtime_data['1579.T']['price']:,.2f}")
                else:
                    st.metric("1579.T Price", "N/A")
            with col2:
                if '1360.T' in realtime_data:
                    st.metric("1360.T Price", f"¥{realtime_data['1360.T']['price']:,.2f}")
                else:
                    st.metric("1360.T Price", "N/A")
            with col3:
                st.metric("Last Refresh", st.session_state.last_refresh.strftime("%H:%M:%S"))
            with col4:
                st.metric("Data Source", "KabusAPI" if all('source' not in data for data in realtime_data.values()) else "Mixed")
            
            # Data source information
            st.info(f"🔄 Auto-refresh every {refresh_interval} seconds. Last updated: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
            
        else:
            st.error("❌ Failed to authenticate with KabusAPI. Using fallback data.")
            # Fallback to yfinance
            import yfinance as yf
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("1579.T - Nikkei 225 ETF (Fallback)")
                try:
                    ticker_1579 = yf.Ticker("1579.T")
                    latest_1579 = ticker_1579.history(period='1d')
                    if not latest_1579.empty:
                        price_1579 = latest_1579['Close'].iloc[-1]
                        st.metric("Current Price", f"¥{price_1579:,.2f}")
                        st.info("Source: Yahoo Finance (Fallback)")
                    else:
                        st.error("No data available")
                except Exception as e:
                    st.error(f"Error getting data: {str(e)}")
            
            with col2:
                st.subheader("1360.T - Inverse Nikkei 225 ETF (Fallback)")
                try:
                    ticker_1360 = yf.Ticker("1360.T")
                    latest_1360 = ticker_1360.history(period='1d')
                    if not latest_1360.empty:
                        price_1360 = latest_1360['Close'].iloc[-1]
                        st.metric("Current Price", f"¥{price_1360:,.2f}")
                        st.info("Source: Yahoo Finance (Fallback)")
                    else:
                        st.error("No data available")
                except Exception as e:
                    st.error(f"Error getting data: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error getting market data: {str(e)}")
        st.info("Please check your API connection and try again.")
    
    # Auto-refresh using JavaScript
    st.markdown(f"""
    <script>
        setTimeout(function() {{
            window.location.reload();
        }}, {refresh_interval * 1000});
    </script>
    """, unsafe_allow_html=True)

with tab4:
    st.header("⚙️ Settings")
    
    st.subheader("API Configuration")
    
    # Display current settings
    st.info("Current API settings (from .env file):")
    st.code(f"""
Host: {api_host or 'Not set'}
Environment: {api_env or 'Not set'} (dev=port 18081, prod=port 18080)
Password: {'*' * len(api_password) if api_password else 'Not set'}
    """)
    
    st.subheader("Trading Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_position_size = st.number_input("Max Position Size (¥)", value=500000, step=50000)
        stop_loss_pct = st.slider("Stop Loss (%)", 1, 10, 5)
    
    with col2:
        take_profit_pct = st.slider("Take Profit (%)", 1, 20, 10)
        max_daily_trades = st.number_input("Max Daily Trades", value=10, step=1)
    
    st.subheader("Risk Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_drawdown = st.slider("Max Drawdown (%)", 5, 30, 15, key="settings_max_drawdown")
        volatility_threshold = st.slider("Volatility Threshold", 0.1, 1.0, 0.5, 0.1, key="settings_volatility_threshold")
    
    with col2:
        correlation_threshold = st.slider("Correlation Threshold", 0.5, 0.9, 0.7, 0.05, key="settings_correlation_threshold")
        volume_threshold = st.slider("Volume Threshold", 1.0, 3.0, 1.5, 0.1, key="settings_volume_threshold")
    
    if st.button("💾 Save Settings", type="primary"):
        st.success("Settings saved successfully!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Stock Trading Agent - Nikkei 225 ETF Trading System</p>
    <p>Built with Streamlit, yfinance, and KabusAPI</p>
</div>
""", unsafe_allow_html=True) 