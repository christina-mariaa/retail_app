from django.db import models
from locations.models import Location
from people.models import CounterAgent
from products.models import Product
from django.utils import timezone

class Purchase(models.Model):
    supplier = models.ForeignKey(CounterAgent, on_delete=models.CASCADE, related_name='supplier_purchases')
    warehouse = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='warehouse_purchases')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Закупка {self.id} от {self.supplier.name}"


class PurchaseProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchase_products')
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='products')
    amount = models.PositiveIntegerField()
    price_for_an_item = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.amount} x {self.product.name} для закупки {self.purchase.id}"