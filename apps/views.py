from django.http import JsonResponse
from drf_spectacular.utils import extend_schema

from .serializer import WorkshopSerializer, ReviewSerializer
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Workshop
from rapidfuzz import fuzz
@api_view(['GET'])
def hello_world_api_view(request):
    return JsonResponse({"message": "helloworld"})



# ----------------GET id bilan-------------------
@api_view(['GET'])
def workshop_detail(request, pk):
    try:
        workshop = Workshop.objects.get(id=pk)
    except Workshop.DoesNotExist:
        return Response({"error": "Workshop not found"}, status=404)

    serializer = WorkshopSerializer(workshop)
    return Response(serializer.data)

# -------------------POST--------------------
@extend_schema(
    request=WorkshopSerializer,
    responses=WorkshopSerializer
)
@api_view(['POST'])
def workshop_create(request):
    serializer = WorkshopSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --------------GET+SEARCH---------------
@api_view(['GET'])
def workshop_list(request):
    queryset = Workshop.objects.all().order_by('-premium', '-rating')

    q = request.GET.get('q')
    location = request.GET.get('location')
    min_rating = request.GET.get('min_rating')

    # 🔍 umumiy search
    if q:
        queryset = queryset.filter(
            Q(name__icontains=q) |
            Q(location__icontains=q)
        )

    # 📍 location filter
    if location:
        queryset = queryset.filter(location__icontains=location)

    # ⭐ rating filter
    if min_rating:
        try:
            queryset = queryset.filter(rating__gte=float(min_rating))
        except ValueError:
            return Response({"error": "min_rating must be a number"}, status=400)

    serializer = WorkshopSerializer(queryset, many=True)
    return Response(serializer.data)
@extend_schema(
    request=WorkshopSerializer,
    responses=WorkshopSerializer
)
@api_view(['PUT', 'PATCH'])
def workshop_update(request, pk):
    try:
        workshop = Workshop.objects.get(id=pk)
    except Workshop.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    # 🔥 muhim joy
    partial = request.method == 'PATCH'

    serializer = WorkshopSerializer(
        workshop,
        data=request.data,
        partial=partial
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)

# -----------------DELETE-------------------
@api_view(['DELETE'])
def workshop_delete(request, pk):
    try:
        workshop = Workshop.objects.get(id=pk)
    except Workshop.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    workshop.delete()
    return Response({"message": "Deleted successfully"}, status=204)