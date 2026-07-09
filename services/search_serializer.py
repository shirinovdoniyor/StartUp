from rest_framework import serializers

from .models import Problem


class FindWorkshopRequestSerializer(serializers.Serializer):

    problem_id = serializers.PrimaryKeyRelatedField(
        queryset=Problem.objects.all(),
    )


    latitude = serializers.FloatField(
        min_value=-90,
        max_value=90,
    )

    longitude = serializers.FloatField(
        min_value=-180,
        max_value=180,
    )

    radius = serializers.FloatField(
        required=False,
        default=10,
        min_value=1,
        max_value=100,
    )








class WorkshopFindResponseSerializer(serializers.Serializer):

    id = serializers.UUIDField()

    name = serializers.CharField()

    address = serializers.CharField()

    phone = serializers.CharField()

    photo = serializers.ImageField(
        allow_null=True,
    )

    premium = serializers.BooleanField()

    rating = serializers.FloatField()

    rating_count = serializers.IntegerField()

    distance = serializers.FloatField()

    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    matched_services = serializers.ListField(
        child=serializers.CharField(),
    )

    opening_time = serializers.TimeField(
        allow_null=True,
    )

    closing_time = serializers.TimeField(
        allow_null=True,
    )

    latitude = serializers.FloatField()

    longitude = serializers.FloatField()