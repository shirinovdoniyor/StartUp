from rest_framework import status

from apps.serializer import ReviewSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.models import Workshop


@api_view(['GET'])
def list_reviews(request, workshop_id):
    try:
        workshop = Workshop.objects.get(id=workshop_id)
    except Workshop.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    reviews = workshop.reviews.all()  # 🔥 shu yerda olishimiz mumkin
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)



@api_view(['POST'])
def create_review(request, workshop_id):
    try:
        workshop = Workshop.objects.get(id=workshop_id)
    except Workshop.DoesNotExist:
        return Response({"error": "Workshop not found"}, status=status.HTTP_404_NOT_FOUND)

    # request.data ga user_name, rating, comment bo‘lishi kerak
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(workshop=workshop)  # workshopni shu yerda qo‘shamiz
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)