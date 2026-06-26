from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q

from .models import WorkshopService
from .serializer import (
    WorkshopServiceSerializer,
    WorkshopServiceCreateSerializer,
    WorkshopServiceCreateResponseSerializer,
    WorkshopServiceUpdateSerializer,
)



# -------------------------GET-------------------------
@extend_schema(
    parameters=[
        OpenApiParameter(
            name='q',
            description='Search query (masalan: tormoz, engine)',
            required=True,
            type=str
        )
    ]
)
@api_view(['GET'])
def search_services(request):
    query = request.GET.get('q')

    if not query:
        return Response({"error": "Query required"}, status=400)

    queryset = WorkshopService.objects.filter(
        Q(service_name__icontains=query)
    ).select_related('workshop')

    serializer = WorkshopServiceSerializer(queryset, many=True)
    data = serializer.data

    data = sorted(data, key=lambda x: (-x['premium'], -x['rating'], float(x['price'])))

    return Response(data)


# -------------------------GET workshop services-------------------------
@extend_schema(
    parameters=[
        OpenApiParameter(
            name='workshop_id',
            description='Workshop ID',
            required=True,
            type=int,
            location=OpenApiParameter.PATH,
        )
    ],
    responses=WorkshopServiceSerializer(many=True),
)
@api_view(['GET'])
def workshop_services(request, workshop_id):
    queryset = WorkshopService.objects.filter(
        workshop_id=workshop_id
    ).select_related('workshop')

    if not queryset.exists():
        return Response([], status=200)

    serializer = WorkshopServiceSerializer(queryset, many=True)
    return Response(serializer.data)


# -------------------------POST-------------------------
@extend_schema(
    request=WorkshopServiceCreateSerializer,
    responses=WorkshopServiceCreateResponseSerializer,
)
@api_view(['POST'])
def workshop_service_create(request):
    serializer = WorkshopServiceCreateSerializer(data=request.data)

    if serializer.is_valid():
        instance = serializer.save()
        return Response(WorkshopServiceCreateResponseSerializer(instance).data, status=201)

    return Response(serializer.errors, status=400)



@extend_schema(
    responses={204: None}
)

# -------------------------Delete-------------------------
@api_view(['DELETE'])
def workshop_service_delete(request, pk):
    try:
        ws = WorkshopService.objects.get(id=pk)
    except WorkshopService.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    ws.delete()
    return Response({"message": "Deleted successfully"}, status=204)


# -------------------------PUT-------------------------
@extend_schema(
    request=WorkshopServiceUpdateSerializer,
    responses=WorkshopServiceSerializer,
)
@api_view(['PUT'])
def workshop_service_update(request, pk):
    try:
        ws = WorkshopService.objects.get(id=pk)
    except WorkshopService.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    serializer = WorkshopServiceUpdateSerializer(ws, data=request.data, partial=True)

    if serializer.is_valid():
        instance = serializer.save()
        return Response(WorkshopServiceSerializer(instance).data, status=200)

    return Response(serializer.errors, status=400)