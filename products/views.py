from rest_framework import viewsets
from .models import Product
from .serializers import *
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Case, When
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_date
from sales.models import SaleProduct
from purchases.models import PurchaseProduct, Purchase


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'code'

    
class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    lookup_field = 'id'


@api_view(['GET'])
def most_profitable_products(request):
    """Возвращает список товаров с максимальной прибылью за указанный период"""

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date or not end_date:
        return Response({"error": "Необходимо указать start_date и end_date"}, status=status.HTTP_400_BAD_REQUEST)

    start_date = parse_date(start_date)
    end_date = parse_date(end_date)

    if not start_date or not end_date:
        return Response({"error": "Неверный формат дат"}, status=status.HTTP_400_BAD_REQUEST)

    # Получаем все закупки за период
    purchases = Purchase.objects.filter(
        purchase_date__range=(start_date, end_date)
    )

    # Фильтруем PurchaseProduct для получения товаров с закупками за нужный период
    purchase_products = PurchaseProduct.objects.filter(
        purchase__in=purchases
    ).values('product').annotate(
        total_cost=Sum(F('amount') * F('price_for_an_item'), output_field=DecimalField()),
        total_qty=Sum('amount')
    ).annotate(
        avg_purchase_price=ExpressionWrapper(
            F('total_cost') / Case(
                When(total_qty=0, then=1),  # Избегаем деления на 0
                default=F('total_qty'),
                output_field=DecimalField()
            ),
            output_field=DecimalField()
        )
    )

    # Получаем данные по продажам
    sales_data = SaleProduct.objects.filter(
        sale__date_of_sale__range=(start_date, end_date)
    ).values('product').annotate(
        total_revenue=Sum(F('amount') * F('price_for_an_item__price'), output_field=DecimalField()),
        total_qty_sold=Sum('amount')
    )

    # Создаем словарь {product_id: средняя закупочная цена}
    purchase_cost_map = {p['product']: p['avg_purchase_price'] for p in purchase_products}

    result = []
    for sale in sales_data:
        product_id = sale['product']
        revenue = sale['total_revenue']
        quantity_sold = sale['total_qty_sold']
        avg_cost = purchase_cost_map.get(product_id, 0)  # Если закупок не было, себестоимость 0

        # Прибыль = (цена продажи - закупочная цена) * объем продаж
        profit = (revenue - (avg_cost * quantity_sold))

        result.append({
            "product": {
                "id": product_id,
                "name": Product.objects.get(pk=product_id).name
            },
            "profit": profit
        })

    # Сортируем по убыванию прибыли
    result.sort(key=lambda x: x['profit'], reverse=True)

    return Response(result, status=status.HTTP_200_OK)

@api_view(['GET'])
def popular_products_report(request):
    """Возвращает отчет по топ-10 товарам по объему продаж за указанный период"""

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date or not end_date:
        return Response({"error": "Необходимо указать start_date и end_date"}, status=status.HTTP_400_BAD_REQUEST)

    start_date = parse_date(start_date)
    end_date = parse_date(end_date)

    if not start_date or not end_date:
        return Response({"error": "Неверный формат дат"}, status=status.HTTP_400_BAD_REQUEST)

    # Получаем данные по продажам за период
    sales_data = SaleProduct.objects.filter(
        sale__date_of_sale__range=(start_date, end_date)
    ).values('product').annotate(
        total_qty_sold=Sum('amount')
    )

    # Сортируем по количеству проданных товаров
    top_products = sorted(sales_data, key=lambda x: x['total_qty_sold'], reverse=True)[:10]

    # Получаем продукты по их code
    product_map = {product.code: product for product in Product.objects.filter(code__in=[p['product'] for p in top_products])}

    result = [{
        "product": {
            "code": product_map.get(Product.objects.get(code=product['product']).code).code,
            "name": product_map.get(Product.objects.get(code=product['product']).code).name
        },
        "total_qty_sold": product['total_qty_sold']
    } for product in top_products]

    return Response(result, status=status.HTTP_200_OK)