from rest_framework import serializers
from django.db import transaction
from decimal import Decimal
from django.core.exceptions import ValidationError
from locations.serializers import LocationSerializer
from locations.models import Location
from people.serializers import CounterAgentSerializer, EmployeeSerializer
from people.models import CounterAgent, Employee
from products.serializers import ProductSerializer
from .models import Order, OrderProduct
from locations.models import Stock
from products.models import Product

class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        write_only=True
    )

    class Meta:
        model = OrderProduct
        fields = ['product', 'product_id', 'amount']


class OrderSerializer(serializers.ModelSerializer):
    store = LocationSerializer(read_only=True)  # Вложенный магазин
    store_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source="store",
        write_only=True
    )

    client = CounterAgentSerializer(read_only=True)  # Вложенный клиент
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=CounterAgent.objects.all(),
        source="client",
        write_only=True
    )

    delivery_driver = EmployeeSerializer(read_only=True)  # Вложенный водитель
    delivery_driver_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source="delivery_driver",
        write_only=True,
        allow_null=True,
        required=False
    )

    order_picker = EmployeeSerializer(read_only=True)  # Вложенный сборщик
    order_picker_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source="order_picker",
        write_only=True,
        allow_null=True,
        required=False
    )
    # Вложенный список товаров в заказе
    order_items = OrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'store', 'client', 'delivery_address', 'delivery_date', 
            'comment', 'state', 'total_price', 'delivery_driver', 'order_picker',
            'order_items', 'order_picker_id', 'delivery_driver_id', 'client_id', 'store_id'
        ]
        read_only_fields = ['total_price']

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')  # Извлекаем вложенные товары
        total_price = Decimal('0.00')

        with transaction.atomic():
            # Сначала вычисляем общую сумму, а затем создаем заказ с этим значением
            for item_data in order_items_data:
                product = item_data['product']
                amount = item_data['amount']

                # Проверяем наличие записи запаса для продукта в данном магазине
                try:
                    stock_record = Stock.objects.get(product=product, location=validated_data['store'])
                except Stock.DoesNotExist:
                    raise ValidationError(
                        f"Запись остатка для товара {product.name} не найдена в магазине {validated_data['store'].code}"
                    )

                # Проверка наличия нужного количества товара
                if stock_record.quantity < amount:
                    raise ValidationError(
                        f"Недостаточно товара {product.name}. Доступно: {stock_record.quantity}, требуется: {amount}"
                    )

                # Списание товара из запаса
                stock_record.quantity -= amount
                stock_record.save()

                # Получаем актуальную цену товара
                current_price_record = product.price_history.filter(end_date__isnull=True).order_by('-start_date').first()
                if not current_price_record:
                    raise ValidationError(f"Не найдена актуальная цена для товара {product.name}")
                price = current_price_record.price

                # Расчет итоговой суммы
                total_price += price * amount

            # Создаем заказ с рассчитанной суммой
            order = Order.objects.create(
                **validated_data,
                total_price=total_price
            )

            # Создаем записи в OrderProduct
            for item_data in order_items_data:
                product = item_data['product']
                amount = item_data['amount']

                # Создание записи OrderProduct
                OrderProduct.objects.create(
                    product=product,
                    order=order,
                    amount=amount,
                    price_for_an_item=current_price_record
                )

        return order