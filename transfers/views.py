from rest_framework import viewsets
from rest_framework.decorators import api_view
from django.db import transaction
from rest_framework.response import Response
from .models import *
from .serializers import TransferSerializer
from django.shortcuts import get_object_or_404
from locations.models import Stock, Location
from rest_framework import status

class TransferViewSet(viewsets.ModelViewSet):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer

@api_view(['POST'])
def distribute_stock(request):
    """Распределение товаров из основного склада по магазинам"""
    main_warehouse = get_object_or_404(Location, is_main=True)
    products = Stock.objects.filter(location=main_warehouse)

    transfer_data = []  # Для передачи пользователю
    for stock in products:
        product = stock.product
        available_qty = stock.quantity

        stores = Stock.objects.filter(product=product, location__is_store=True).order_by('-location__priority')
        for store_stock in stores:
            needed_qty = max(0, store_stock.max_qty - store_stock.quantity)
            if store_stock.quantity < store_stock.min_qty and available_qty > 0:
                transfer_qty = min(needed_qty, available_qty)
                transfer_data.append({
                    "store": {
                        "code": store_stock.location.code,
                        "address": store_stock.location.address,
                        "priority": store_stock.location.priority
                    },
                    "product": {
                        "code": product.code,
                        "name": product.name,
                        "category": product.category.name if product.category else None,
                        "brand": product.brand if product.brand else None,
                    },
                    "transfer_qty": transfer_qty
                })
                available_qty -= transfer_qty

    return Response(transfer_data, status=status.HTTP_200_OK)