from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import Service
from .serializer import ServiceSerializer


# ==========================================================
# LIST SERVICES
# ==========================================================

@extend_schema(
    tags=["Services"],
    summary="Services List",
    responses=ServiceSerializer(many=True),
)
@api_view(["GET"])
def service_list(request):

    services = Service.objects.prefetch_related(
        "problems"
    ).all()

    serializer = ServiceSerializer(
        services,
        many=True,
    )

    return Response(serializer.data)


# ==========================================================
# DETAIL SERVICE
# ==========================================================

@extend_schema(
    tags=["Services"],
    summary="Service Detail",
    responses=ServiceSerializer,
)
@api_view(["GET"])
def service_detail(request, id):

    try:
        service = Service.objects.prefetch_related(
            "problems"
        ).get(id=id)

    except Service.DoesNotExist:

        return Response(
            {
                "error": "Service topilmadi."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = ServiceSerializer(service)

    return Response(serializer.data)


# ==========================================================
# CREATE SERVICE
# ==========================================================

@extend_schema(
    tags=["Services"],
    summary="Create Service",
    request=ServiceSerializer,
    responses=ServiceSerializer,
)
@api_view(["POST"])
@permission_classes([IsAdminUser])
def service_create(request):

    serializer = ServiceSerializer(
        data=request.data
    )

    if serializer.is_valid():

        service = serializer.save()

        return Response(
            ServiceSerializer(service).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


# ==========================================================
# UPDATE SERVICE
# ==========================================================

@extend_schema(
    tags=["Services"],
    summary="Update Service",
    request=ServiceSerializer,
    responses=ServiceSerializer,
)
@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def service_update(request, id):

    try:

        service = Service.objects.get(id=id)

    except Service.DoesNotExist:

        return Response(
            {
                "error": "Service topilmadi."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = ServiceSerializer(
        service,
        data=request.data,
        partial=True,
    )

    if serializer.is_valid():

        service = serializer.save()

        return Response(
            ServiceSerializer(service).data
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


# ==========================================================
# DELETE SERVICE
# ==========================================================

@extend_schema(
    tags=["Services"],
    summary="Delete Service",
)
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def service_delete(request, id):

    try:

        service = Service.objects.get(id=id)

    except Service.DoesNotExist:

        return Response(
            {
                "error": "Service topilmadi."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    service.delete()

    return Response(
        {
            "message": "Service muvaffaqiyatli o'chirildi."
        },
        status=status.HTTP_204_NO_CONTENT,
    )