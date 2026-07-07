from rest_framework import serializers

from users.models import User, Notification


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


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "message", "is_read", "created_at", "updated_at"]
        read_only_fields = ["id", "title", "message", "created_at", "updated_at"]