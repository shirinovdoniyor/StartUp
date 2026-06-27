from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.models import Workshop
from reviews.models import Review
from reviews.serializer import ReviewSerializer
# --------------GET------------------

@api_view(['GET'])
def list_reviews(request, workshop_id):
    try:
        workshop = Workshop.objects.get(id=workshop_id)
    except Workshop.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    reviews = workshop.reviews.all().order_by('-created_at')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)



# --------------POST------------------
@extend_schema(
    request=ReviewSerializer,
    responses=ReviewSerializer
)
@api_view(['POST'])
def create_review(request, workshop_id):
    if not request.user:
        return Response({"error": "Authentication required"}, status=401)

    try:
        workshop = Workshop.objects.get(id=workshop_id)
    except Workshop.DoesNotExist:
        return Response({"error": "Workshop not found"}, status=404)

    serializer = ReviewSerializer(data=request.data)

    if serializer.is_valid():
        review = serializer.save(
            workshop=workshop,
            user=request.user
        )

        workshop.rating_count += 1
        workshop.rating = (
            (workshop.rating * (workshop.rating_count - 1) + review.rating)
            / workshop.rating_count
        )
        workshop.save()

        return Response(ReviewSerializer(review).data, status=201)

    return Response(serializer.errors, status=400)


# --------------DELETE------------------
@api_view(['DELETE'])
def delete_review(request, review_id):
    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return Response({"error": "Review not found"}, status=404)

    review.delete()
    return Response({"message": "Deleted"}, status=204)





