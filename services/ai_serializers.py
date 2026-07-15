from rest_framework import serializers


class AIRequestSerializer(serializers.Serializer):
    query = serializers.CharField()
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)


class AIResultWorkshopSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    address = serializers.CharField()
    phone = serializers.CharField()
    rating = serializers.FloatField()
    rating_count = serializers.IntegerField()
    premium = serializers.BooleanField()
    matched_services = serializers.ListField(child=serializers.CharField())
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    latitude = serializers.FloatField(allow_null=True)
    longitude = serializers.FloatField(allow_null=True)


class AISearchResponseSerializer(serializers.Serializer):
    ai = serializers.DictField()
    results = AIResultWorkshopSerializer(many=True)
