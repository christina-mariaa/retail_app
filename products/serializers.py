from rest_framework import serializers
from .models import Product, ProductCategory, PriceHistory
from django.utils import timezone


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all(), allow_null=True, required=False)
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        write_only=True,
        required=True
    )
    current_price = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['code', 'name', 'brand', 'image', 'category', 'price', 'current_price']

    def create(self, validated_data):
        price = validated_data.pop('price')
        product = super().create(validated_data)
        
        PriceHistory.objects.create(
            product=product,
            price=price,
            start_date=timezone.now().date()
        )
        return product
    
    def update(self, instance, validated_data):
        new_price = validated_data.pop('price')
        
        # Создаём новую запись в истории только если цена изменилась
        if new_price != instance.current_price:
            PriceHistory.objects.create(
                product=instance,
                price=new_price,
                start_date=timezone.now().date()
            )
        return super().update(instance, validated_data)
    
    def get_current_price(self, obj):
        return obj.current_price


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name']
