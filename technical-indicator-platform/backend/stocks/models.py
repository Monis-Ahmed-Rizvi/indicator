from django.db import models
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
        ordering = ['-date']