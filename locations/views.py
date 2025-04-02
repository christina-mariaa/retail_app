from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum
from .models import *
from .serializers import *


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    lookup_field = 'code'


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

    @action(detail=False, methods=['get'])
    def get_product_stocks(self, request):
        store_code = request.query_params.get('store_code', None)
        product_code = request.query_params.get('product_code', None)
        
        queryset = Stock.objects.all()

        if store_code and product_code:
            queryset = queryset.filter(product__code=product_code, location__code=store_code)
        else:
            if store_code:
                queryset = queryset.filter(location__code=store_code)
            if product_code:
                queryset = queryset.filter(product__code=product_code)

        serializer = StockSerializer(queryset, many=True)
        return Response(serializer.data)