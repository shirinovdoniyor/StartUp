from rest_framework import serializers
from .models import WorkshopService


class WorkshopServiceSerializer(serializers.ModelSerializer):
    workshop_name = serializers.CharField(source='workshop.name', read_only=True)
    location = serializers.CharField(source='workshop.location', read_only=True)
    rating = serializers.FloatField(source='workshop.rating', read_only=True)
    premium = serializers.BooleanField(source='workshop.premium', read_only=True)

    class Meta:
        model = WorkshopService
        fields = [
            'workshop_name',
            'location',
            'price',
            'rating',
            'premium'
        ]