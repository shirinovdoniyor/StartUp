from django.db import models
from rest_framework import serializers
from reviews.serializer import ReviewSerializer
from .models import Workshop


class WorkshopSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    photo = models.ImageField(
        upload_to='workshops/images/',
        null=True,
        blank=True
    )

    document = models.FileField(
        upload_to='workshops/docs/',
        null=True,
        blank=True
    )
    rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Workshop
        fields = [
            'id',
            'name',
            'owner_name',


            'phone',
            'rating',
            'rating_count',
            'premium',

            'photo',

            'opening_time',
            'closing_time',

            'reviews',
            'created_at',

            'address',
        ]
