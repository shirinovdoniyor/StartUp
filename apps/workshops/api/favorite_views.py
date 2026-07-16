from apps.common.permissions import IsCustomer
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .. import services
from ..models import Favorite, WorkshopLocation
from ..serializers import FavoriteSerializer


@extend_schema(tags=["Favorites"], responses=FavoriteSerializer(many=True), summary="My favorites")
@api_view(["GET"])
@permission_classes([IsCustomer])
def favorite_list(request):
    qs = Favorite.objects.filter(user=request.user).select_related("location")
    return Response(FavoriteSerializer(qs, many=True).data)


@extend_schema(tags=["Favorites"], summary="Add favorite location")
@api_view(["POST"])
@permission_classes([IsCustomer])
def favorite_add(request, location_id):
    location = WorkshopLocation.objects.get(id=location_id)
    services.add_favorite(user=request.user, location=location)
    return Response({"message": "Added to favorites."}, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Favorites"], summary="Remove favorite location")
@api_view(["DELETE"])
@permission_classes([IsCustomer])
def favorite_remove(request, location_id):
    if services.remove_favorite(user=request.user, location_id=location_id):
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
