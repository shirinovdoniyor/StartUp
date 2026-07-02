from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q

from .models import WorkshopService, Problem
from .serializer import (
    WorkshopServiceSerializer,
    WorkshopServiceCreateSerializer,
    WorkshopServiceCreateResponseSerializer,
    WorkshopServiceUpdateSerializer,
    ProblemSerializer,
    ProblemCreateSerializer,
    ProblemUpdateSerializer,
)



# -------------------------GET-------------------------
@extend_schema(
    tags=["Services"],

    parameters=[
        OpenApiParameter(
            name='q',
            description='Query bilan qidiring (masalan: tormoz, motor)',
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
    tags=["Services"],

    parameters=[
        OpenApiParameter(
            name='workshop_id',
            description='Workshop ID',
            required=True,
            type=OpenApiTypes.UUID,
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
    tags=["Services"],

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
@extend_schema(
    tags=["Services"],
)
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
    tags=["Services"],

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


# ===================================
# PROBLEM CRUD ENDPOINTS
# ===================================

@extend_schema(
    tags=["Admin Problems"],
    summary="List all problems",
)
@api_view(['GET'])
def admin_problems_list(request):
    problems = Problem.objects.all()
    serializer = ProblemSerializer(problems, many=True)
    return Response(serializer.data)


@extend_schema(
    tags=["Admin Problems"],
    summary="Create a new problem",
    request=ProblemCreateSerializer,
    responses=ProblemSerializer,
)
@api_view(['POST'])
def admin_problems_create(request):
    serializer = ProblemCreateSerializer(data=request.data)

    if serializer.is_valid():
        problem = serializer.save()
        return Response(ProblemSerializer(problem).data, status=201)

    return Response(serializer.errors, status=400)


@extend_schema(
    tags=["Admin Problems"],
    summary="Update a problem",
    request=ProblemUpdateSerializer,
    responses=ProblemSerializer,
)
@api_view(['PATCH'])
def admin_problems_update(request, problem_id):
    try:
        problem = Problem.objects.get(id=problem_id)
    except Problem.DoesNotExist:
        return Response({"error": "Problem not found"}, status=404)

    serializer = ProblemUpdateSerializer(problem, data=request.data, partial=True)

    if serializer.is_valid():
        problem = serializer.save()
        return Response(ProblemSerializer(problem).data, status=200)

    return Response(serializer.errors, status=400)


@extend_schema(
    tags=["Admin Problems"],
    summary="Delete a problem",
)
@api_view(['DELETE'])
def admin_problems_delete(request, problem_id):
    try:
        problem = Problem.objects.get(id=problem_id)
    except Problem.DoesNotExist:
        return Response({"error": "Problem not found"}, status=404)

    problem.delete()
    return Response({"message": "Problem deleted successfully"}, status=204)