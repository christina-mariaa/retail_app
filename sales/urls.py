from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'sales', SaleViewSet)
router.register(r'order-products', OrderProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('sales-by-period/', sales_by_period, name='sales-by-period'),
]