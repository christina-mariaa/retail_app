from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, PositionViewSet


router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'employees-positions', PositionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
