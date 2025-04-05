from django.db import models
from locations.models import Location, Stock
from products.models import Product

class Transfer(models.Model):
    from_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="transfers_start")
    to_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="transfers_end")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Трансфер {self.id} из {self.from_location} в {self.to_location}"

class TransferItem(models.Model):
    transfer = models.ForeignKey(Transfer, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    initial_quantity = models.PositiveIntegerField(default=0)  # Начальный остаток
    final_quantity = models.PositiveIntegerField(default=0)    # Конечный остаток

    def save(self, *args, **kwargs):
        # При сохранении обновляем начальный и конечный остаток
        if not self.initial_quantity:
            stock_from = Stock.objects.filter(product=self.product, location=self.transfer.from_location).first()
            self.initial_quantity = stock_from.quantity if stock_from else 0

        stock_to = Stock.objects.filter(product=self.product, location=self.transfer.to_location).first()
        self.final_quantity = stock_to.quantity + self.quantity if stock_to else self.quantity

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product} (Трансфер {self.transfer.id})"