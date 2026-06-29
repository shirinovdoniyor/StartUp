from rest_framework import serializers

from apps.models import Workshop
from users.models import User


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "name",
            "is_staff",
            "is_active",
            "created_at",
        ]




#-------------------- PATCH /admin/users/{id}/--------------
class AdminUserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "name",
            "is_active",
            "is_staff",
        ]

        extra_kwargs = {
            "name": {"required": False},
            "is_active": {"required": False},
            "is_staff": {"required": False},
        }


#----------------- GET /api/v1/admin/workshops/ --------------

class AdminWorkshopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Workshop
        fields = [
            "id",
            "name",
            "owner_name",
            "address",
            "phone",
            "rating",
            "rating_count",
            "premium",
            "opening_time",
            "closing_time",
            "photo",
            "created_at",
        ]

# -------------PATCH /api/v1/admin/workshops/{id}/-------------------

class AdminWorkshopPatchSerializer(serializers.ModelSerializer):

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
            "premium",
            "photo",
        ]

        extra_kwargs = {
            "name": {"required": False},
            "owner_name": {"required": False},
            "address": {"required": False},
            "phone": {"required": False},
            "opening_time": {"required": False},
            "closing_time": {"required": False},
            "premium": {"required": False},
            "photo": {"required": False},
        }