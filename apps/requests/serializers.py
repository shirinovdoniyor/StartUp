from rest_framework import serializers

from .models import ServiceRequest


class ServiceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = [
            "id",
            "user",
            "title",
            "description",
            "latitude",
            "longitude",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class ServiceRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = ["title", "description", "latitude", "longitude"]


class ServiceRequestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = ["status"]
