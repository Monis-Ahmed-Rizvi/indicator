# stocks/views.py - IMPROVED VERSION with rate limit handling
import time
import random
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from requests.exceptions import HTTPError
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
        """Search stocks by symbol with rate limit handling"""
        query = request.query_params.get('q', '')
        print(f"DEBUG: Searching for symbol: {query}")
        
        if not query:
            return Response({'error': 'Query parameter required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # First check if stock already exists in database
        try:
            stock = Stock.objects.get(symbol=query.upper())
            print(f"DEBUG: Found existing stock: {stock.symbol}")
            serializer = StockSerializer(stock)
            return Response(serializer.data)
        except Stock.DoesNotExist:
            pass
        
        # If not in database, try to fetch from yfinance with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"DEBUG: Attempt {attempt + 1} to fetch from yfinance")
                
                # Add random delay to avoid rate limiting
                if attempt > 0:
                    delay = random.uniform(1, 3) * (attempt + 1)
                    print(f"DEBUG: Waiting {delay:.1f} seconds before retry")
                    time.sleep(delay)
                
                ticker = yf.Ticker(query.upper())
                
                # Use a simpler approach - just get basic info
                try:
                    # Try to get minimal data first
                    hist = ticker.history(period="5d")
                    if hist.empty:
                        raise ValueError("No historical data available")
                    
                    # If we get here, the symbol is valid
                    info = {}
                    try:
                        info = ticker.info
                    except:
                        # If info fails, create with minimal data
                        print("DEBUG: Could not get detailed info, using minimal data")
                        pass
                    
                    stock, created = Stock.objects.get_or_create(
                        symbol=query.upper(),
                        defaults={
                            'company_name': info.get('longName', info.get('shortName', query.upper())),
                            'sector': info.get('sector', 'Unknown')
                        }
                    )
                    
                    print(f"DEBUG: Stock {'created' if created else 'updated'}: {stock.symbol}")
                    serializer = StockSerializer(stock)
                    return Response(serializer.data)
                    
                except Exception as e:
                    print(f"DEBUG: Error getting stock data: {str(e)}")
                    if attempt == max_retries - 1:
                        raise
                    continue
                    
            except HTTPError as e:
                print(f"DEBUG: HTTP Error on attempt {attempt + 1}: {e}")
                if e.response.status_code == 429:  # Too Many Requests
                    if attempt < max_retries - 1:
                        # Exponential backoff for rate limiting
                        delay = (2 ** attempt) + random.uniform(0, 1)
                        print(f"DEBUG: Rate limited, waiting {delay:.1f} seconds")
                        time.sleep(delay)
                        continue
                    else:
                        return Response({
                            'error': 'Yahoo Finance rate limit exceeded. Please try again in a few minutes.',
                            'suggestion': 'Try searching for a different stock or wait before retrying.'
                        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
                else:
                    break
            except Exception as e:
                print(f"DEBUG: Unexpected error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    return Response({
                        'error': f'Unable to fetch stock data: {str(e)}',
                        'suggestion': 'Please check the stock symbol and try again.'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'error': 'Stock not found or temporarily unavailable'}, 
                       status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get historical data for a stock with rate limit handling"""
        stock = self.get_object()
        
        # Check if we need to update data
        if stock.last_updated < timezone.now() - timedelta(days=1):
            try:
                # Add delay to prevent rate limiting
                time.sleep(random.uniform(0.5, 1.5))
                
                ticker = yf.Ticker(stock.symbol)
                df = ticker.history(period="1y")
                
                if not df.empty:
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
                    print(f"DEBUG: Updated data for {stock.symbol}")
                
            except HTTPError as e:
                if e.response.status_code == 429:
                    print(f"DEBUG: Rate limited when fetching data for {stock.symbol}")
                    # Don't fail, just use existing data
                    pass
                else:
                    print(f"DEBUG: Error updating data: {e}")
            except Exception as e:
                print(f"DEBUG: Error updating data: {e}")
        
        # Return data
        data = StockData.objects.filter(stock=stock).order_by('-date')[:252]
        serializer = StockDataSerializer(data, many=True)
        return Response(serializer.data)

# Keep the rest of your views the same...
class AnalysisViewSet(viewsets.ViewSet):
    """Handle technical analysis requests"""
    
    def create(self, request):
        """Run analysis on a stock with rate limit handling"""
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
        
        # Fetch data with retry logic
        max_retries = 3
        df = None
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = random.uniform(1, 3) * (attempt + 1)
                    time.sleep(delay)
                
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date)
                
                if not df.empty:
                    break
                    
            except HTTPError as e:
                if e.response.status_code == 429:
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return Response({
                            'error': 'Yahoo Finance rate limit exceeded. Please try again later.'
                        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            except Exception as e:
                if attempt == max_retries - 1:
                    return Response({
                        'error': f'Error fetching data: {str(e)}'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if df is None or df.empty:
            return Response({'error': 'No data available for the selected period'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare dataframe
        df.columns = df.columns.str.lower()
        df.reset_index(inplace=True)
        
        # Calculate indicators
        ti = TechnicalIndicators(df)
        results = []
        
        for indicator in indicators:
            try:
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
                
            except Exception as e:
                print(f"DEBUG: Error processing indicator {indicator}: {e}")
                continue
        
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
