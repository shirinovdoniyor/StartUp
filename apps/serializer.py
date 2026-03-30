from rest_framework import serializers
from reviews.serializer import ReviewSerializer
from .models import Workshop


class WorkshopSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    photo = serializers.ImageField(use_url=True, required=False)
    rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)
    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Workshop
        fields = [
            'id',
            'name',
            'owner_name',

            'latitude',
            'longitude',

            'phone',
            'rating',
            'rating_count',
            'premium',

            'photo',

            'opening_time',
            'closing_time',

            'reviews',
            'created_at',
            'updated_at',

            'address',
        ]
