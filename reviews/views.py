from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import status, serializers

from apps.serializer import ReviewSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.models import Workshop
from reviews.models import Review


# --------------GET------------------
@api_view(['GET'])
def list_reviews(request, workshop_id):
    try:
        workshop = Workshop.objects.get(id=workshop_id)
    except Workshop.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    reviews = workshop.reviews.all()  # 🔥 shu yerda olishimiz mumkin
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)




# --------------POST------------------

@extend_schema(
    request=ReviewSerializer,
    responses=ReviewSerializer
)
@api_view(['POST'])

def create_review(request, workshop_id):
    try:
        workshop = Workshop.objects.get(id=workshop_id)
    except Workshop.DoesNotExist:
        return Response({"error": "Workshop not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(workshop=workshop)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# --------------DELETE------------------


@api_view(['DELETE'])
def delete_review(request, review_id):
    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return Response({"error": "Review not found"}, status=404)

    review.delete()
    return Response({"message": "Review deleted"}, status=204)





