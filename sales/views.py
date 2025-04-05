from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view
from django.utils.dateparse import parse_date
from datetime import datetime, time
from .models import Order
from .serializers import *

class OrderProductViewSet(viewsets.ModelViewSet):
    queryset = OrderProduct.objects.all()
    serializer_class = OrderProductSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['GET'])
def sales_by_period(request):
    """Возвращает список продаж за указанный период"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date or not end_date:
        return Response({"error": "Укажите start_date и end_date"}, status=status.HTTP_400_BAD_REQUEST)

    start_date = parse_date(start_date)
    end_date = parse_date(end_date)

    if not start_date or not end_date:
        return Response({"error": "Неверный формат дат"}, status=status.HTTP_400_BAD_REQUEST)
    
    start_dt = datetime.combine(start_date, time.min)
    end_dt = datetime.combine(end_date, time.max)

    sales = Sale.objects.filter(date_of_sale__range=(start_dt, end_dt))
    serializer = SaleSerializer(sales, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)