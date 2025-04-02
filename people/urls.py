from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'employees-positions', PositionViewSet)
router.register(r'suppliers', SupplierViewSet, basename='suppliers-info')
router.register(r'clients-info', ClientViewSet, basename='clients-info')

urlpatterns = [
    path('', include(router.urls)),
]
