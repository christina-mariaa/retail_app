from rest_framework import serializers
from django.db import transaction
from decimal import Decimal
from django.utils import timezone
from .models import Purchase, PurchaseProduct
from products.models import Product, PriceHistory
from locations.models import Stock  # Модель запасов
from people.models import CounterAgent
from locations.models import Location

class PurchaseProductSerializer(serializers.ModelSerializer):
    product_code = serializers.CharField(write_only=True)  # Код продукта
    product_name = serializers.CharField(write_only=True)
    increase_percent = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, write_only=True)

    class Meta:
        model = PurchaseProduct
        fields = ['product', 'amount', 'price_for_an_item', 'product_code', 'increase_percent', 'product_name']
        read_only_fields = ['product']

class PurchaseSerializer(serializers.ModelSerializer):
    supplier = serializers.PrimaryKeyRelatedField(queryset=CounterAgent.objects.all())
    warehouse = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())
    purchase_products = PurchaseProductSerializer(many=True, write_only=True)

    class Meta:
        model = Purchase
        fields = ['id', 'supplier', 'warehouse', 'total_price', 'purchase_products']
        read_only_fields = ['total_price']

    def create(self, validated_data):
        purchase_products_data = validated_data.pop('purchase_products')
        total_price = Decimal('0.00')

        with transaction.atomic():
            purchase = Purchase.objects.create(**validated_data, total_price=total_price)

            for item_data in purchase_products_data:
                product_code = item_data.pop('product_code')
                product_name = item_data.pop('product_name')
                increase_percent = item_data.pop('increase_percent', None)
                price_for_an_item = item_data['price_for_an_item']
                amount = item_data['amount']

                # Ищем товар, если нет — создаем
                product, created = Product.objects.get_or_create(code=product_code, defaults={'name': product_name})

                # Считаем новую цену с учетом наценки
                new_price = price_for_an_item
                if increase_percent:
                    new_price += new_price * (Decimal(increase_percent) / Decimal('100.00'))

                if created:
                    # Если товар только что создан — создаем цену сразу
                    PriceHistory.objects.create(
                        product=product,
                        price=new_price,
                        start_date=timezone.now().date()
                    )
                else:
                    # Если товар существовал — проверим, нужно ли обновить цену
                    last_price = product.price_history.filter(end_date__isnull=True).first()
                    if last_price:
                        if last_price.price != new_price:
                            last_price.end_date = timezone.now().date()
                            last_price.save()

                            PriceHistory.objects.create(
                                product=product,
                                price=new_price,
                                start_date=timezone.now().date()
                            )
                    else:
                        # Не было активной цены — создаем
                        PriceHistory.objects.create(
                            product=product,
                            price=new_price,
                            start_date=timezone.now().date()
                        )

                # Создаем запись в PurchaseProduct
                purchase_product = PurchaseProduct.objects.create(
                    purchase=purchase,
                    product=product,
                    amount=amount,
                    price_for_an_item=price_for_an_item
                )

                total_price += price_for_an_item * amount

                # Обновляем количество товара на складе
                stock, _ = Stock.objects.get_or_create(product=product, location=validated_data['warehouse'], defaults={'quantity': 0})
                stock.quantity += amount
                stock.save()

            # Сохраняем итоговую сумму закупки
            purchase.total_price = total_price
            purchase.save(update_fields=['total_price'])

        return purchase