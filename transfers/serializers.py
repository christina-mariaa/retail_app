from rest_framework import serializers
from .models import Transfer, TransferItem
from locations.models import Stock, Location
from products.models import Product
from locations.serializers import LocationSerializer
from products.serializers import ProductSerializer  

class TransferItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Вложенный сериализатор для продукта
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = TransferItem
        fields = ["product", "product_id", "quantity", "initial_quantity", "final_quantity"]  # Включаем все поля

class TransferSerializer(serializers.ModelSerializer):
    from_location = LocationSerializer(read_only=True)  # Вложенный сериализатор для from_location
    from_location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source="from_location", write_only=True
    )
    
    to_location = LocationSerializer(read_only=True)  # Вложенный сериализатор для to_location
    to_location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source="to_location", write_only=True
    )

    items = TransferItemSerializer(many=True)  # Сериализатор для товаров в перемещении

    class Meta:
        model = Transfer
        fields = [
            "id", "from_location", "from_location_id", "to_location", "to_location_id", 
            "created_at", "items"
        ]
        read_only_fields = ["created_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        from_location = validated_data["from_location"]

        # Проверка остатков
        for item in items_data:
            stock = Stock.objects.filter(
                product=item["product"], location=from_location
            ).first()
            if not stock or stock.quantity < item["quantity"]:
                raise serializers.ValidationError(
                    f"Недостаточно товара {item['product'].name} на складе {from_location}"
                )

        # Создаём перемещение
        transfer = Transfer.objects.create(**validated_data)

        # Создаём элементы трансфера и обновляем остатки
        for item in items_data:
            TransferItem.objects.create(transfer=transfer, **item)

            stock_from = Stock.objects.get(product=item["product"], location=from_location)
            stock_from.quantity -= item["quantity"]
            stock_from.save()

            stock_to, _ = Stock.objects.get_or_create(
                product=item["product"], location=validated_data["to_location"], defaults={"quantity": 0}
            )
            stock_to.quantity += item["quantity"]
            stock_to.save()

        return transfer