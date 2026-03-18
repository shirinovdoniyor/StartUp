
from rest_framework import serializers
from .models import Workshop, Review

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'workshop', 'user_name', 'rating', 'comment', 'created_at']


class WorkshopSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Workshop
        fields = ['id', 'name', 'owner_name', 'location', 'services', 'phone', 'rating', 'premium', 'reviews', 'created_at', 'updated_at']