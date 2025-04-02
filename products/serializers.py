from rest_framework import serializers
from .models import *

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(), 
        allow_null=True, required=False)
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        write_only=True,
        required=True
    )
    current_price = serializers.SerializerMethodField(read_only=True)
    category_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['code', 'name', 'brand', 'image', 'category', 'price', 'current_price', 'category_name']

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

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
