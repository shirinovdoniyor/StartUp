from django.db.models import Q, Model, Avg
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, OpenApiRequest, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.parsers import MultiPartParser, FormParser

from .serializer import WorkshopSerializer, WorkshopPutSerializer, WorkshopPatchSerializer
from rest_framework import  status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from .models import Workshop
from .utils import get_coordinates
from services.models import WorkshopService
from reviews.models import Review
from users.models import User
from geopy.distance import geodesic
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes


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
@api_view(["POST"])
def workshop_create(request):

    serializer = WorkshopSerializer(data=request.data)

    if serializer.is_valid():

        latitude = serializer.validated_data.get("latitude")
        longitude = serializer.validated_data.get("longitude")

        # Frontend latitude va longitude yubormagan bo'lsa
        if latitude is None or longitude is None:

            latitude, longitude = get_coordinates(
                serializer.validated_data["address"]
            )

        serializer.save(
            latitude=latitude,
            longitude=longitude,
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )
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


@extend_schema(
    tags=["Workshops"],
    summary="Workshop Statistics",
)
@api_view(["GET"])
def workshop_statistics(request, pk):
    try:
        workshop = Workshop.objects.get(id=pk)
    except Workshop.DoesNotExist:
        return Response({"error": "Workshop not found"}, status=404)

    services_count = workshop.services.count()
    reviews_count = workshop.reviews.count()
    average_rating = round(workshop.rating, 1)

    return Response({
        "services": services_count,
        "reviews": reviews_count,
        "average_rating": average_rating
    })


@extend_schema(
    tags=["Workshops"],
    summary="Top Rated Workshops",
)
@api_view(["GET"])
def top_rated_workshops(request):
    limit = request.GET.get('limit', 10)
    try:
        limit = int(limit)
    except ValueError:
        limit = 10

    workshops = Workshop.objects.all().order_by('-rating')[:limit]
    serializer = WorkshopSerializer(workshops, many=True)
    return Response(serializer.data)


@extend_schema(
    tags=["Owners"],
    summary="Owner Dashboard",
    parameters=[
        OpenApiParameter(
            name="owner_id",
            description="Owner ID to filter workshops",
            required=False,
            type=OpenApiTypes.UUID,
        ),
        OpenApiParameter(
            name="phone",
            description="Owner phone to filter workshops",
            required=False,
            type=OpenApiTypes.STR,
        ),
    ]
)
@api_view(["GET"])
def owner_dashboard(request):
    owner_id = request.GET.get("owner_id")
    phone = request.GET.get("phone")

    if not owner_id and not phone:
        return Response({"error": "Provide owner_id or phone as query parameter"}, status=400)

    if owner_id:
        try:
            user = User.objects.get(id=owner_id)
        except User.DoesNotExist:
            return Response({"error": "Owner not found"}, status=404)

        if phone and phone != user.phone:
            return Response({"error": "Provided phone does not match owner"}, status=403)

        phone = user.phone

    workshops = Workshop.objects.filter(phone=phone)

    total_workshops = workshops.count()
    total_services = WorkshopService.objects.filter(workshop__in=workshops).count()
    total_reviews = Review.objects.filter(workshop__in=workshops).count()

    average_rating = round(
        workshops.aggregate(avg=Avg("rating"))["avg"] or 0,
        1
    )

    workshop_list = []
    for w in workshops:
        workshop_list.append({
            "id": str(w.id),
            "name": w.name,
            "rating": w.rating,
            "rating_count": w.rating_count,
            "services_count": w.services.count(),
            "reviews_count": w.reviews.count(),
        })

    dashboard = {
        "total_workshops": total_workshops,
        "total_services": total_services,
        "total_reviews": total_reviews,
        "average_rating": average_rating,
        "workshops": workshop_list,
    }

    return Response(dashboard)