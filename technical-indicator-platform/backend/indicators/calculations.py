import pandas as pd
import numpy as np
from ta import add_all_ta_features
from ta.utils import dropna
from ta.volatility import BollingerBands, AverageTrueRange
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import SMAIndicator, EMAIndicator, ADXIndicator, MACD
from ta.volume import OnBalanceVolumeIndicator

class TechnicalIndicators:
    def __init__(self, df):
        self.df = df.copy()
        
    def calculate_sma(self, period=20):
        """Simple Moving Average"""
        indicator = SMAIndicator(close=self.df['close'], window=period)
        self.df[f'sma_{period}'] = indicator.sma_indicator()
        return self.df
    
    def calculate_ema(self, period=20):
        """Exponential Moving Average"""
        indicator = EMAIndicator(close=self.df['close'], window=period)
        self.df[f'ema_{period}'] = indicator.ema_indicator()
        return self.df
    
    def calculate_rsi(self, period=14):
        """Relative Strength Index"""
        indicator = RSIIndicator(close=self.df['close'], window=period)
        self.df['rsi'] = indicator.rsi()
        return self.df
    
    def calculate_macd(self):
        """MACD"""
        indicator = MACD(close=self.df['close'])
        self.df['macd'] = indicator.macd()
        self.df['macd_signal'] = indicator.macd_signal()
        self.df['macd_diff'] = indicator.macd_diff()
        return self.df
    
    def calculate_bollinger_bands(self, period=20, std_dev=2):
        """Bollinger Bands"""
        indicator = BollingerBands(close=self.df['close'], window=period, window_dev=std_dev)
        self.df['bb_high'] = indicator.bollinger_hband()
        self.df['bb_mid'] = indicator.bollinger_mavg()
        self.df['bb_low'] = indicator.bollinger_lband()
        return self.df
    
    def calculate_stochastic(self, period=14):
        """Stochastic Oscillator"""
        indicator = StochasticOscillator(
            high=self.df['high'], 
            low=self.df['low'], 
            close=self.df['close'], 
            window=period
        )
        self.df['stoch_k'] = indicator.stoch()
        self.df['stoch_d'] = indicator.stoch_signal()
        return self.df
    
    def calculate_atr(self, period=14):
        """Average True Range"""
        indicator = AverageTrueRange(
            high=self.df['high'], 
            low=self.df['low'], 
            close=self.df['close'], 
            window=period
        )
        self.df['atr'] = indicator.average_true_range()
        return self.df
    
    def calculate_obv(self):
        """On-Balance Volume"""
        indicator = OnBalanceVolumeIndicator(close=self.df['close'], volume=self.df['volume'])
        self.df['obv'] = indicator.on_balance_volume()
        return self.df
    
    def calculate_adx(self, period=14):
        """Average Directional Index"""
        indicator = ADXIndicator(
            high=self.df['high'], 
            low=self.df['low'], 
            close=self.df['close'], 
            window=period
        )
        self.df['adx'] = indicator.adx()
        return self.df
