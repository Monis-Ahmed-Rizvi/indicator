from django.urls import path, include
from rest_framework.routers import DefaultRouter
from stocks.views import StockViewSet, AnalysisViewSet, IndicatorViewSet, ResultsViewSet

router = DefaultRouter()
router.register(r'stocks', StockViewSet)
router.register(r'analysis', AnalysisViewSet, basename='analysis')
router.register(r'indicators', IndicatorViewSet, basename='indicators')
router.register(r'results', ResultsViewSet, basename='results')

urlpatterns = [
    path('', include(router.urls)),
]