from django.db import models
from locations.models import Location

class CounterAgent(models.Model):
    code = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    contact_info = models.TextField()
    is_supplier = models.BooleanField(default=False)
    personal_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return self.name
    
class Position(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Employee(models.Model):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.surname} {self.name} {self.middle_name}"