from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q

from .models import WorkshopService
from .serializer import WorkshopServiceSerializer



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
        Q(service__name__icontains=query) |
        Q(service__problem__name__icontains=query)
    ).select_related('workshop', 'service')

    serializer = WorkshopServiceSerializer(queryset, many=True)
    data = serializer.data

    data = sorted(data, key=lambda x: (-x['premium'], -x['rating'], float(x['price'])))

    return Response(data)

