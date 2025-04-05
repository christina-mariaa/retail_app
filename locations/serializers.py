from rest_framework import serializers
from products.serializers import ProductSerializer
from .models import *


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['code', 'address', 'is_store', 'is_main']


class StockSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    location = LocationSerializer(read_only=True)

    class Meta:
        model = Stock
        fields = ['product', 'location', 'quantity']