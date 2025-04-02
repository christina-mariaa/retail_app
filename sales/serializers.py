from rest_framework import serializers
from django.db import transaction
from decimal import Decimal
from django.core.exceptions import ValidationError
from .models import Order, OrderProduct
from locations.models import Stock
from products.models import Product

class OrderProductSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderProduct
        fields = ['product', 'amount']


class OrderSerializer(serializers.ModelSerializer):
    # Вложенный список товаров в заказе
    order_items = OrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'store', 'client', 'delivery_address', 'delivery_date', 
            'comment', 'state', 'total_price', 'delivery_driver', 'order_picker',
            'order_items'
        ]
        read_only_fields = ['total_price', 'state']

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