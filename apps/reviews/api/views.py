from apps.workshops.models import WorkshopLocation
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .. import services
from ..models import Review
from ..serializers import ReviewCreateSerializer, ReviewSerializer


@extend_schema(tags=["Reviews"], responses=ReviewSerializer(many=True), summary="List reviews for a location")
@api_view(["GET"])
@permission_classes([AllowAny])
def location_reviews(request, location_id):
    qs = Review.objects.filter(location_id=location_id).order_by("-created_at")
    return Response(ReviewSerializer(qs, many=True).data)


@extend_schema(tags=["Reviews"], request=ReviewCreateSerializer, responses=ReviewSerializer, summary="Create review for a location")
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_review(request, location_id):
    location = WorkshopLocation.objects.get(id=location_id)
    serializer = ReviewCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    review = services.create_review(
        user=request.user,
        location=location,
        rating=serializer.validated_data["rating"],
        comment=serializer.validated_data.get("comment", ""),
    )
    return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Reviews"], summary="Delete own review")
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_review(request, review_id):
    review = Review.objects.get(id=review_id)
    if review.user_id != request.user.id and not request.user.is_superuser:
        return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
    services.delete_review(review=review)
    return Response(status=status.HTTP_204_NO_CONTENT)
