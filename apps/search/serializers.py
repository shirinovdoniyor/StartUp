from rest_framework import serializers


class LocationResultSerializer(serializers.Serializer):
    location_id = serializers.UUIDField()
    workshop_id = serializers.UUIDField()
    workshop_name = serializers.CharField()
    premium = serializers.BooleanField()
    location_name = serializers.CharField()
    address = serializers.CharField()
    phone = serializers.CharField(allow_null=True)
    rating = serializers.FloatField()
    review_count = serializers.IntegerField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    distance_km = serializers.FloatField(allow_null=True)
    matched_services = serializers.ListField(child=serializers.CharField())
    price_from = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)


class NearbySearchRequestSerializer(serializers.Serializer):
    service_id = serializers.UUIDField(required=False)
    category_id = serializers.UUIDField(required=False)
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)
    radius = serializers.FloatField(required=False, default=10, min_value=1, max_value=100)


class AISearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField()
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    radius = serializers.FloatField(required=False, allow_null=True, min_value=1, max_value=100)


class AISearchResponseSerializer(serializers.Serializer):
    ai = serializers.DictField()
    results = LocationResultSerializer(many=True)
