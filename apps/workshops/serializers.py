from rest_framework import serializers

from .models import (
    Favorite,
    LocationImage,
    LocationService,
    Workshop,
    WorkshopLocation,
    WorkingHour,
)


# --- Working hours / images --------------------------------------------------
class WorkingHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHour
        fields = ["id", "day_of_week", "open_time", "close_time", "is_closed"]
        read_only_fields = ["id"]


class LocationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationImage
        fields = ["id", "image_url", "is_primary", "sort_order", "created_at"]
        read_only_fields = ["id", "created_at"]


# --- Location services -------------------------------------------------------
class LocationServiceReadSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    category = serializers.CharField(source="service.category.name", read_only=True)

    class Meta:
        model = LocationService
        fields = [
            "id",
            "service",
            "service_name",
            "category",
            "display_name",
            "price_type",
            "price_from",
            "price_to",
            "estimated_duration_minutes",
            "is_available",
        ]


class LocationServiceWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationService
        fields = [
            "service",
            "display_name",
            "price_type",
            "price_from",
            "price_to",
            "estimated_duration_minutes",
            "is_available",
        ]

    def validate(self, attrs):
        price_type = attrs.get("price_type", getattr(self.instance, "price_type", None))
        price_from = attrs.get("price_from", getattr(self.instance, "price_from", None))
        price_to = attrs.get("price_to", getattr(self.instance, "price_to", None))

        if price_type == "FIXED" and price_from is None:
            raise serializers.ValidationError("FIXED narx uchun price_from majburiy.")
        if price_type == "RANGE" and (price_from is None or price_to is None):
            raise serializers.ValidationError("RANGE narx uchun price_from va price_to majburiy.")
        if price_from is not None and price_to is not None and price_to < price_from:
            raise serializers.ValidationError("price_to price_from dan kichik bo'lishi mumkin emas.")
        return attrs


# --- Location ----------------------------------------------------------------
class LocationReadSerializer(serializers.ModelSerializer):
    working_hours = WorkingHourSerializer(many=True, read_only=True)
    images = LocationImageSerializer(many=True, read_only=True)

    class Meta:
        model = WorkshopLocation
        fields = [
            "id",
            "workshop",
            "name",
            "slug",
            "phone",
            "address",
            "region",
            "district",
            "latitude",
            "longitude",
            "rating",
            "review_count",
            "is_main",
            "status",
            "working_hours",
            "images",
            "created_at",
            "updated_at",
        ]


class LocationWriteSerializer(serializers.ModelSerializer):
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=False, allow_null=True)

    class Meta:
        model = WorkshopLocation
        fields = [
            "name",
            "phone",
            "address",
            "region",
            "district",
            "latitude",
            "longitude",
            "is_main",
            "status",
        ]


# --- Workshop ----------------------------------------------------------------
class WorkshopReadSerializer(serializers.ModelSerializer):
    locations_count = serializers.IntegerField(source="locations.count", read_only=True)

    class Meta:
        model = Workshop
        fields = [
            "id",
            "owner",
            "name",
            "slug",
            "description",
            "logo_url",
            "website",
            "telegram",
            "instagram",
            "status",
            "is_verified",
            "premium",
            "locations_count",
            "created_at",
            "updated_at",
        ]


class WorkshopWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workshop
        fields = [
            "name",
            "description",
            "logo_url",
            "website",
            "telegram",
            "instagram",
        ]


class FavoriteSerializer(serializers.ModelSerializer):
    location_detail = LocationReadSerializer(source="location", read_only=True)

    class Meta:
        model = Favorite
        fields = ["location", "location_detail", "created_at"]
        read_only_fields = ["created_at"]
