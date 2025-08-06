import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd
from trading_algorithms import STRATEGIES

# Load environment variables
load_dotenv()

class KabusAPIClient:
    """
    Client for KabusAPI trading interface
    """
    
    def __init__(self):
        self.host = os.getenv('KABUSAPI_HOST', 'localhost')
        self.port = os.getenv('KABUSAPI_PORT', '18081')  # Changed to dev port
        self.password = os.getenv('KABUSAPI_PASSWORD', '')
        self.base_url = f"http://{self.host}:{self.port}/kabusapi"
        self.token = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with KabusAPI
        """
        try:
            url = f"{self.base_url}/token"
            headers = {'Content-Type': 'application/json'}
            data = {'APIPassword': self.password}
            
            print(f"🔐 Attempting authentication to: {url}")
            print(f"📋 Request data: {data}")
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            print(f"📡 Response status: {response.status_code}")
            print(f"📡 Response headers: {dict(response.headers)}")
            
            # Print response content for debugging
            try:
                response_text = response.text
                print(f"📡 Response content: {response_text}")
            except Exception as e:
                print(f"❌ Error reading response: {str(e)}")
            
            response.raise_for_status()
            
            result = response.json()
            print(f"📊 Parsed response: {result}")
            
            if result.get('ResultCode') == 0:
                self.token = result.get('Token')
                print(f"✅ Authentication successful! Token: {self.token[:10]}..." if self.token else "✅ Authentication successful!")
                return True
            else:
                error_msg = result.get('ResultText', 'Unknown error')
                print(f"❌ Authentication failed: {error_msg}")
                print(f"❌ Result code: {result.get('ResultCode')}")
                return False
                
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection error: {str(e)}")
            print(f"🔍 Check if KabusAPI is running on {self.host}:{self.port}")
            print(f"🔍 Verify network connectivity and firewall settings")
            return False
        except requests.exceptions.Timeout as e:
            print(f"❌ Timeout error: {str(e)}")
            print(f"🔍 API server may be slow or unresponsive")
            return False
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP error: {str(e)}")
            print(f"📡 Status code: {e.response.status_code if hasattr(e, 'response') else 'Unknown'}")
            try:
                error_content = e.response.text if hasattr(e, 'response') else 'No content'
                print(f"📡 Error content: {error_content}")
            except:
                print("📡 Could not read error content")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {str(e)}")
            print(f"📡 Raw response: {response.text if 'response' in locals() else 'No response'}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            print(f"🔍 Error type: {type(e).__name__}")
            import traceback
            print(f"🔍 Full traceback: {traceback.format_exc()}")
            return False
    
    def get_token_header(self) -> Dict[str, str]:
        """
        Get headers with authentication token
        """
        if not self.token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        return {
            'Content-Type': 'application/json',
            'X-API-KEY': self.token
        }
    
    def convert_symbol_to_api_format(self, symbol: str) -> str:
        """
        Convert Yahoo Finance symbol to KabusAPI format
        e.g., '1579.T' -> '1579@1' (Tokyo Exchange)
        """
        # Map of common symbols to their exchange codes
        symbol_mapping = {
            '1579.T': '1579@1',  # Nikkei 225 ETF on Tokyo Exchange
            '1360.T': '1360@1',  # Inverse Nikkei 225 ETF on Tokyo Exchange
        }
        
        if symbol in symbol_mapping:
            return symbol_mapping[symbol]
        
        # Default mapping for .T symbols (Tokyo Exchange = 1)
        if symbol.endswith('.T'):
            code = symbol.replace('.T', '')
            return f"{code}@1"
        
        # For other symbols, assume Tokyo Exchange
        return f"{symbol}@1"
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """
        Get symbol information
        """
        try:
            api_symbol = self.convert_symbol_to_api_format(symbol)
            url = f"{self.base_url}/symbol/{api_symbol}"
            headers = self.get_token_header()
            
            print(f"🔍 Getting symbol info for {symbol} -> {api_symbol}")
            print(f"📡 Request URL: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            print(f"📊 Symbol info response: {result}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error getting symbol info for {symbol}: {str(e)}")
            return None
    
    def get_market_price(self, symbols: List[str]) -> Dict[str, float]:
        """
        Get current market prices for symbols using KabusAPI board endpoint
        """
        prices = {}
        
        for symbol in symbols:
            try:
                api_symbol = self.convert_symbol_to_api_format(symbol)
                url = f"{self.base_url}/board/{api_symbol}"
                headers = self.get_token_header()
                
                print(f"💰 Getting market price for {symbol} -> {api_symbol}")
                
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                result = response.json()
                print(f"📊 Board response for {symbol}: {result}")
                
                # Extract current price from board data
                if result.get('ResultCode') == 0:
                    board_data = result.get('Board', {})
                    current_price = board_data.get('CurrentPrice')
                    if current_price:
                        prices[symbol] = float(current_price)
                        print(f"✅ Got price for {symbol}: ¥{current_price}")
                    else:
                        print(f"⚠️ No current price found for {symbol}")
                else:
                    print(f"❌ Board API error for {symbol}: {result.get('ResultText', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ Error getting price for {symbol}: {str(e)}")
                # Fallback to yfinance
                try:
                    ticker = yf.Ticker(symbol)
                    current_price = ticker.info.get('regularMarketPrice')
                    if current_price:
                        prices[symbol] = current_price
                        print(f"✅ Got fallback price for {symbol}: ¥{current_price}")
                    else:
                        # Get latest close price
                        hist = ticker.history(period='1d')
                        if not hist.empty:
                            prices[symbol] = hist['Close'].iloc[-1]
                            print(f"✅ Got fallback close price for {symbol}: ¥{hist['Close'].iloc[-1]}")
                except Exception as fallback_error:
                    print(f"❌ Fallback error for {symbol}: {str(fallback_error)}")
                    
        return prices
    
    def place_order(self, 
                   symbol: str,
                   side: str,  # 'BUY' or 'SELL'
                   quantity: int,
                   order_type: str = 'MARKET') -> Optional[Dict]:
        """
        Place an order through KabusAPI
        """
        try:
            url = f"{self.base_url}/sendorder"
            headers = self.get_token_header()
            
            # Convert symbol to API format
            api_symbol = self.convert_symbol_to_api_format(symbol)
            
            # Get current price for limit orders
            current_price = self.get_market_price([symbol]).get(symbol)
            
            # Convert side to API format (1=BUY, 2=SELL)
            side_code = 1 if side == 'BUY' else 2
            
            data = {
                'Symbol': api_symbol,
                'Exchange': 1,  # 1 for Tokyo Stock Exchange
                'SecurityType': 1,  # 1 for stocks
                'Side': side_code,
                'CashMargin': 1,  # 1 for cash trading
                'DelivType': 2,  # 2 for delivery
                'AccountType': 2,  # 2 for general account
                'Qty': quantity,
                'FrontOrderType': 30 if order_type == 'MARKET' else 20,  # 30 for market, 20 for limit
                'Price': current_price if order_type == 'LIMIT' else 0,
                'ExpireDay': 0,  # 0 for same day
            }
            
            print(f"📤 Placing order: {side} {quantity} {symbol} -> {api_symbol}")
            print(f"📋 Order data: {data}")
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            print(f"📡 Response status: {response.status_code}")
            try:
                response_text = response.text
                print(f"📡 Response content: {response_text}")
            except Exception as e:
                print(f"❌ Error reading response: {str(e)}")
            
            response.raise_for_status()
            
            result = response.json()
            print(f"📊 Order response: {result}")
            
            if result.get('ResultCode') == 0:
                order_id = result.get('OrderId', 'Unknown')
                print(f"✅ Order placed successfully: {side} {quantity} {symbol} (Order ID: {order_id})")
                return result
            else:
                error_msg = result.get('ResultText', 'Unknown error')
                print(f"❌ Order failed: {error_msg}")
                print(f"❌ Result code: {result.get('ResultCode')}")
                return None
                
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection error placing order: {str(e)}")
            return None
        except requests.exceptions.Timeout as e:
            print(f"❌ Timeout error placing order: {str(e)}")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP error placing order: {str(e)}")
            print(f"📡 Status code: {e.response.status_code if hasattr(e, 'response') else 'Unknown'}")
            try:
                error_content = e.response.text if hasattr(e, 'response') else 'No content'
                print(f"📡 Error content: {error_content}")
            except:
                print("📡 Could not read error content")
            return None
        except Exception as e:
            print(f"❌ Unexpected error placing order: {str(e)}")
            print(f"🔍 Error type: {type(e).__name__}")
            import traceback
            print(f"🔍 Full traceback: {traceback.format_exc()}")
            return None
    
    def get_positions(self) -> List[Dict]:
        """
        Get current positions
        """
        try:
            url = f"{self.base_url}/positions"
            headers = self.get_token_header()
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error getting positions: {str(e)}")
            return []

class LiveTradingAgent:
    """
    Live trading agent that executes trades based on algorithms
    """
    
    def __init__(self, initial_capital: float = 1000000):
        self.api_client = KabusAPIClient()
        self.initial_capital = initial_capital
        self.positions = {'1579.T': 0, '1360.T': 0}
        self.trade_history = []
        self.is_running = False
        
    def authenticate(self) -> bool:
        """
        Authenticate with the trading API
        """
        return self.api_client.authenticate()
    
    def get_current_data(self, symbols: List[str], lookback_days: int = 50) -> Dict[str, pd.DataFrame]:
        """
        Get current market data for analysis
        """
        data = {}
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date)
                if not df.empty:
                    data[symbol] = df
            except Exception as e:
                print(f"Error getting data for {symbol}: {str(e)}")
                continue
        
        return data
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators (same as in backtesting)
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
        
        return df
    
    def execute_signals(self, signals: List[Dict]) -> List[Dict]:
        """
        Execute trading signals
        """
        executed_trades = []
        
        for signal in signals:
            try:
                symbol = signal['symbol']
                action = signal['action']
                quantity = signal['quantity']
                
                # Place order
                order_result = self.api_client.place_order(
                    symbol=symbol,
                    side=action,
                    quantity=quantity
                )
                
                if order_result:
                    # Update positions
                    if action == 'BUY':
                        self.positions[symbol] += quantity
                    else:  # SELL
                        self.positions[symbol] -= quantity
                    
                    # Record trade
                    trade_record = {
                        'timestamp': datetime.now(),
                        'symbol': symbol,
                        'action': action,
                        'quantity': quantity,
                        'reason': signal.get('reason', 'Algorithm signal'),
                        'order_result': order_result
                    }
                    
                    self.trade_history.append(trade_record)
                    executed_trades.append(trade_record)
                    
                    print(f"Executed: {action} {quantity} {symbol} - {signal.get('reason', 'Algorithm signal')}")
                
            except Exception as e:
                print(f"Error executing signal: {str(e)}")
                continue
        
        return executed_trades
    
    def run_trading_cycle(self, 
                          strategy_name: str,
                          symbols: List[str] = ['1579.T', '1360.T'],
                          **strategy_params) -> List[Dict]:
        """
        Run one trading cycle with the specified strategy
        """
        if strategy_name not in STRATEGIES:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        # Get current market data
        data = self.get_current_data(symbols)
        
        if not data:
            print("No market data available")
            return []
        
        # Calculate technical indicators
        for symbol in symbols:
            if symbol in data:
                data[symbol] = self.calculate_technical_indicators(data[symbol])
        
        # Get current prices
        current_prices = self.api_client.get_market_price(symbols)
        
        if not current_prices:
            print("No current prices available")
            return []
        
        # Generate trading signals
        strategy_func = STRATEGIES[strategy_name]
        signals = strategy_func(data, current_prices, **strategy_params)
        
        # Execute signals
        executed_trades = self.execute_signals(signals)
        
        return executed_trades
    
    def start_trading(self, 
                     strategy_name: str,
                     symbols: List[str] = ['1579.T', '1360.T'],
                     interval_minutes: int = 15,
                     **strategy_params):
        """
        Start continuous trading
        """
        if not self.authenticate():
            print("Failed to authenticate with trading API")
            return
        
        print(f"Starting live trading with strategy: {strategy_name}")
        print(f"Symbols: {symbols}")
        print(f"Interval: {interval_minutes} minutes")
        print("Press Ctrl+C to stop")
        
        self.is_running = True
        
        try:
            while self.is_running:
                print(f"\n--- Trading cycle at {datetime.now()} ---")
                
                # Run trading cycle
                executed_trades = self.run_trading_cycle(strategy_name, symbols, **strategy_params)
                
                if executed_trades:
                    print(f"Executed {len(executed_trades)} trades")
                else:
                    print("No trades executed")
                
                # Print current positions
                print(f"Current positions: {self.positions}")
                
                # Wait for next cycle
                print(f"Waiting {interval_minutes} minutes until next cycle...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\nStopping live trading...")
            self.is_running = False
    
    def get_trading_summary(self) -> Dict:
        """
        Get summary of trading activity
        """
        return {
            'total_trades': len(self.trade_history),
            'current_positions': self.positions,
            'trade_history': self.trade_history
        }

# Example usage
if __name__ == "__main__":
    # Initialize trading agent
    agent = LiveTradingAgent(initial_capital=1000000)
    
    # Test authentication
    if agent.authenticate():
        print("Successfully authenticated with KabusAPI")
        
        # Run a single trading cycle
        trades = agent.run_trading_cycle('mean_reversion', ['1579.T', '1360.T'])
        print(f"Executed {len(trades)} trades")
        
        # Get summary
        summary = agent.get_trading_summary()
        print(f"Trading summary: {summary}")
    else:
        print("Failed to authenticate. Please check your API credentials.") 