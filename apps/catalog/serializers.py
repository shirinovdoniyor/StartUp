from django.utils.text import slugify
from rest_framework import serializers

from .models import Category, Service, ServiceAlias


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "icon", "sort_order", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        if not attrs.get("slug") and attrs.get("name"):
            attrs["slug"] = slugify(attrs["name"])
        return attrs


class ServiceAliasSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceAlias
        fields = ["id", "alias"]
        read_only_fields = ["id"]


class ServiceSerializer(serializers.ModelSerializer):
    aliases = ServiceAliasSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    slug = serializers.SlugField(required=False)

    class Meta:
        model = Service
        fields = [
            "id",
            "category",
            "category_name",
            "name",
            "slug",
            "description",
            "estimated_duration_minutes",
            "aliases",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        if not attrs.get("slug") and attrs.get("name"):
            attrs["slug"] = slugify(attrs["name"])
        return attrs
