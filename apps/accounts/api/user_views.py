from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .. import services
from ..serializers import ProfileUpdateSerializer, UserProfileSerializer


@extend_schema(tags=["Users"], responses=UserProfileSerializer, summary="Current user profile")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserProfileSerializer(request.user).data)


@extend_schema(tags=["Users"], request=ProfileUpdateSerializer, responses=UserProfileSerializer, summary="Update profile")
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_me(request):
    serializer = ProfileUpdateSerializer(data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    user = services.update_profile(request.user, serializer.validated_data)
    return Response(UserProfileSerializer(user).data)
