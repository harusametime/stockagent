import pandas as pd
import numpy as np
from typing import Dict, List, Callable
from datetime import datetime

class TradingAlgorithms:
    """
    Collection of trading algorithms for Nikkei 225 ETFs
    """
    
    @staticmethod
    def mean_reversion_strategy(data: Dict[str, pd.DataFrame], 
                              current_prices: Dict[str, float],
                              rsi_oversold: float = 30,
                              rsi_overbought: float = 70,
                              bb_std_multiplier: float = 2.0) -> List[Dict]:
        """
        Mean reversion strategy using RSI and Bollinger Bands
        """
        signals = []
        
        for symbol, df in data.items():
            if len(df) < 50:  # Need enough data for indicators
                continue
                
            current_row = df.iloc[-1]
            
            # RSI signals
            if current_row['RSI'] < rsi_oversold:
                # Oversold - buy signal
                quantity = int(100000 / current_prices[symbol])  # Buy ¥100k worth
                signals.append({
                    'symbol': symbol,
                    'action': 'BUY',
                    'quantity': quantity,
                    'reason': f'RSI oversold ({current_row["RSI"]:.1f})'
                })
            elif current_row['RSI'] > rsi_overbought:
                # Overbought - sell signal
                quantity = int(100000 / current_prices[symbol])  # Sell ¥100k worth
                signals.append({
                    'symbol': symbol,
                    'action': 'SELL',
                    'quantity': quantity,
                    'reason': f'RSI overbought ({current_row["RSI"]:.1f})'
                })
            
            # Bollinger Bands signals
            if current_prices[symbol] < current_row['BB_Lower']:
                # Price below lower band - buy signal
                quantity = int(100000 / current_prices[symbol])
                signals.append({
                    'symbol': symbol,
                    'action': 'BUY',
                    'quantity': quantity,
                    'reason': f'Price below BB lower ({current_prices[symbol]:.0f} < {current_row["BB_Lower"]:.0f})'
                })
            elif current_prices[symbol] > current_row['BB_Upper']:
                # Price above upper band - sell signal
                quantity = int(100000 / current_prices[symbol])
                signals.append({
                    'symbol': symbol,
                    'action': 'SELL',
                    'quantity': quantity,
                    'reason': f'Price above BB upper ({current_prices[symbol]:.0f} > {current_row["BB_Upper"]:.0f})'
                })
        
        return signals
    
    @staticmethod
    def momentum_strategy(data: Dict[str, pd.DataFrame],
                        current_prices: Dict[str, float],
                        macd_threshold: float = 0.0,
                        volume_threshold: float = 1.5) -> List[Dict]:
        """
        Momentum strategy using MACD and volume
        """
        signals = []
        
        for symbol, df in data.items():
            if len(df) < 50:
                continue
                
            current_row = df.iloc[-1]
            
            # MACD signals
            if current_row['MACD'] > current_row['MACD_Signal'] and current_row['MACD'] > macd_threshold:
                # MACD bullish crossover
                quantity = int(150000 / current_prices[symbol])
                signals.append({
                    'symbol': symbol,
                    'action': 'BUY',
                    'quantity': quantity,
                    'reason': f'MACD bullish ({current_row["MACD"]:.3f} > {current_row["MACD_Signal"]:.3f})'
                })
            elif current_row['MACD'] < current_row['MACD_Signal'] and current_row['MACD'] < -macd_threshold:
                # MACD bearish crossover
                quantity = int(150000 / current_prices[symbol])
                signals.append({
                    'symbol': symbol,
                    'action': 'SELL',
                    'quantity': quantity,
                    'reason': f'MACD bearish ({current_row["MACD"]:.3f} < {current_row["MACD_Signal"]:.3f})'
                })
            
            # Volume confirmation
            if current_row['Volume_Ratio'] > volume_threshold:
                # High volume - potential trend continuation
                if current_row['Close'] > current_row['SMA_20']:
                    quantity = int(100000 / current_prices[symbol])
                    signals.append({
                        'symbol': symbol,
                        'action': 'BUY',
                        'quantity': quantity,
                        'reason': f'High volume uptrend (Volume ratio: {current_row["Volume_Ratio"]:.1f})'
                    })
                elif current_row['Close'] < current_row['SMA_20']:
                    quantity = int(100000 / current_prices[symbol])
                    signals.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': quantity,
                        'reason': f'High volume downtrend (Volume ratio: {current_row["Volume_Ratio"]:.1f})'
                    })
        
        return signals
    
    @staticmethod
    def pairs_trading_strategy(data: Dict[str, pd.DataFrame],
                             current_prices: Dict[str, float],
                             correlation_threshold: float = 0.7,
                             z_score_threshold: float = 2.0) -> List[Dict]:
        """
        Pairs trading strategy for 1579.T and 1360.T
        Since these ETFs are inversely correlated, we can exploit divergences
        """
        signals = []
        
        if '1579.T' not in data or '1360.T' not in data:
            return signals
            
        df_1579 = data['1579.T']
        df_1360 = data['1360.T']
        
        if len(df_1579) < 50 or len(df_1360) < 50:
            return signals
        
        # Calculate rolling correlation
        window = 20
        if len(df_1579) >= window:
            correlation = df_1579['Close'].rolling(window).corr(df_1360['Close'])
            current_corr = correlation.iloc[-1]
            
            if abs(current_corr) > correlation_threshold:
                # Calculate z-score of price ratio
                price_ratio = df_1579['Close'] / df_1360['Close']
                ratio_mean = price_ratio.rolling(window).mean()
                ratio_std = price_ratio.rolling(window).std()
                z_score = (price_ratio.iloc[-1] - ratio_mean.iloc[-1]) / ratio_std.iloc[-1]
                
                if z_score > z_score_threshold:
                    # 1579.T is overvalued relative to 1360.T
                    quantity_1579 = int(100000 / current_prices['1579.T'])
                    quantity_1360 = int(100000 / current_prices['1360.T'])
                    
                    signals.extend([
                        {
                            'symbol': '1579.T',
                            'action': 'SELL',
                            'quantity': quantity_1579,
                            'reason': f'Pairs trading: 1579.T overvalued (z-score: {z_score:.2f})'
                        },
                        {
                            'symbol': '1360.T',
                            'action': 'BUY',
                            'quantity': quantity_1360,
                            'reason': f'Pairs trading: 1360.T undervalued (z-score: {z_score:.2f})'
                        }
                    ])
                elif z_score < -z_score_threshold:
                    # 1360.T is overvalued relative to 1579.T
                    quantity_1579 = int(100000 / current_prices['1579.T'])
                    quantity_1360 = int(100000 / current_prices['1360.T'])
                    
                    signals.extend([
                        {
                            'symbol': '1579.T',
                            'action': 'BUY',
                            'quantity': quantity_1579,
                            'reason': f'Pairs trading: 1579.T undervalued (z-score: {z_score:.2f})'
                        },
                        {
                            'symbol': '1360.T',
                            'action': 'SELL',
                            'quantity': quantity_1360,
                            'reason': f'Pairs trading: 1360.T overvalued (z-score: {z_score:.2f})'
                        }
                    ])
        
        return signals
    
    @staticmethod
    def trend_following_strategy(data: Dict[str, pd.DataFrame],
                               current_prices: Dict[str, float],
                               short_window: int = 10,
                               long_window: int = 30) -> List[Dict]:
        """
        Trend following strategy using moving average crossovers
        """
        signals = []
        
        for symbol, df in data.items():
            if len(df) < long_window:
                continue
                
            # Calculate additional moving averages
            df['SMA_Short'] = df['Close'].rolling(window=short_window).mean()
            df['SMA_Long'] = df['Close'].rolling(window=long_window).mean()
            
            current_row = df.iloc[-1]
            prev_row = df.iloc[-2] if len(df) > 1 else None
            
            if prev_row is not None:
                # Golden cross (short MA crosses above long MA)
                if (current_row['SMA_Short'] > current_row['SMA_Long'] and 
                    prev_row['SMA_Short'] <= prev_row['SMA_Long']):
                    quantity = int(200000 / current_prices[symbol])
                    signals.append({
                        'symbol': symbol,
                        'action': 'BUY',
                        'quantity': quantity,
                        'reason': f'Golden cross ({short_window}MA > {long_window}MA)'
                    })
                
                # Death cross (short MA crosses below long MA)
                elif (current_row['SMA_Short'] < current_row['SMA_Long'] and 
                      prev_row['SMA_Short'] >= prev_row['SMA_Long']):
                    quantity = int(200000 / current_prices[symbol])
                    signals.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': quantity,
                        'reason': f'Death cross ({short_window}MA < {long_window}MA)'
                    })
        
        return signals
    
    @staticmethod
    def volatility_breakout_strategy(data: Dict[str, pd.DataFrame],
                                   current_prices: Dict[str, float],
                                   atr_period: int = 14,
                                   breakout_multiplier: float = 2.0) -> List[Dict]:
        """
        Volatility breakout strategy using ATR (Average True Range)
        """
        signals = []
        
        for symbol, df in data.items():
            if len(df) < atr_period + 1:
                continue
                
            # Calculate ATR
            high_low = df['High'] - df['Low']
            high_close = np.abs(df['High'] - df['Close'].shift())
            low_close = np.abs(df['Low'] - df['Close'].shift())
            
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            atr = true_range.rolling(window=atr_period).mean()
            
            current_row = df.iloc[-1]
            current_atr = atr.iloc[-1]
            
            # Breakout signals
            upper_band = current_row['SMA_20'] + (breakout_multiplier * current_atr)
            lower_band = current_row['SMA_20'] - (breakout_multiplier * current_atr)
            
            if current_prices[symbol] > upper_band:
                # Upside breakout
                quantity = int(150000 / current_prices[symbol])
                signals.append({
                    'symbol': symbol,
                    'action': 'BUY',
                    'quantity': quantity,
                    'reason': f'Upside breakout (Price: {current_prices[symbol]:.0f} > {upper_band:.0f})'
                })
            elif current_prices[symbol] < lower_band:
                # Downside breakout
                quantity = int(150000 / current_prices[symbol])
                signals.append({
                    'symbol': symbol,
                    'action': 'SELL',
                    'quantity': quantity,
                    'reason': f'Downside breakout (Price: {current_prices[symbol]:.0f} < {lower_band:.0f})'
                })
        
        return signals
    
    @staticmethod
    def combined_strategy(data: Dict[str, pd.DataFrame],
                        current_prices: Dict[str, float],
                        **params) -> List[Dict]:
        """
        Combined strategy using multiple signals
        """
        signals = []
        
        # Get signals from different strategies
        mean_rev_signals = TradingAlgorithms.mean_reversion_strategy(data, current_prices, **params)
        momentum_signals = TradingAlgorithms.momentum_strategy(data, current_prices, **params)
        pairs_signals = TradingAlgorithms.pairs_trading_strategy(data, current_prices, **params)
        trend_signals = TradingAlgorithms.trend_following_strategy(data, current_prices, **params)
        
        # Combine signals (avoid duplicates by symbol)
        all_signals = mean_rev_signals + momentum_signals + pairs_signals + trend_signals
        
        # Group by symbol and action
        signal_groups = {}
        for signal in all_signals:
            key = (signal['symbol'], signal['action'])
            if key not in signal_groups:
                signal_groups[key] = []
            signal_groups[key].append(signal)
        
        # Take the signal with highest quantity for each symbol-action pair
        for (symbol, action), signal_list in signal_groups.items():
            best_signal = max(signal_list, key=lambda x: x['quantity'])
            signals.append(best_signal)
        
        return signals

# Strategy registry for easy access
STRATEGIES = {
    'mean_reversion': TradingAlgorithms.mean_reversion_strategy,
    'momentum': TradingAlgorithms.momentum_strategy,
    'pairs_trading': TradingAlgorithms.pairs_trading_strategy,
    'trend_following': TradingAlgorithms.trend_following_strategy,
    'volatility_breakout': TradingAlgorithms.volatility_breakout_strategy,
    'combined': TradingAlgorithms.combined_strategy
}

if __name__ == "__main__":
    print("Trading algorithms created successfully!")
    print("Available strategies:", list(STRATEGIES.keys())) 