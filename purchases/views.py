from rest_framework import viewsets
from .models import Purchase
from .serializers import *

class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer