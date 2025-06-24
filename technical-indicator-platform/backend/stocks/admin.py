from django.contrib import admin
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
    list_filter = ['stock', 'date']