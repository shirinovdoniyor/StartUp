from django.db.models import Q, Model
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, OpenApiRequest
from rest_framework.parsers import MultiPartParser, FormParser

from .serializer import WorkshopSerializer, WorkshopPutSerializer, WorkshopPatchSerializer
from rest_framework import  status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from .models import Workshop
from .utils import get_coordinates

@extend_schema(
    tags=["System"],
)
@api_view(['GET'])
def hello_world_api_view(request):
    return JsonResponse({"message": "helloworld"})



# ----------------GET id bilan-------------------
@extend_schema(
    tags=["Workshops"],
)
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
    tags=["Workshops"],
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'owner_name': {'type': 'string'},
                'address': {'type': 'string'},
                'phone': {'type': 'string'},
                'photo': {
                    'type': 'string',
                    'format': 'binary'
                },
                'opening_time': {'type': 'string'},
                'closing_time': {'type': 'string'},
            },
            'required': ['name', 'owner_name', 'phone','address']
        }
    },
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

@extend_schema(
    tags=["Workshops"]
)
@api_view(['GET'])
def workshop_list(request):
    queryset = Workshop.objects.all().order_by('-premium', '-rating')

    q = request.GET.get('q')
    min_rating = request.GET.get('min_rating')

    # 🔍 umumiy search (faqat name)
    if q:
        queryset = queryset.filter(
            Q(name__icontains=q)
        )

    # ⭐ rating filter
    if min_rating:
        try:
            queryset = queryset.filter(rating__gte=float(min_rating))
        except ValueError:
            return Response({"error": "min_rating must be a number"}, status=400)

    serializer = WorkshopSerializer(queryset, many=True)
    return Response(serializer.data)

# -------------------PUT--------------------
@parser_classes([MultiPartParser, FormParser])
@extend_schema(
    tags=["Workshops"],
    request=OpenApiRequest(
        request=WorkshopPutSerializer,
        encoding={
            "photo": {
                "contentType": "image/*"
            }
        }
    ),
    responses=WorkshopPutSerializer,
)
@api_view(["PUT"])
def workshop_put(request, pk):
    try:
        workshop = Workshop.objects.get(pk=pk)
    except Workshop.DoesNotExist:
        return Response(
            {"error": "Workshop not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    data = request.data.copy()

    if "address" in data:
        lat, lng = get_coordinates(data["address"])
        data["latitude"] = lat
        data["longitude"] = lng

    serializer = WorkshopPutSerializer(
        workshop,
        data=data
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# -------------------------PATCH--------------------

@parser_classes([MultiPartParser, FormParser])
@extend_schema(
    tags=["Workshops"],
    request=WorkshopPatchSerializer,
    responses=WorkshopPutSerializer
)
@api_view(["PATCH"])
def workshop_patch(request, pk):
    try:
        workshop = Workshop.objects.get(pk=pk)
    except Workshop.DoesNotExist:
        return Response(
            {"error": "Workshop not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    data = request.data.copy()

    if "address" in data:
        lat, lng = get_coordinates(data["address"])
        data["latitude"] = lat
        data["longitude"] = lng

    serializer = WorkshopPatchSerializer(
        workshop,
        data=data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(
            WorkshopPutSerializer(workshop).data
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------DELETE-------------------
@extend_schema(tags=["Workshops"],)
@api_view(['DELETE'])
def workshop_delete(request, pk):
    try:
        workshop = Workshop.objects.get(id=pk)
    except Workshop.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    workshop.delete()
    return Response({"message": "Deleted successfully"}, status=204)