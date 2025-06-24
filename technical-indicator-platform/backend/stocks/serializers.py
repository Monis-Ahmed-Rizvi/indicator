from rest_framework import serializers
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
    )