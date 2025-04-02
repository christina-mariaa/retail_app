from rest_framework import serializers
from .models import Position, Employee, CounterAgent
from locations.models import Location
from locations.serializers import LocationSerializer


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name']


class EmployeeSerializer(serializers.ModelSerializer):
    position_data = PositionSerializer(source='position', read_only=True)
    location_data = LocationSerializer(source='location', read_only=True)

    # Для записи — только id
    position = serializers.PrimaryKeyRelatedField(queryset=Position.objects.all(), write_only=True)
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all(), write_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'name', 'surname', 'middle_name', 'position', 'location', 'position_data', 'location_data']
