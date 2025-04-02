from rest_framework import serializers
from .models import Position, Employee, CounterAgent
from locations.serializers import LocationSerializer


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name']


class EmployeeSerializer(serializers.ModelSerializer):
    position = PositionSerializer()
    location = LocationSerializer()

    class Meta:
        model = Employee
        fields = ['id', 'name', 'surname', 'middle_name', 'position', 'location']
