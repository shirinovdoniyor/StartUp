from django.db import models
from rest_framework import serializers
from reviews.serializer import ReviewSerializer
from .models import Workshop



class WorkshopSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    photo = serializers.ImageField(required=False)
    document = serializers.FileField(required=False)
    rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Workshop
        fields = [
            'name',
            'owner_name',
            'document',


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
            'latitude',
            'longitude',

        ]




# ------------------------PUT-----------------------
class WorkshopPutSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)

    photo = serializers.ImageField(required=False)

    class Meta:
        model = Workshop
        fields = [
            "name",
            "owner_name",
            "address",
            "phone",
            "opening_time",
            "closing_time",
            "photo",
            "premium",
            "rating",
            "rating_count",
            "reviews",
            "created_at",
        ]


# ------------------------PATCH-------------------------------
class WorkshopPatchSerializer(serializers.ModelSerializer):

    photo = serializers.ImageField(required=False)

    class Meta:
        model = Workshop
        fields = [
            "id",
            "name",
            "owner_name",
            "address",
            "phone",
            "opening_time",
            "closing_time",
            "photo",
            "premium",
        ]

        extra_kwargs = {
            "name": {"required": False},
            "owner_name": {"required": False},
            "address": {"required": False},
            "phone": {"required": False},
            "opening_time": {"required": False},
            "closing_time": {"required": False},
            "photo": {"required": False},
            "premium": {"required": False},
        }