from django.db import models
from locations.models import Location
from people.models import CounterAgent, Employee
from products.models import Product, PriceHistory


class Order(models.Model):
    STATE_CHOICES = [
        ('new', 'Новый'),
        ('packed', 'Собран'),
        ('delivered', 'Доставлен'),
    ]

    store = models.ForeignKey(Location, on_delete=models.CASCADE) 
    client = models.ForeignKey(CounterAgent, on_delete=models.SET_NULL, null=True, blank=True, related_name='clients')
    delivery_address = models.TextField()
    ordering_date  = models.DateTimeField(auto_now=True)
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
    

class Sale(models.Model):
    store = models.ForeignKey(Location, on_delete=models.CASCADE) 
    client = models.ForeignKey(CounterAgent, on_delete=models.SET_NULL, null=True, blank=True, related_name='clients_sales')
    date_of_sale  = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='sellers')

    def __str__(self):
        return f"Продажа {self.id} - {self.date_of_sale}, {self.total_price} руб."

class SaleProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='sale_items')
    amount = models.PositiveIntegerField() 
    price_for_an_item = models.ForeignKey(PriceHistory, on_delete=models.SET_NULL, null=True, blank=True, related_name='item_sale_price')

    def __str__(self):
        return f"{self.product.name} x {self.amount} (Заказ {self.order.id})"
    
class OrderChangeHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='change_logs')
    order_product = models.ForeignKey(OrderProduct, on_delete=models.CASCADE, related_name='change_logs')
    previous_amount = models.PositiveIntegerField()
    new_amount = models.PositiveIntegerField()
    changed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_changes')
    change_time = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Изменение для Заказа {self.order.id}: {self.order_product.product.name} {self.previous_amount} -> {self.new_amount}"