from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import WorkshopService
from .serializer import (
    WorkshopServiceSerializer,
    WorkshopServiceCreateSerializer,
    WorkshopServiceCreateResponseSerializer, WorkshopServiceUpdateSerializer,
)


# ==========================================================
# LIST
# ==========================================================

@extend_schema(
    tags=["Workshop Services"],
    summary="Workshop Services List",
    responses=WorkshopServiceSerializer(many=True),
)
@api_view(["GET"])
def workshop_service_list(request):

    queryset = (
        WorkshopService.objects
        .select_related(
            "workshop",
            "service",
        )
        .all()
    )

    serializer = WorkshopServiceSerializer(
        queryset,
        many=True,
    )

    return Response(serializer.data)


# ==========================================================
# DETAIL
# ==========================================================

@extend_schema(
    tags=["Workshop Services"],
    summary="Workshop Service Detail",
    responses=WorkshopServiceSerializer,
)
@api_view(["GET"])
def workshop_service_detail(request, id):

    try:

        workshop_service = (
            WorkshopService.objects
            .select_related(
                "workshop",
                "service",
            )
            .get(id=id)
        )

    except WorkshopService.DoesNotExist:

        return Response(
            {
                "error": "Workshop service topilmadi."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = WorkshopServiceSerializer(
        workshop_service
    )

    return Response(serializer.data)


# ==========================================================
# CREATE
# ==========================================================

@extend_schema(
    tags=["Workshop Services"],
    summary="Create Workshop Service",
    request=WorkshopServiceCreateSerializer,
    responses=WorkshopServiceCreateResponseSerializer,
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def workshop_service_create(request):

    serializer = WorkshopServiceCreateSerializer(
        data=request.data
    )

    if serializer.is_valid():

        workshop_service = serializer.save()

        return Response(
            WorkshopServiceCreateResponseSerializer(
                workshop_service
            ).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )







@extend_schema(
    tags=["Workshop Services"],
    summary="Update Workshop Service",
    request=WorkshopServiceUpdateSerializer,
    responses=WorkshopServiceSerializer,
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def workshop_service_update(request, id):

    try:
        workshop_service = WorkshopService.objects.get(id=id)

    except WorkshopService.DoesNotExist:
        return Response(
            {
                "error": "Workshop service topilmadi."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = WorkshopServiceUpdateSerializer(
        workshop_service,
        data=request.data,
        partial=True,
    )

    if serializer.is_valid():

        serializer.save()

        return Response(
            WorkshopServiceSerializer(
                workshop_service
            ).data,
            status=status.HTTP_200_OK,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


@extend_schema(
    tags=["Workshop Services"],
    summary="Delete Workshop Service",
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def workshop_service_delete(request, id):

    try:

        workshop_service = WorkshopService.objects.get(
            id=id
        )

    except WorkshopService.DoesNotExist:

        return Response(
            {
                "error": "Workshop service topilmadi."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    workshop_service.delete()

    return Response(
        {
            "message": "Workshop service muvaffaqiyatli o'chirildi."
        },
        status=status.HTTP_204_NO_CONTENT,
    )


from django.db.models import Q


@extend_schema(
    tags=["Workshop Services"],
    summary="Search Workshop Services",
)
@api_view(["GET"])
def search_workshop_services(request):

    q = request.GET.get("q", "").strip()

    if not q:

        return Response(
            {
                "error": "Qidiruv matni majburiy."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    queryset = (
        WorkshopService.objects
        .select_related(
            "workshop",
            "service",
        )
        .filter(
            Q(service__name__icontains=q)
        )
    )

    serializer = WorkshopServiceSerializer(
        queryset,
        many=True,
    )

    return Response(serializer.data)