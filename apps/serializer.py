
from rest_framework import serializers
from reviews.serializer import ReviewSerializer
from .models import Workshop

class WorkshopSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    class Meta:
        model = Workshop
        fields = ['id', 'name', 'owner_name', 'location', 'services', 'phone', 'rating', 'premium', 'reviews', 'created_at', 'updated_at']