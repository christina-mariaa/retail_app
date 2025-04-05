from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'product-categories', ProductCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('profitable-products/', most_profitable_products, name='profitable-products'),
    path('popular-products/', popular_products_report, name='popular-products'),
]
