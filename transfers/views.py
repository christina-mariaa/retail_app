from rest_framework import viewsets
from django.db.models import Sum, F
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Transfer
from .serializers import TransferSerializer

class TransferViewSet(viewsets.ModelViewSet):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer

# @api_view(["GET"])
# def stock_report(request):
#     stocks = Stock.objects.values("product__name", "location__code").annotate(
#         начальный_остаток=F("quantity"),
#         приход=Sum("transferitem__quantity", filter=F("transferitem__transfer__to_location")),
#         расход=Sum("transferitem__quantity", filter=F("transferitem__transfer__from_location")),
#     )

#     for stock in stocks:
#         stock["конечный_остаток"] = stock["начальный_остаток"] + (stock["приход"] or 0) - (stock["расход"] or 0)

#     return Response(stocks)