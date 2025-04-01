from django.db import models


class ProductCategory(models.Model):
    name = models.CharField(max_length=50)


class Product(models.Model):
    code = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    category = models.ForeignKey('ProductCategory', on_delete=models.SET_NULL, blank=True, null=True, related_name='products')

    @property
    def current_price(self):
        """Возвращает текущую активную цену (последнюю по дате начала)"""
        latest_price = self.price_history.filter(end_date__isnull=True).order_by('-start_date').first()
        return latest_price.price if latest_price else None


class PriceHistory(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['product', '-start_date']),
        ]

    def save(self, *args, **kwargs):
        # При создании новой цены закрываем предыдущую активную цену
        if not self.pk:  # Только для новых записей
            previous_active = PriceHistory.objects.filter(
                product=self.product,
                end_date__isnull=True
            ).exclude(pk=self.pk).first()
            
            if previous_active:
                previous_active.end_date = self.start_date
                previous_active.save()
        
        super().save(*args, **kwargs)
