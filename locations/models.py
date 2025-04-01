from django.db import models


class Location(models.Model):
    code = models.CharField(max_length=50, primary_key=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    is_store = models.BooleanField()
    is_main = models.BooleanField(default=False)
