from django.db import models


class Location(models.Model):
    code = models.CharField(max_length=50, primary_key=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    is_store = models.BooleanField()
    is_main = models.BooleanField(default=False)


class Stock(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    min_qty = models.IntegerField(default=0)
    max_qty = models.IntegerField(default=0)

    class Meta:
        unique_together = ('product', 'location')
