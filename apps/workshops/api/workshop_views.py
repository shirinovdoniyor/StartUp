from apps.accounts.enums import UserRole
from apps.common.permissions import IsWorkshopOwner
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .. import selectors, services
from ..models import Workshop
from ..serializers import WorkshopReadSerializer, WorkshopWriteSerializer


def _get_owned_workshop(request, pk) -> Workshop:
    workshop = selectors.get_workshop(pk)
    services.ensure_owner(workshop, request.user)
    return workshop


@extend_schema(tags=["Workshops"], responses=WorkshopReadSerializer(many=True), summary="List workshops")
@api_view(["GET"])
@permission_classes([AllowAny])
def workshop_list(request):
    if request.user.is_authenticated and request.user.role == UserRole.WORKSHOP_OWNER:
        qs = selectors.workshops_for_owner(request.user)
    else:
        qs = selectors.public_workshops(search=request.query_params.get("search", ""))
    return Response(WorkshopReadSerializer(qs, many=True).data)


@extend_schema(tags=["Workshops"], request=WorkshopWriteSerializer, responses=WorkshopReadSerializer, summary="Create workshop")
@api_view(["POST"])
@permission_classes([IsWorkshopOwner])
def workshop_create(request):
    serializer = WorkshopWriteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    workshop = services.create_workshop(owner=request.user, data=serializer.validated_data)
    return Response(WorkshopReadSerializer(workshop).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Workshops"], responses=WorkshopReadSerializer, summary="Workshop detail")
@api_view(["GET"])
@permission_classes([AllowAny])
def workshop_detail(request, pk):
    workshop = selectors.get_workshop(pk)
    return Response(WorkshopReadSerializer(workshop).data)


@extend_schema(tags=["Workshops"], request=WorkshopWriteSerializer, responses=WorkshopReadSerializer, summary="Update workshop")
@api_view(["PATCH"])
@permission_classes([IsWorkshopOwner])
def workshop_update(request, pk):
    workshop = _get_owned_workshop(request, pk)
    serializer = WorkshopWriteSerializer(workshop, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    workshop = services.update_workshop(workshop=workshop, data=serializer.validated_data)
    return Response(WorkshopReadSerializer(workshop).data)


@extend_schema(tags=["Workshops"], summary="Delete workshop")
@api_view(["DELETE"])
@permission_classes([IsWorkshopOwner])
def workshop_delete(request, pk):
    workshop = _get_owned_workshop(request, pk)
    services.delete_workshop(workshop=workshop)
    return Response(status=status.HTTP_204_NO_CONTENT)
