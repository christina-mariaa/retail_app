from rest_framework import serializers
from django.db import transaction
from decimal import Decimal
from django.core.exceptions import ValidationError
from locations.serializers import LocationSerializer
from locations.models import Location
from people.serializers import CounterAgentSerializer, EmployeeSerializer
from people.models import CounterAgent, Employee
from products.serializers import ProductSerializer
from .models import *
from locations.models import Stock
from products.models import Product

class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        write_only=True
    )
    changed_by_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = OrderProduct
        fields = ['product', 'product_id', 'amount', 'id', 'changed_by_id'] 

    def update(self, instance, validated_data):
        old_amount = instance.amount
        changed_by_id = validated_data.pop('changed_by_id', None)
        instance = super().update(instance, validated_data)
        new_amount = instance.amount

        if old_amount != new_amount:
            request = self.context.get('request')
            comment = request.data.get('comment', '')

            changed_by = None
            if changed_by_id:
                try:
                    changed_by = Employee.objects.get(id=changed_by_id)
                except Employee.DoesNotExist:
                    print(f"Employee with id {changed_by_id} does not exist")
                    pass

            OrderChangeHistory.objects.create(
                order=instance.order,
                order_product=instance,
                previous_amount=old_amount,
                new_amount=new_amount,
                changed_by=changed_by,
                comment=comment
            )
        
        return instance


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
    
class SaleProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        write_only=True
    )

    class Meta:
        model = SaleProduct
        fields = ['product', 'product_id', 'amount']


class SaleSerializer(serializers.ModelSerializer):
    store = LocationSerializer(read_only=True)
    store_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source="store",
        write_only=True
    )

    client = CounterAgentSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=CounterAgent.objects.all(),
        source="client",
        write_only=True,
        allow_null=True,
        required=False
    )

    seller = EmployeeSerializer(read_only=True)
    seller_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source="seller",
        write_only=True,
        allow_null=True,
        required=False
    )
    
    sale_items = SaleProductSerializer(many=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'store', 'client', 'date_of_sale', 'total_price', 'seller',
            'sale_items', 'seller_id', 'client_id', 'store_id'
        ]
        read_only_fields = ['total_price', 'date_of_sale']

    def create(self, validated_data):
        sale_items_data = validated_data.pop('sale_items', [])
        total_price = Decimal('0.00')

        with transaction.atomic():
            if not validated_data.get('seller'):
                last_sale = Sale.objects.filter(store=validated_data['store']).order_by('-date_of_sale').first()
                if last_sale:
                    validated_data['seller'] = last_sale.seller
                else:
                    raise ValidationError("Необходимо указать продавца, так как в магазине нет предыдущих продаж.")

            sale = Sale.objects.create(**validated_data, total_price=total_price)

            for item_data in sale_items_data:
                product = item_data['product']
                amount = item_data['amount']
                
                try:
                    stock_record = Stock.objects.get(product=product, location=validated_data['store'])
                except Stock.DoesNotExist:
                    raise ValidationError(f"Запись остатка для товара {product.name} не найдена в магазине {validated_data['store'].code}")
                
                if stock_record.quantity < amount:
                    raise ValidationError(f"Недостаточно товара {product.name}. Доступно: {stock_record.quantity}, требуется: {amount}")
                
                stock_record.quantity -= amount
                stock_record.save()
                
                current_price_record = product.price_history.filter(end_date__isnull=True).order_by('-start_date').first()
                if not current_price_record:
                    raise ValidationError(f"Не найдена актуальная цена для товара {product.name}")
                price = current_price_record.price
                
                total_price += price * amount

                SaleProduct.objects.create(
                    product=product,
                    sale=sale,
                    amount=amount,
                    price_for_an_item=current_price_record
                )

            # Убеждаемся, что total_price не NULL
            sale.total_price = total_price or Decimal('0.00')
            sale.save(update_fields=['total_price'])

        return sale