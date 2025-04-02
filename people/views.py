from rest_framework import viewsets
from .models import *
from .serializers import *


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer


class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = CounterAgentSerializer
    queryset = CounterAgent.objects.filter(is_supplier=False)

class SupplierViewSet(viewsets.ModelViewSet):
    serializer_class = CounterAgentSerializer
    queryset = CounterAgent.objects.filter(is_supplier=True)