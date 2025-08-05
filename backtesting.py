import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

class BacktestingEngine:
    """
    Backtesting engine for trading algorithms on Nikkei 225 ETFs
    """
    
    def __init__(self, initial_capital: float = 1000000, 
                 transaction_cost: float = 0.002,  # 0.2% transaction cost
                 slippage: float = 0.001,  # 0.1% slippage
                 stop_loss: float = 0.05,  # 5% stop loss
                 take_profit: float = 0.15):  # 15% take profit
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {'1579.T': 0, '1360.T': 0}
        self.trade_history = []
        self.portfolio_values = []
        self.transaction_cost = transaction_cost
        self.slippage = slippage
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.position_entry_prices = {}  # Track entry prices for stop-loss/take-profit
        
    def get_historical_data(self, symbols: List[str], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical data from Yahoo Finance
        """
        data = {}
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            data[symbol] = df
        return data
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate common technical indicators
        """
        # Moving averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # Handle NaN values
        df = df.ffill().bfill()
        
        return df
    
    def execute_trade(self, symbol: str, action: str, quantity: int, price: float, date: datetime):
        """
        Execute a trade and update portfolio with transaction costs and slippage
        """
        # Apply slippage
        if action == 'BUY':
            execution_price = price * (1 + self.slippage)  # Pay slightly more when buying
        else:  # SELL
            execution_price = price * (1 - self.slippage)  # Receive slightly less when selling
        
        if action == 'BUY':
            gross_cost = quantity * execution_price
            transaction_fee = gross_cost * self.transaction_cost
            total_cost = gross_cost + transaction_fee
            
            if total_cost <= self.current_capital:
                self.current_capital -= total_cost
                self.positions[symbol] += quantity
                
                # Track entry price for new positions
                if symbol not in self.position_entry_prices or self.positions[symbol] == quantity:
                    self.position_entry_prices[symbol] = execution_price
                
                self.trade_history.append({
                    'date': date,
                    'symbol': symbol,
                    'action': action,
                    'quantity': quantity,
                    'price': execution_price,
                    'cost': total_cost,
                    'transaction_fee': transaction_fee,
                    'slippage_cost': quantity * price * self.slippage
                })
        elif action == 'SELL':
            if self.positions[symbol] >= quantity:
                gross_revenue = quantity * execution_price
                transaction_fee = gross_revenue * self.transaction_cost
                net_revenue = gross_revenue - transaction_fee
                
                self.current_capital += net_revenue
                self.positions[symbol] -= quantity
                self.trade_history.append({
                    'date': date,
                    'symbol': symbol,
                    'action': action,
                    'quantity': quantity,
                    'price': execution_price,
                    'revenue': net_revenue,
                    'transaction_fee': transaction_fee,
                    'slippage_cost': quantity * price * self.slippage
                })
    
    def calculate_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate current portfolio value
        """
        portfolio_value = self.current_capital
        for symbol, quantity in self.positions.items():
            if symbol in current_prices:
                portfolio_value += quantity * current_prices[symbol]
        return portfolio_value
    
    def check_risk_management(self, symbol: str, current_price: float, date: datetime) -> List[Dict]:
        """
        Check for stop-loss and take-profit triggers
        """
        signals = []
        
        if symbol in self.positions and self.positions[symbol] > 0 and symbol in self.position_entry_prices:
            entry_price = self.position_entry_prices[symbol]
            current_return = (current_price - entry_price) / entry_price
            
            # Stop-loss trigger
            if current_return <= -self.stop_loss:
                signals.append({
                    'symbol': symbol,
                    'action': 'SELL',
                    'quantity': self.positions[symbol],
                    'reason': f'Stop-loss triggered: {current_return:.2%} loss'
                })
            
            # Take-profit trigger
            elif current_return >= self.take_profit:
                signals.append({
                    'symbol': symbol,
                    'action': 'SELL',
                    'quantity': self.positions[symbol],
                    'reason': f'Take-profit triggered: {current_return:.2%} gain'
                })
        
        return signals
    
    def run_backtest(self, 
                    trading_algorithm: Callable,
                    symbols: List[str],
                    start_date: str,
                    end_date: str,
                    **algorithm_params) -> Dict:
        """
        Run backtesting with given trading algorithm
        """
        # Get historical data
        data = self.get_historical_data(symbols, start_date, end_date)
        
        # Calculate technical indicators for each symbol
        for symbol in symbols:
            data[symbol] = self.calculate_technical_indicators(data[symbol])
        
        # Align data by date
        common_dates = set.intersection(*[set(df.index) for df in data.values()])
        common_dates = sorted(list(common_dates))
        
        # Initialize tracking
        self.current_capital = self.initial_capital
        self.positions = {symbol: 0 for symbol in symbols}
        self.trade_history = []
        self.portfolio_values = []
        
        # Run backtest
        for date in common_dates:
            current_data = {symbol: data[symbol].loc[:date] for symbol in symbols}
            current_prices = {symbol: data[symbol].loc[date, 'Close'] for symbol in symbols}
            
            # Get trading signals from algorithm
            signals = trading_algorithm(current_data, current_prices, **algorithm_params)
            
            # Check for risk management triggers first
            risk_signals = []
            for symbol in symbols:
                risk_signals.extend(self.check_risk_management(symbol, current_prices[symbol], date))
            
            # Execute risk management trades first
            for signal in risk_signals:
                self.execute_trade(
                    symbol=signal['symbol'],
                    action=signal['action'],
                    quantity=signal['quantity'],
                    price=current_prices[signal['symbol']],
                    date=date
                )
            
            # Execute regular trading signals
            for signal in signals:
                self.execute_trade(
                    symbol=signal['symbol'],
                    action=signal['action'],
                    quantity=signal['quantity'],
                    price=current_prices[signal['symbol']],
                    date=date
                )
            
            # Record portfolio value
            portfolio_value = self.calculate_portfolio_value(current_prices)
            self.portfolio_values.append({
                'date': date,
                'portfolio_value': portfolio_value,
                'cash': self.current_capital,
                'positions': self.positions.copy()
            })
        
        # Calculate performance metrics
        final_value = self.portfolio_values[-1]['portfolio_value']
        total_return = (final_value - self.initial_capital) / self.initial_capital * 100
        
        # Calculate max drawdown
        portfolio_values = [pv['portfolio_value'] for pv in self.portfolio_values]
        peak = portfolio_values[0]
        max_drawdown = 0
        for value in portfolio_values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'trade_history': self.trade_history,
            'portfolio_values': self.portfolio_values,
            'total_trades': len(self.trade_history)
        }
    
    def plot_results(self, results: Dict):
        """
        Plot backtesting results
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Portfolio value over time
        dates = [pv['date'] for pv in results['portfolio_values']]
        values = [pv['portfolio_value'] for pv in results['portfolio_values']]
        
        axes[0, 0].plot(dates, values, label='Portfolio Value')
        axes[0, 0].axhline(y=self.initial_capital, color='r', linestyle='--', label='Initial Capital')
        axes[0, 0].set_title('Portfolio Value Over Time')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Drawdown
        peak = values[0]
        drawdowns = []
        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100
            drawdowns.append(drawdown)
        
        axes[0, 1].fill_between(dates, drawdowns, 0, alpha=0.3, color='red')
        axes[0, 1].set_title('Drawdown (%)')
        axes[0, 1].grid(True)
        
        # Trade distribution
        if results['trade_history']:
            trade_prices = [trade['price'] for trade in results['trade_history']]
            axes[1, 0].hist(trade_prices, bins=20, alpha=0.7)
            axes[1, 0].set_title('Trade Price Distribution')
            axes[1, 0].grid(True)
        
        # Performance summary
        summary_text = f"""
        Initial Capital: ¥{self.initial_capital:,.0f}
        Final Value: ¥{results['final_value']:,.0f}
        Total Return: {results['total_return']:.2f}%
        Max Drawdown: {results['max_drawdown']:.2f}%
        Total Trades: {results['total_trades']}
        """
        axes[1, 1].text(0.1, 0.5, summary_text, transform=axes[1, 1].transAxes, 
                        fontsize=12, verticalalignment='center')
        axes[1, 1].set_title('Performance Summary')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.show()

# Example usage
if __name__ == "__main__":
    # This will be implemented in the next step with actual trading algorithms
    print("Backtesting engine created successfully!")
    print("Trading algorithms will be implemented in the next step.") 