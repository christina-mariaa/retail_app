from django.db import models
from locations.models import Location
from people.models import CounterAgent, Employee
from products.models import Product, PriceHistory


""" Не уверена какое действие делать при удалении сотрудников и товаров - 
 пока поставила setNull, но это значит - что поля будут необязательные.
  Можно поставить каскад везде """
class Order(models.Model):
    STATE_CHOICES = [
        ('new', 'Новый'),
        ('packed', 'Собран'),
        ('delivered', 'Доставлен'),
    ]

    store = models.ForeignKey(Location, on_delete=models.CASCADE) 
    client = models.ForeignKey(CounterAgent, on_delete=models.SET_NULL, null=True, blank=True, related_name='clients')
    delivery_address = models.TextField()
    delivery_date = models.DateField()
    comment = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='new')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_driver = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    order_picker = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='pickers')

    def __str__(self):
        return f"Заказ {self.id} - {self.state}"

class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    amount = models.PositiveIntegerField() 
    price_for_an_item = models.ForeignKey(PriceHistory, on_delete=models.SET_NULL, null=True, blank=True, related_name='item_price')

    def __str__(self):
        return f"{self.product.name} x {self.amount} (Заказ {self.order.id})"