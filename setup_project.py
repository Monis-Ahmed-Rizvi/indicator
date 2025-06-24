#!/usr/bin/env python3
"""
Technical Indicator Platform - Automated Setup Script
This script creates the entire project structure and files automatically.
Just run: python setup_project.py
"""

import os
import json

def create_file(path, content):
    """Create a file with the given content"""
    # Create directory if it doesn't exist
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    # Write content to file
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {path}")

def setup_project():
    """Create the entire project structure"""
    
    # Create main project directory
    project_root = "technical-indicator-platform"
    if not os.path.exists(project_root):
        os.makedirs(project_root)
    os.chdir(project_root)
    
    # Backend files
    print("\n=== Creating Backend Files ===\n")
    
    # requirements.txt
    create_file("backend/requirements.txt", """Django==4.2.0
djangorestframework==3.14.0
django-cors-headers==4.0.0
yfinance==0.2.18
pandas==2.0.0
numpy==1.24.0
ta==0.10.2
python-dateutil==2.8.2
psycopg2-binary==2.9.6""")
    
    # manage.py
    create_file("backend/manage.py", """#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)""")
    
    # config/__init__.py
    create_file("backend/config/__init__.py", "")
    
    # config/settings.py
    create_file("backend/config/settings.py", """import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-your-secret-key-here-change-in-production'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'stocks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100
}""")
    
    # config/urls.py
    create_file("backend/config/urls.py", """from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]""")
    
    # config/wsgi.py
    create_file("backend/config/wsgi.py", """import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()""")
    
    # stocks/__init__.py
    create_file("backend/stocks/__init__.py", "")
    
    # stocks/models.py
    create_file("backend/stocks/models.py", """from django.db import models
from django.utils import timezone

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    company_name = models.CharField(max_length=255)
    sector = models.CharField(max_length=100, blank=True)
    last_updated = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.symbol} - {self.company_name}"
    
    class Meta:
        ordering = ['symbol']

class IndicatorResult(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='indicator_results')
    indicator_name = models.CharField(max_length=50)
    timeframe = models.CharField(max_length=20)
    success_rate = models.FloatField()
    avg_return = models.FloatField()
    total_signals = models.IntegerField()
    max_drawdown = models.FloatField(default=0)
    sharpe_ratio = models.FloatField(default=0)
    date_calculated = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.stock.symbol} - {self.indicator_name} ({self.timeframe})"
    
    class Meta:
        ordering = ['-success_rate']

class StockData(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='price_data')
    date = models.DateField()
    open_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    close_price = models.FloatField()
    volume = models.BigIntegerField()
    
    def __str__(self):
        return f"{self.stock.symbol} - {self.date}"
    
    class Meta:
        unique_together = ['stock', 'date']
        ordering = ['-date']""")
    
    # stocks/serializers.py
    create_file("backend/stocks/serializers.py", """from rest_framework import serializers
from .models import Stock, IndicatorResult, StockData

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'company_name', 'sector', 'last_updated']

class IndicatorResultSerializer(serializers.ModelSerializer):
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)
    
    class Meta:
        model = IndicatorResult
        fields = ['id', 'stock_symbol', 'indicator_name', 'timeframe', 
                 'success_rate', 'avg_return', 'total_signals', 
                 'max_drawdown', 'sharpe_ratio', 'date_calculated']

class StockDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockData
        fields = ['date', 'open_price', 'high_price', 'low_price', 
                 'close_price', 'volume']

class AnalysisRequestSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=10)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    indicators = serializers.ListField(
        child=serializers.CharField(max_length=50)
    )""")
    
    # stocks/views.py
    create_file("backend/stocks/views.py", """from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from .models import Stock, IndicatorResult, StockData
from .serializers import (
    StockSerializer, IndicatorResultSerializer, 
    StockDataSerializer, AnalysisRequestSerializer
)
from indicators.calculations import TechnicalIndicators
from indicators.backtesting import BacktestEngine

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        \"\"\"Search stocks by symbol\"\"\"
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Query parameter required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Try to fetch from yfinance if not in database
        ticker = yf.Ticker(query.upper())
        info = ticker.info
        
        if 'symbol' in info:
            stock, created = Stock.objects.get_or_create(
                symbol=info['symbol'],
                defaults={
                    'company_name': info.get('longName', ''),
                    'sector': info.get('sector', '')
                }
            )
            serializer = StockSerializer(stock)
            return Response(serializer.data)
        
        return Response({'error': 'Stock not found'}, 
                       status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        \"\"\"Get historical data for a stock\"\"\"
        stock = self.get_object()
        
        # Check if we need to update data
        if stock.last_updated < timezone.now() - timedelta(days=1):
            # Fetch new data from yfinance
            ticker = yf.Ticker(stock.symbol)
            df = ticker.history(period="1y")
            
            # Update database
            for date, row in df.iterrows():
                StockData.objects.update_or_create(
                    stock=stock,
                    date=date.date(),
                    defaults={
                        'open_price': row['Open'],
                        'high_price': row['High'],
                        'low_price': row['Low'],
                        'close_price': row['Close'],
                        'volume': row['Volume']
                    }
                )
            
            stock.last_updated = timezone.now()
            stock.save()
        
        # Return data
        data = StockData.objects.filter(stock=stock).order_by('-date')[:252]
        serializer = StockDataSerializer(data, many=True)
        return Response(serializer.data)

class AnalysisViewSet(viewsets.ViewSet):
    \"\"\"Handle technical analysis requests\"\"\"
    
    def create(self, request):
        \"\"\"Run analysis on a stock\"\"\"
        serializer = AnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        symbol = data['symbol']
        start_date = data['start_date']
        end_date = data['end_date']
        indicators = data['indicators']
        
        # Get stock
        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            return Response({'error': 'Stock not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Fetch data
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            return Response({'error': 'No data available for the selected period'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare dataframe
        df.columns = df.columns.str.lower()
        df.reset_index(inplace=True)
        
        # Calculate indicators
        ti = TechnicalIndicators(df)
        
        results = []
        
        for indicator in indicators:
            if indicator == 'sma_50':
                ti.calculate_sma(50)
                backtest = BacktestEngine(ti.df, 'sma_crossover')
            elif indicator == 'rsi':
                ti.calculate_rsi()
                backtest = BacktestEngine(ti.df, 'rsi')
            elif indicator == 'macd':
                ti.calculate_macd()
                backtest = BacktestEngine(ti.df, 'macd')
            elif indicator == 'bollinger_bands':
                ti.calculate_bollinger_bands()
                backtest = BacktestEngine(ti.df, 'bollinger_bands')
            else:
                continue
            
            # Run backtest
            metrics = backtest.run_backtest()
            
            # Save results
            result = IndicatorResult.objects.create(
                stock=stock,
                indicator_name=indicator,
                timeframe=f"{(end_date - start_date).days} days",
                success_rate=metrics['success_rate'],
                avg_return=metrics['avg_return'],
                total_signals=metrics['total_signals'],
                max_drawdown=metrics['max_drawdown'],
                sharpe_ratio=metrics['sharpe_ratio']
            )
            
            results.append(IndicatorResultSerializer(result).data)
        
        return Response({'results': results}, status=status.HTTP_201_CREATED)

class IndicatorViewSet(viewsets.ViewSet):
    \"\"\"List available indicators\"\"\"
    
    def list(self, request):
        indicators = [
            {
                'name': 'sma_50',
                'display_name': '50-Day Simple Moving Average',
                'category': 'Trend',
                'description': 'Average price over the last 50 days'
            },
            {
                'name': 'rsi',
                'display_name': 'Relative Strength Index',
                'category': 'Momentum',
                'description': 'Measures overbought/oversold conditions'
            },
            {
                'name': 'macd',
                'display_name': 'MACD',
                'category': 'Momentum',
                'description': 'Moving Average Convergence Divergence'
            },
            {
                'name': 'bollinger_bands',
                'display_name': 'Bollinger Bands',
                'category': 'Volatility',
                'description': 'Price bands based on standard deviation'
            }
        ]
        return Response(indicators)

class ResultsViewSet(viewsets.ViewSet):
    \"\"\"Get analysis results\"\"\"
    
    def retrieve(self, request, pk=None):
        \"\"\"Get results for a specific stock\"\"\"
        try:
            stock = Stock.objects.get(symbol=pk.upper())
        except Stock.DoesNotExist:
            return Response({'error': 'Stock not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        results = IndicatorResult.objects.filter(stock=stock).order_by('-date_calculated')[:20]
        serializer = IndicatorResultSerializer(results, many=True)
        return Response(serializer.data)""")
    
    # stocks/urls.py
    create_file("backend/stocks/urls.py", "# URLs are configured in api/urls.py")
    
    # stocks/admin.py
    create_file("backend/stocks/admin.py", """from django.contrib import admin
from .models import Stock, IndicatorResult, StockData

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'company_name', 'sector', 'last_updated']
    search_fields = ['symbol', 'company_name']

@admin.register(IndicatorResult)
class IndicatorResultAdmin(admin.ModelAdmin):
    list_display = ['stock', 'indicator_name', 'success_rate', 'avg_return', 'date_calculated']
    list_filter = ['indicator_name', 'date_calculated']

@admin.register(StockData)
class StockDataAdmin(admin.ModelAdmin):
    list_display = ['stock', 'date', 'close_price', 'volume']
    list_filter = ['stock', 'date']""")
    
    # indicators/__init__.py
    create_file("backend/indicators/__init__.py", "")
    
    # indicators/calculations.py
    create_file("backend/indicators/calculations.py", """import pandas as pd
import numpy as np
from ta import add_all_ta_features
from ta.utils import dropna
from ta.volatility import BollingerBands, AverageTrueRange
from ta.momentum import RSIIndicator, MACD, StochasticOscillator
from ta.trend import SMAIndicator, EMAIndicator, ADXIndicator
from ta.volume import OnBalanceVolumeIndicator

class TechnicalIndicators:
    def __init__(self, df):
        self.df = df.copy()
        
    def calculate_sma(self, period=20):
        \"\"\"Simple Moving Average\"\"\"
        indicator = SMAIndicator(close=self.df['close'], window=period)
        self.df[f'sma_{period}'] = indicator.sma_indicator()
        return self.df
    
    def calculate_ema(self, period=20):
        \"\"\"Exponential Moving Average\"\"\"
        indicator = EMAIndicator(close=self.df['close'], window=period)
        self.df[f'ema_{period}'] = indicator.ema_indicator()
        return self.df
    
    def calculate_rsi(self, period=14):
        \"\"\"Relative Strength Index\"\"\"
        indicator = RSIIndicator(close=self.df['close'], window=period)
        self.df['rsi'] = indicator.rsi()
        return self.df
    
    def calculate_macd(self):
        \"\"\"MACD\"\"\"
        indicator = MACD(close=self.df['close'])
        self.df['macd'] = indicator.macd()
        self.df['macd_signal'] = indicator.macd_signal()
        self.df['macd_diff'] = indicator.macd_diff()
        return self.df
    
    def calculate_bollinger_bands(self, period=20, std_dev=2):
        \"\"\"Bollinger Bands\"\"\"
        indicator = BollingerBands(close=self.df['close'], window=period, window_dev=std_dev)
        self.df['bb_high'] = indicator.bollinger_hband()
        self.df['bb_mid'] = indicator.bollinger_mavg()
        self.df['bb_low'] = indicator.bollinger_lband()
        return self.df
    
    def calculate_stochastic(self, period=14):
        \"\"\"Stochastic Oscillator\"\"\"
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
        \"\"\"Average True Range\"\"\"
        indicator = AverageTrueRange(
            high=self.df['high'], 
            low=self.df['low'], 
            close=self.df['close'], 
            window=period
        )
        self.df['atr'] = indicator.average_true_range()
        return self.df
    
    def calculate_obv(self):
        \"\"\"On-Balance Volume\"\"\"
        indicator = OnBalanceVolumeIndicator(close=self.df['close'], volume=self.df['volume'])
        self.df['obv'] = indicator.on_balance_volume()
        return self.df
    
    def calculate_adx(self, period=14):
        \"\"\"Average Directional Index\"\"\"
        indicator = ADXIndicator(
            high=self.df['high'], 
            low=self.df['low'], 
            close=self.df['close'], 
            window=period
        )
        self.df['adx'] = indicator.adx()
        return self.df""")
    
    # indicators/backtesting.py
    create_file("backend/indicators/backtesting.py", """import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class BacktestEngine:
    def __init__(self, df, indicator_name):
        self.df = df.copy()
        self.indicator_name = indicator_name
        self.trades = []
        
    def generate_signals(self):
        \"\"\"Generate buy/sell signals based on indicator\"\"\"
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
        \"\"\"Calculate returns for each trade\"\"\"
        self.df['returns'] = self.df['close'].pct_change()
        self.df['strategy_returns'] = self.df['returns'] * self.df['signal'].shift(1)
        self.df['cumulative_returns'] = (1 + self.df['strategy_returns']).cumprod()
        
    def calculate_metrics(self):
        \"\"\"Calculate performance metrics\"\"\"
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
        \"\"\"Run complete backtest\"\"\"
        self.generate_signals()
        self.calculate_returns()
        metrics = self.calculate_metrics()
        return metrics""")
    
    # indicators/utils.py
    create_file("backend/indicators/utils.py", "# Utility functions for indicators can be added here")
    
    # api/__init__.py
    create_file("backend/api/__init__.py", "")
    
    # api/urls.py
    create_file("backend/api/urls.py", """from django.urls import path, include
from rest_framework.routers import DefaultRouter
from stocks.views import StockViewSet, AnalysisViewSet, IndicatorViewSet, ResultsViewSet

router = DefaultRouter()
router.register(r'stocks', StockViewSet)
router.register(r'analysis', AnalysisViewSet, basename='analysis')
router.register(r'indicators', IndicatorViewSet, basename='indicators')
router.register(r'results', ResultsViewSet, basename='results')

urlpatterns = [
    path('', include(router.urls)),
]""")
    
    # Frontend files
    print("\n=== Creating Frontend Files ===\n")
    
    # package.json
    package_json = {
        "name": "technical-indicator-frontend",
        "version": "0.1.0",
        "private": True,
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "axios": "^1.4.0",
            "chart.js": "^4.3.0",
            "react-chartjs-2": "^5.2.0",
            "date-fns": "^2.30.0",
            "react-datepicker": "^4.11.0",
            "react-scripts": "5.0.1"
        },
        "scripts": {
            "start": "react-scripts start",
            "build": "react-scripts build",
            "test": "react-scripts test",
            "eject": "react-scripts eject"
        },
        "proxy": "http://localhost:8000",
        "browserslist": {
            "production": [
                ">0.2%",
                "not dead",
                "not op_mini all"
            ],
            "development": [
                "last 1 chrome version",
                "last 1 firefox version",
                "last 1 safari version"
            ]
        }
    }
    create_file("frontend/package.json", json.dumps(package_json, indent=2))
    
    # public/index.html
    create_file("frontend/public/index.html", """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="Technical Indicator Backtesting Platform"
    />
    <title>Technical Indicator Backtesting Platform</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>""")
    
    # src/index.js
    create_file("frontend/src/index.js", """import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/App.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);""")
    
    # src/App.js
    create_file("frontend/src/App.js", """import React, { useState } from 'react';
import StockSearch from './components/StockSearch';
import IndicatorSelector from './components/IndicatorSelector';
import DateRangePicker from './components/DateRangePicker';
import ResultsDashboard from './components/ResultsDashboard';
import { stockAPI } from './services/api';
import './styles/App.css';

function App() {
  const [selectedStock, setSelectedStock] = useState(null);
  const [selectedIndicators, setSelectedIndicators] = useState([]);
  const [dateRange, setDateRange] = useState({
    startDate: new Date(new Date().setMonth(new Date().getMonth() - 6)),
    endDate: new Date()
  });
  const [analysisResults, setAnalysisResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleRunAnalysis = async () => {
    if (!selectedStock || selectedIndicators.length === 0) {
      alert('Please select a stock and at least one indicator');
      return;
    }

    setLoading(true);
    try {
      const response = await stockAPI.runAnalysis({
        symbol: selectedStock.symbol,
        start_date: dateRange.startDate.toISOString().split('T')[0],
        end_date: dateRange.endDate.toISOString().split('T')[0],
        indicators: selectedIndicators
      });
      
      setAnalysisResults(response.data.results);
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Error running analysis. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>Technical Indicator Backtesting Platform</h1>
        <p className="disclaimer">
          ⚠️ Educational purposes only. Past performance does not guarantee future results.
        </p>
      </header>

      <main className="app-main">
        <div className="config-section">
          <div className="config-panel">
            <h2>Configuration</h2>
            
            <StockSearch 
              onSelectStock={setSelectedStock}
              selectedStock={selectedStock}
            />
            
            <DateRangePicker
              dateRange={dateRange}
              onDateRangeChange={setDateRange}
            />
            
            <IndicatorSelector
              selectedIndicators={selectedIndicators}
              onIndicatorChange={setSelectedIndicators}
            />
            
            <button 
              className="analyze-button"
              onClick={handleRunAnalysis}
              disabled={loading || !selectedStock || selectedIndicators.length === 0}
            >
              {loading ? 'Analyzing...' : 'Run Analysis'}
            </button>
          </div>
        </div>

        <div className="results-section">
          {analysisResults && (
            <ResultsDashboard
              results={analysisResults}
              stock={selectedStock}
            />
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>© 2024 Technical Indicator Platform | Not Financial Advice</p>
      </footer>
    </div>
  );
}

export default App;""")
    
    # src/services/api.js
    create_file("frontend/src/services/api.js", """import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const stockAPI = {
  searchStock: (query) => api.get(`/stocks/search/?q=${query}`),
  getStockData: (symbol) => api.get(`/stocks/${symbol}/data/`),
  getIndicators: () => api.get('/indicators/'),
  runAnalysis: (data) => api.post('/analysis/', data),
  getResults: (symbol) => api.get(`/results/${symbol}/`),
};

export default api;""")
    
    # src/components/StockSearch.js
    create_file("frontend/src/components/StockSearch.js", """import React, { useState } from 'react';
import { stockAPI } from '../services/api';

const StockSearch = ({ onSelectStock, selectedStock }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    try {
      const response = await stockAPI.searchStock(searchQuery);
      onSelectStock(response.data);
      setSearchQuery('');
    } catch (error) {
      alert('Stock not found. Please try another symbol.');
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="stock-search">
      <h3>Select Stock</h3>
      <form onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Enter stock symbol (e.g., AAPL)"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value.toUpperCase())}
          disabled={searching}
        />
        <button type="submit" disabled={searching}>
          {searching ? 'Searching...' : 'Search'}
        </button>
      </form>
      
      {selectedStock && (
        <div className="selected-stock">
          <h4>{selectedStock.symbol}</h4>
          <p>{selectedStock.company_name}</p>
          <p className="sector">{selectedStock.sector}</p>
        </div>
      )}
    </div>
  );
};

export default StockSearch;""")
    
    # src/components/IndicatorSelector.js
    create_file("frontend/src/components/IndicatorSelector.js", """import React, { useState, useEffect } from 'react';
import { stockAPI } from '../services/api';

const IndicatorSelector = ({ selectedIndicators, onIndicatorChange }) => {
  const [indicators, setIndicators] = useState([]);

  useEffect(() => {
    fetchIndicators();
  }, []);

  const fetchIndicators = async () => {
    try {
      const response = await stockAPI.getIndicators();
      setIndicators(response.data);
    } catch (error) {
      console.error('Error fetching indicators:', error);
    }
  };

  const handleIndicatorToggle = (indicatorName) => {
    if (selectedIndicators.includes(indicatorName)) {
      onIndicatorChange(selectedIndicators.filter(ind => ind !== indicatorName));
    } else {
      onIndicatorChange([...selectedIndicators, indicatorName]);
    }
  };

  return (
    <div className="indicator-selector">
      <h3>Select Indicators</h3>
      <div className="indicator-grid">
        {indicators.map((indicator) => (
          <div key={indicator.name} className="indicator-item">
            <label>
              <input
                type="checkbox"
                checked={selectedIndicators.includes(indicator.name)}
                onChange={() => handleIndicatorToggle(indicator.name)}
              />
              <div className="indicator-info">
                <span className="indicator-name">{indicator.display_name}</span>
                <span className="indicator-category">{indicator.category}</span>
                <span className="indicator-description">{indicator.description}</span>
              </div>
            </label>
          </div>
        ))}
      </div>
    </div>
  );
};

export default IndicatorSelector;""")
    
    # src/components/DateRangePicker.js
    create_file("frontend/src/components/DateRangePicker.js", """import React from 'react';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";

const DateRangePicker = ({ dateRange, onDateRangeChange }) => {
  const handleStartDateChange = (date) => {
    onDateRangeChange({
      ...dateRange,
      startDate: date
    });
  };

  const handleEndDateChange = (date) => {
    onDateRangeChange({
      ...dateRange,
      endDate: date
    });
  };

  const setPresetRange = (months) => {
    const end = new Date();
    const start = new Date();
    start.setMonth(start.getMonth() - months);
    
    onDateRangeChange({
      startDate: start,
      endDate: end
    });
  };

  return (
    <div className="date-range-picker">
      <h3>Select Date Range</h3>
      
      <div className="preset-buttons">
        <button onClick={() => setPresetRange(1)}>1 Month</button>
        <button onClick={() => setPresetRange(3)}>3 Months</button>
        <button onClick={() => setPresetRange(6)}>6 Months</button>
        <button onClick={() => setPresetRange(12)}>1 Year</button>
      </div>
      
      <div className="date-inputs">
        <div>
          <label>Start Date</label>
          <DatePicker
            selected={dateRange.startDate}
            onChange={handleStartDateChange}
            maxDate={dateRange.endDate}
          />
        </div>
        <div>
          <label>End Date</label>
          <DatePicker
            selected={dateRange.endDate}
            onChange={handleEndDateChange}
            minDate={dateRange.startDate}
            maxDate={new Date()}
          />
        </div>
      </div>
    </div>
  );
};

export default DateRangePicker;""")
    
    # src/components/ResultsDashboard.js
    create_file("frontend/src/components/ResultsDashboard.js", """import React from 'react';
import ComparisonTable from './ComparisonTable';
import ChartContainer from './ChartContainer';

const ResultsDashboard = ({ results, stock }) => {
  return (
    <div className="results-dashboard">
      <h2>Analysis Results for {stock.symbol}</h2>
      
      <div className="results-summary">
        <div className="summary-cards">
          {results.map((result) => (
            <div key={result.id} className="summary-card">
              <h3>{result.indicator_name}</h3>
              <div className="metric">
                <span className="label">Success Rate</span>
                <span className={`value ${result.success_rate > 50 ? 'positive' : 'negative'}`}>
                  {result.success_rate.toFixed(2)}%
                </span>
              </div>
              <div className="metric">
                <span className="label">Avg Return</span>
                <span className={`value ${result.avg_return > 0 ? 'positive' : 'negative'}`}>
                  {result.avg_return.toFixed(2)}%
                </span>
              </div>
              <div className="metric">
                <span className="label">Total Signals</span>
                <span className="value">{result.total_signals}</span>
              </div>
              <div className="metric">
                <span className="label">Max Drawdown</span>
                <span className="value negative">{result.max_drawdown.toFixed(2)}%</span>
              </div>
              <div className="metric">
                <span className="label">Sharpe Ratio</span>
                <span className="value">{result.sharpe_ratio.toFixed(2)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <ComparisonTable results={results} />
      
      <ChartContainer stock={stock} results={results} />
    </div>
  );
};

export default ResultsDashboard;""")
    
    # src/components/ComparisonTable.js
    create_file("frontend/src/components/ComparisonTable.js", """import React, { useState } from 'react';

const ComparisonTable = ({ results }) => {
  const [sortBy, setSortBy] = useState('success_rate');
  const [sortOrder, setSortOrder] = useState('desc');

  const sortedResults = [...results].sort((a, b) => {
    const aValue = a[sortBy];
    const bValue = b[sortBy];
    
    if (sortOrder === 'desc') {
      return bValue - aValue;
    } else {
      return aValue - bValue;
    }
  });

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  return (
    <div className="comparison-table">
      <h3>Indicator Performance Ranking</h3>
      <table>
        <thead>
          <tr>
            <th>Indicator</th>
            <th onClick={() => handleSort('success_rate')} className="sortable">
              Success Rate {sortBy === 'success_rate' && (sortOrder === 'desc' ? '↓' : '↑')}
            </th>
            <th onClick={() => handleSort('avg_return')} className="sortable">
              Avg Return {sortBy === 'avg_return' && (sortOrder === 'desc' ? '↓' : '↑')}
            </th>
            <th onClick={() => handleSort('total_signals')} className="sortable">
              Signals {sortBy === 'total_signals' && (sortOrder === 'desc' ? '↓' : '↑')}
            </th>
            <th onClick={() => handleSort('sharpe_ratio')} className="sortable">
              Sharpe Ratio {sortBy === 'sharpe_ratio' && (sortOrder === 'desc' ? '↓' : '↑')}
            </th>
            <th onClick={() => handleSort('max_drawdown')} className="sortable">
              Max Drawdown {sortBy === 'max_drawdown' && (sortOrder === 'desc' ? '↓' : '↑')}
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedResults.map((result) => (
            <tr key={result.id}>
              <td>{result.indicator_name}</td>
              <td className={result.success_rate > 50 ? 'positive' : 'negative'}>
                {result.success_rate.toFixed(2)}%
              </td>
              <td className={result.avg_return > 0 ? 'positive' : 'negative'}>
                {result.avg_return.toFixed(2)}%
              </td>
              <td>{result.total_signals}</td>
              <td>{result.sharpe_ratio.toFixed(2)}</td>
              <td className="negative">{result.max_drawdown.toFixed(2)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ComparisonTable;""")
    
    # src/components/ChartContainer.js
    create_file("frontend/src/components/ChartContainer.js", """import React, { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import { stockAPI } from '../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const ChartContainer = ({ stock, results }) => {
  const [priceData, setPriceData] = useState(null);
  const [chartType, setChartType] = useState('performance');

  useEffect(() => {
    if (stock) {
      fetchPriceData();
    }
  }, [stock]);

  const fetchPriceData = async () => {
    try {
      const response = await stockAPI.getStockData(stock.id);
      setPriceData(response.data);
    } catch (error) {
      console.error('Error fetching price data:', error);
    }
  };

  const getPriceChartData = () => {
    if (!priceData) return null;

    return {
      labels: priceData.map(d => new Date(d.date).toLocaleDateString()),
      datasets: [
        {
          label: 'Close Price',
          data: priceData.map(d => d.close_price),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.1)',
          tension: 0.1
        }
      ]
    };
  };

  const getPerformanceChartData = () => {
    return {
      labels: results.map(r => r.indicator_name),
      datasets: [
        {
          label: 'Success Rate (%)',
          data: results.map(r => r.success_rate),
          backgroundColor: results.map(r => 
            r.success_rate > 50 ? 'rgba(75, 192, 75, 0.8)' : 'rgba(192, 75, 75, 0.8)'
          ),
        }
      ]
    };
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: chartType === 'price' ? `${stock.symbol} Price History` : 'Indicator Performance Comparison'
      }
    },
    scales: {
      y: {
        beginAtZero: chartType !== 'price'
      }
    }
  };

  return (
    <div className="chart-container">
      <div className="chart-controls">
        <button 
          className={chartType === 'performance' ? 'active' : ''}
          onClick={() => setChartType('performance')}
        >
          Performance Comparison
        </button>
        <button 
          className={chartType === 'price' ? 'active' : ''}
          onClick={() => setChartType('price')}
        >
          Price History
        </button>
      </div>

      <div className="chart-wrapper">
        {chartType === 'price' && priceData ? (
          <Line data={getPriceChartData()} options={chartOptions} />
        ) : (
          <Bar data={getPerformanceChartData()} options={chartOptions} />
        )}
      </div>
    </div>
  );
};

export default ChartContainer;""")
    
    # src/components/EducationalModal.js
    create_file("frontend/src/components/EducationalModal.js", """import React from 'react';

const EducationalModal = ({ isOpen, onClose, indicator }) => {
  if (!isOpen || !indicator) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h2>{indicator.display_name}</h2>
        <p className="indicator-category">{indicator.category}</p>
        <p>{indicator.description}</p>
        <div className="modal-section">
          <h3>How it works</h3>
          <p>{indicator.explanation}</p>
        </div>
        <div className="modal-section">
          <h3>Formula</h3>
          <code>{indicator.formula}</code>
        </div>
        <div className="modal-disclaimer">
          <strong>Remember:</strong> No indicator is perfect. Always use multiple indicators 
          and consider market conditions before making trading decisions.
        </div>
      </div>
    </div>
  );
};

export default EducationalModal;""")
    
    # src/styles/App.css
    create_file("frontend/src/styles/App.css", """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f5f5;
}

.App {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Header */
.app-header {
  background-color: #1a1a2e;
  color: white;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.app-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.disclaimer {
  background-color: #f39c12;
  color: #000;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  display: inline-block;
  margin-top: 1rem;
  font-weight: 500;
}

/* Main Layout */
.app-main {
  flex: 1;
  display: flex;
  gap: 2rem;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.config-section {
  flex: 0 0 350px;
}

.results-section {
  flex: 1;
}

/* Configuration Panel */
.config-panel {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.config-panel h2 {
  margin-bottom: 1.5rem;
  color: #1a1a2e;
}

/* Stock Search */
.stock-search {
  margin-bottom: 2rem;
}

.stock-search h3 {
  margin-bottom: 1rem;
  color: #333;
}

.stock-search form {
  display: flex;
  gap: 0.5rem;
}

.stock-search input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  text-transform: uppercase;
}

.stock-search button {
  padding: 0.75rem 1.5rem;
  background-color: #0f3460;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.stock-search button:hover:not(:disabled) {
  background-color: #16213e;
}

.stock-search button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.selected-stock {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f0f0f0;
  border-radius: 4px;
}

.selected-stock h4 {
  font-size: 1.25rem;
  margin-bottom: 0.25rem;
  color: #0f3460;
}

.selected-stock .sector {
  color: #666;
  font-size: 0.9rem;
}

/* Date Range Picker */
.date-range-picker {
  margin-bottom: 2rem;
}

.date-range-picker h3 {
  margin-bottom: 1rem;
  color: #333;
}

.preset-buttons {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.preset-buttons button {
  flex: 1;
  padding: 0.5rem;
  background-color: #e0e0e0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.preset-buttons button:hover {
  background-color: #d0d0d0;
}

.date-inputs {
  display: flex;
  gap: 1rem;
}

.date-inputs > div {
  flex: 1;
}

.date-inputs label {
  display: block;
  margin-bottom: 0.25rem;
  color: #666;
  font-size: 0.9rem;
}

.date-inputs input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

/* Indicator Selector */
.indicator-selector {
  margin-bottom: 2rem;
}

.indicator-selector h3 {
  margin-bottom: 1rem;
  color: #333;
}

.indicator-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.indicator-item label {
  display: flex;
  align-items: flex-start;
  cursor: pointer;
  padding: 0.75rem;
  background-color: #f8f8f8;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.indicator-item label:hover {
  background-color: #f0f0f0;
}

.indicator-item input[type="checkbox"] {
  margin-right: 0.75rem;
  margin-top: 0.25rem;
}

.indicator-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.indicator-name {
  font-weight: 500;
  color: #333;
}

.indicator-category {
  font-size: 0.8rem;
  color: #666;
  background-color: #e0e0e0;
  padding: 0.2rem 0.5rem;
  border-radius: 3px;
  align-self: flex-start;
}

.indicator-description {
  font-size: 0.85rem;
  color: #666;
}

/* Analyze Button */
.analyze-button {
  width: 100%;
  padding: 1rem;
  background-color: #e94560;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1.1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.analyze-button:hover:not(:disabled) {
  background-color: #d63550;
}

.analyze-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* Results Dashboard */
.results-dashboard {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.results-dashboard h2 {
  margin-bottom: 2rem;
  color: #1a1a2e;
}

/* Summary Cards */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.summary-card {
  background-color: #f8f8f8;
  border-radius: 8px;
  padding: 1.5rem;
  border: 1px solid #e0e0e0;
}

.summary-card h3 {
  margin-bottom: 1rem;
  color: #0f3460;
  font-size: 1.1rem;
}

.metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.metric .label {
  color: #666;
  font-size: 0.9rem;
}

.metric .value {
  font-weight: 600;
  font-size: 1rem;
}

.metric .value.positive {
  color: #27ae60;
}

.metric .value.negative {
  color: #e74c3c;
}

/* Comparison Table */
.comparison-table {
  margin-bottom: 3rem;
}

.comparison-table h3 {
  margin-bottom: 1rem;
  color: #333;
}

.comparison-table table {
  width: 100%;
  border-collapse: collapse;
  background-color: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.comparison-table th {
  background-color: #f5f5f5;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #ddd;
}

.comparison-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.comparison-table th.sortable:hover {
  background-color: #e8e8e8;
}

.comparison-table td {
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.comparison-table tr:hover {
  background-color: #f8f8f8;
}

.comparison-table .positive {
  color: #27ae60;
  font-weight: 500;
}

.comparison-table .negative {
  color: #e74c3c;
  font-weight: 500;
}

/* Chart Container */
.chart-container {
  margin-top: 2rem;
}

.chart-controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.chart-controls button {
  padding: 0.75rem 1.5rem;
  background-color: #e0e0e0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.chart-controls button:hover {
  background-color: #d0d0d0;
}

.chart-controls button.active {
  background-color: #0f3460;
  color: white;
}

.chart-wrapper {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* Footer */
.app-footer {
  background-color: #1a1a2e;
  color: white;
  text-align: center;
  padding: 1.5rem;
  margin-top: auto;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .app-main {
    flex-direction: column;
  }
  
  .config-section {
    flex: 1;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .app-header h1 {
    font-size: 1.75rem;
  }
  
  .date-inputs {
    flex-direction: column;
  }
  
  .preset-buttons {
    flex-wrap: wrap;
  }
  
  .comparison-table {
    overflow-x: auto;
  }
  
  .comparison-table table {
    min-width: 600px;
  }
}

/* Loading States */
.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.loading::after {
  content: "";
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #0f3460;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error States */
.error {
  background-color: #fee;
  color: #c33;
  padding: 1rem;
  border-radius: 4px;
  margin: 1rem 0;
  border: 1px solid #fcc;
}

/* Success States */
.success {
  background-color: #efe;
  color: #3c3;
  padding: 1rem;
  border-radius: 4px;
  margin: 1rem 0;
  border: 1px solid #cfc;
}""")
    
    # Create README
    create_file("README.md", """# Technical Indicator Backtesting Platform

## Overview
A web application that analyzes the historical performance of technical indicators for stocks.

## Setup Instructions

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd technical-indicator-platform/backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   venv\\Scripts\\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py makemigrations stocks
   python manage.py migrate
   ```

5. Create superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. Run the server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd ../frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## Usage

1. Backend API: http://localhost:8000/api/
2. Frontend: http://localhost:3000/
3. Admin: http://localhost:8000/admin/ (if superuser created)

## Features

- Stock search with Yahoo Finance integration
- Technical indicators: SMA, RSI, MACD, Bollinger Bands
- Backtesting with performance metrics
- Interactive charts and comparison tables
- Responsive design

## Important Note

This is for educational purposes only. Past performance does not guarantee future results.""")
    
    print("\n=== Project setup complete! ===")
    print(f"\nProject created in: {os.path.abspath('.')}")
    print("\nNext steps:")
    print("1. Navigate to the backend folder and follow setup instructions")
    print("2. Navigate to the frontend folder and follow setup instructions")
    print("3. Access the application at http://localhost:3000")
    
if __name__ == "__main__":
    print("Technical Indicator Platform - Automated Setup")
    print("=" * 50)
    setup_project()
