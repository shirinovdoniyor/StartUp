from apps.accounts.models import User
from rest_framework import serializers
from apps.workshops.models import Workshop


class AdminUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "phone", "first_name", "last_name", "full_name", "email", "role", "status", "created_at"]


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["role", "status"]
        extra_kwargs = {"role": {"required": False}, "status": {"required": False}}


class BroadcastSerializer(serializers.Serializer):
    title = serializers.CharField()
    message = serializers.CharField()
class AdminWorkshopStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workshop
        fields = ["status"]
        extra_kwargs = {"status": {"required": False}}