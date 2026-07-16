from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..services import AISearchService, nearby_search
from ..serializers import (
    AISearchRequestSerializer,
    AISearchResponseSerializer,
    LocationResultSerializer,
    NearbySearchRequestSerializer,
)


@extend_schema(
    tags=["Search"],
    parameters=[NearbySearchRequestSerializer],
    responses=LocationResultSerializer(many=True),
    summary="Nearby location search by service/category",
)
@api_view(["GET"])
@permission_classes([AllowAny])
def nearby(request):
    serializer = NearbySearchRequestSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    results = nearby_search(
        service_id=data.get("service_id"),
        category_id=data.get("category_id"),
        user_lat=data["latitude"],
        user_lng=data["longitude"],
        radius_km=data["radius"],
    )
    return Response(LocationResultSerializer(results, many=True).data)


@extend_schema(
    tags=["Search"],
    request=AISearchRequestSerializer,
    responses=AISearchResponseSerializer,
    summary="AI semantic search",
)
@api_view(["POST"])
@permission_classes([AllowAny])
def ai_search(request):
    serializer = AISearchRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    try:
        result = AISearchService().search(
            data["query"].strip(),
            user_lat=data.get("latitude"),
            user_lng=data.get("longitude"),
            radius_km=data.get("radius"),
        )
    except RuntimeError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response(AISearchResponseSerializer(result).data)
