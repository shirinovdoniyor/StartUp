from rest_framework import serializers

from users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "phone",
            "created_at",
            "updated_at",
        ]