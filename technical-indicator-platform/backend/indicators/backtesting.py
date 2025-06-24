import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class BacktestEngine:
    def __init__(self, df, indicator_name):
        self.df = df.copy()
        self.indicator_name = indicator_name
        self.trades = []
        
    def generate_signals(self):
        """Generate buy/sell signals based on indicator"""
        if self.indicator_name == 'sma_crossover':
            self.df['signal'] = 0
            self.df['signal'][self.df['close'] > self.df['sma_50']] = 1
            self.df['signal'][self.df['close'] < self.df['sma_50']] = -1
            
        elif self.indicator_name == 'rsi':
            self.df['signal'] = 0
            self.df['signal'][self.df['rsi'] < 30] = 1  # Oversold
            self.df['signal'][self.df['rsi'] > 70] = -1  # Overbought
            
        elif self.indicator_name == 'macd':
            self.df['signal'] = 0
            self.df['signal'][self.df['macd'] > self.df['macd_signal']] = 1
            self.df['signal'][self.df['macd'] < self.df['macd_signal']] = -1
            
        elif self.indicator_name == 'bollinger_bands':
            self.df['signal'] = 0
            self.df['signal'][self.df['close'] < self.df['bb_low']] = 1
            self.df['signal'][self.df['close'] > self.df['bb_high']] = -1
            
        # Generate positions
        self.df['position'] = self.df['signal'].diff()
        
    def calculate_returns(self):
        """Calculate returns for each trade"""
        self.df['returns'] = self.df['close'].pct_change()
        self.df['strategy_returns'] = self.df['returns'] * self.df['signal'].shift(1)
        self.df['cumulative_returns'] = (1 + self.df['strategy_returns']).cumprod()
        
    def calculate_metrics(self):
        """Calculate performance metrics"""
        # Success rate
        winning_trades = len(self.df[self.df['strategy_returns'] > 0])
        total_trades = len(self.df[self.df['position'] != 0])
        success_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Average return
        avg_return = self.df['strategy_returns'].mean() * 100
        
        # Maximum drawdown
        cumulative = self.df['cumulative_returns']
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # Sharpe ratio
        sharpe_ratio = (self.df['strategy_returns'].mean() / 
                       self.df['strategy_returns'].std() * np.sqrt(252)) if self.df['strategy_returns'].std() != 0 else 0
        
        return {
            'success_rate': success_rate,
            'avg_return': avg_return,
            'total_signals': total_trades,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio
        }
    
    def run_backtest(self):
        """Run complete backtest"""
        self.generate_signals()
        self.calculate_returns()
        metrics = self.calculate_metrics()
        return metrics