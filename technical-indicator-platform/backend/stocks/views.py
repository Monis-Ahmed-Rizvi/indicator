# stocks/views.py - IMPROVED VERSION with comprehensive error handling
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
from requests.exceptions import HTTPError, RequestException
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
        """Search stocks by symbol with comprehensive error handling"""
        query = request.query_params.get('q', '')
        print(f"DEBUG: Searching for symbol: {query}")
        
        if not query:
            return Response({
                'error': 'Query parameter required',
                'suggestion': 'Please provide a stock symbol (e.g., AAPL, GOOGL, QNBK.QA)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Clean and normalize the query
        query = query.strip().upper()
        
        # First check if stock already exists in database
        try:
            stock = Stock.objects.get(symbol=query)
            print(f"DEBUG: Found existing stock: {stock.symbol}")
            serializer = StockSerializer(stock)
            return Response(serializer.data)
        except Stock.DoesNotExist:
            pass
        
        # If not in database, try to fetch from yfinance with comprehensive error handling
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"DEBUG: Attempting to fetch {query}, attempt {attempt + 1}")
                
                # Add progressive delays between attempts
                if attempt > 0:
                    delay = random.uniform(2, 5) * (attempt + 1)
                    print(f"DEBUG: Waiting {delay:.1f} seconds before retry")
                    time.sleep(delay)
                
                ticker = yf.Ticker(query)
                
                # Try to get minimal data first to check if symbol exists
                try:
                    # Test with a small period first
                    hist = ticker.history(period="5d")
                    if hist.empty:
                        print(f"DEBUG: No historical data for {query}")
                        return Response({
                            'error': f'Stock symbol "{query}" not found or may be delisted.',
                            'suggestion': 'Please verify the symbol spelling. For Qatar stocks, ensure correct format (e.g., QNBK.QA). For US stocks, try AAPL, GOOGL, TSLA.'
                        }, status=status.HTTP_404_NOT_FOUND)
                    
                    # If we get here, the symbol has data - try to get company info
                    info = {}
                    company_name = query  # Default fallback
                    sector = 'Unknown'
                    
                    try:
                        info = ticker.info
                        company_name = info.get('longName', info.get('shortName', query))
                        sector = info.get('sector', 'Unknown')
                        print(f"DEBUG: Successfully got info for {query}")
                    except Exception as e:
                        print(f"DEBUG: Could not get detailed info, using defaults: {e}")
                        # Use basic info - still create the stock record
                        pass
                    
                    # Create stock record
                    stock, created = Stock.objects.get_or_create(
                        symbol=query,
                        defaults={
                            'company_name': company_name,
                            'sector': sector
                        }
                    )
                    
                    print(f"DEBUG: Stock {'created' if created else 'found'}: {stock.symbol}")
                    serializer = StockSerializer(stock)
                    return Response(serializer.data)
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    print(f"DEBUG: Error getting stock data: {e}")
                    
                    # Handle specific yfinance errors
                    if any(keyword in error_msg for keyword in ['delisted', 'no data found', 'no price data']):
                        return Response({
                            'error': f'Stock symbol "{query}" appears to be delisted or invalid.',
                            'suggestion': 'Please check the symbol spelling. Try popular symbols like AAPL, GOOGL, TSLA, or for Qatar: QNBK.QA'
                        }, status=status.HTTP_404_NOT_FOUND)
                    
                    if 'timeout' in error_msg:
                        if attempt < max_retries - 1:
                            continue  # Retry on timeout
                        return Response({
                            'error': 'Request timed out while fetching stock data.',
                            'suggestion': 'Please try again in a moment.'
                        }, status=status.HTTP_408_REQUEST_TIMEOUT)
                    
                    # If it's the last attempt, let it bubble up
                    if attempt == max_retries - 1:
                        raise
                    continue
                    
            except HTTPError as e:
                print(f"DEBUG: HTTP Error on attempt {attempt + 1}: {e}")
                if hasattr(e, 'response') and e.response.status_code == 429:  # Too Many Requests
                    if attempt < max_retries - 1:
                        # Exponential backoff for rate limiting
                        delay = (3 ** attempt) + random.uniform(1, 3)
                        print(f"DEBUG: Rate limited, waiting {delay:.1f} seconds")
                        time.sleep(delay)
                        continue
                    else:
                        return Response({
                            'error': 'Yahoo Finance is temporarily rate limiting requests.',
                            'suggestion': 'Please wait a few minutes and try again, or try a different stock symbol.'
                        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
                else:
                    # Other HTTP errors
                    return Response({
                        'error': f'Network error occurred: {e}',
                        'suggestion': 'Please check your connection and try again.'
                    }, status=status.HTTP_502_BAD_GATEWAY)
                    
            except RequestException as e:
                print(f"DEBUG: Request error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    continue  # Retry on request errors
                return Response({
                    'error': 'Network connection error.',
                    'suggestion': 'Please check your internet connection and try again.'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
            except Exception as e:
                print(f"DEBUG: Unexpected error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    return Response({
                        'error': f'An unexpected error occurred: {str(e)}',
                        'suggestion': 'Please try a different stock symbol or contact support.'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                continue
        
        # If we get here, all retries failed
        return Response({
            'error': 'Stock not found or temporarily unavailable after multiple attempts.',
            'suggestion': 'Please try again later or use a different stock symbol.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get historical data for a stock with improved error handling"""
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
                else:
                    print(f"DEBUG: No data available for {stock.symbol}")
                
            except HTTPError as e:
                if hasattr(e, 'response') and e.response.status_code == 429:
                    print(f"DEBUG: Rate limited when fetching data for {stock.symbol}")
                    # Don't fail, just use existing data
                    pass
                else:
                    print(f"DEBUG: HTTP error updating data: {e}")
            except Exception as e:
                print(f"DEBUG: Error updating data: {e}")
        
        # Return data
        data = StockData.objects.filter(stock=stock).order_by('-date')[:252]
        if not data.exists():
            return Response({
                'error': f'No historical data available for {stock.symbol}',
                'suggestion': 'This stock may not have sufficient trading history.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StockDataSerializer(data, many=True)
        return Response(serializer.data)


class AnalysisViewSet(viewsets.ViewSet):
    """Handle technical analysis requests with improved error handling"""
    
    def create(self, request):
        """Run analysis on a stock with comprehensive error handling"""
        serializer = AnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Invalid request data',
                'details': serializer.errors,
                'suggestion': 'Please check your input parameters.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        symbol = data['symbol']
        start_date = data['start_date']
        end_date = data['end_date']
        indicators = data['indicators']
        
        # Validate date range
        if start_date >= end_date:
            return Response({
                'error': 'Invalid date range',
                'suggestion': 'Start date must be before end date.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if date range is too long
        if (end_date - start_date).days > 365 * 3:  # 3 years max
            return Response({
                'error': 'Date range too long',
                'suggestion': 'Please select a date range of 3 years or less.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get stock
        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            return Response({
                'error': f'Stock "{symbol}" not found',
                'suggestion': 'Please search for the stock first to add it to the database.'
            }, status=status.HTTP_404_NOT_FOUND)
        
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
                if hasattr(e, 'response') and e.response.status_code == 429:
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return Response({
                            'error': 'Yahoo Finance rate limit exceeded',
                            'suggestion': 'Please try again in a few minutes.'
                        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            except Exception as e:
                if attempt == max_retries - 1:
                    return Response({
                        'error': f'Error fetching data: {str(e)}',
                        'suggestion': 'Please try again later or select a different date range.'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if df is None or df.empty:
            return Response({
                'error': 'No data available for the selected period',
                'suggestion': 'Try selecting a different date range or check if the stock was trading during this period.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if we have enough data for analysis
        if len(df) < 50:  # Need at least 50 data points
            return Response({
                'error': 'Insufficient data for analysis',
                'suggestion': 'Please select a longer date range to get more reliable results.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
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
                    print(f"DEBUG: Unknown indicator: {indicator}")
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
        
        if not results:
            return Response({
                'error': 'Unable to analyze any indicators',
                'suggestion': 'Please try again with different parameters or contact support.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'results': results,
            'summary': {
                'stock': stock.symbol,
                'period': f"{start_date} to {end_date}",
                'indicators_analyzed': len(results),
                'data_points': len(df)
            }
        }, status=status.HTTP_201_CREATED)


class IndicatorViewSet(viewsets.ViewSet):
    """List available indicators with descriptions"""
    
    def list(self, request):
        indicators = [
            {
                'name': 'sma_50',
                'display_name': '50-Day Simple Moving Average',
                'category': 'Trend',
                'description': 'Average price over the last 50 days - helps identify trend direction'
            },
            {
                'name': 'rsi',
                'display_name': 'Relative Strength Index',
                'category': 'Momentum',
                'description': 'Measures overbought/oversold conditions (0-100 scale)'
            },
            {
                'name': 'macd',
                'display_name': 'MACD',
                'category': 'Momentum',
                'description': 'Moving Average Convergence Divergence - shows trend changes'
            },
            {
                'name': 'bollinger_bands',
                'display_name': 'Bollinger Bands',
                'category': 'Volatility',
                'description': 'Price bands based on standard deviation - identifies volatility'
            }
        ]
        return Response(indicators)


class ResultsViewSet(viewsets.ViewSet):
    """Get analysis results with filtering options"""
    
    def retrieve(self, request, pk=None):
        """Get results for a specific stock"""
        try:
            stock = Stock.objects.get(symbol=pk.upper())
        except Stock.DoesNotExist:
            return Response({
                'error': f'Stock "{pk.upper()}" not found',
                'suggestion': 'Please search for the stock first.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        results = IndicatorResult.objects.filter(stock=stock).order_by('-date_calculated')[:20]
        
        if not results.exists():
            return Response({
                'error': f'No analysis results found for {stock.symbol}',
                'suggestion': 'Please run an analysis first to see results.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = IndicatorResultSerializer(results, many=True)
        return Response({
            'stock': StockSerializer(stock).data,
            'results': serializer.data,
            'total_analyses': results.count()
        })
