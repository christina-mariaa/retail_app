from django.db import models
from locations.models import Location
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

    def __str__(self):
        return f"{self.quantity} x {self.product} (Трансфер {self.transfer.id})"