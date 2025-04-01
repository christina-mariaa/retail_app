from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductCategoryViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'product-categories', ProductCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
