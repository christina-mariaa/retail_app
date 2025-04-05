from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'locations', LocationViewSet)
router.register(r'product-leftovers', StockViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
