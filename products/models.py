from django.db import models
from django.utils import timezone


class ProductCategory(models.Model):
    name = models.CharField(max_length=50)


class Product(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    category = models.ForeignKey('ProductCategory', on_delete=models.SET_NULL, related_name='products')


class PriceHistory(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-start_date']
