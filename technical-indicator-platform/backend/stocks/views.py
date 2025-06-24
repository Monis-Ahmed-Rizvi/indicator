from rest_framework import viewsets, status
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
        """Search stocks by symbol"""
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
        """Get historical data for a stock"""
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
    """Handle technical analysis requests"""
    
    def create(self, request):
        """Run analysis on a stock"""
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
    """List available indicators"""
    
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
    """Get analysis results"""
    
    def retrieve(self, request, pk=None):
        """Get results for a specific stock"""
        try:
            stock = Stock.objects.get(symbol=pk.upper())
        except Stock.DoesNotExist:
            return Response({'error': 'Stock not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        results = IndicatorResult.objects.filter(stock=stock).order_by('-date_calculated')[:20]
        serializer = IndicatorResultSerializer(results, many=True)
        return Response(serializer.data)