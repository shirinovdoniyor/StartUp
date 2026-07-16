from apps.common.permissions import IsWorkshopOwner
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .. import selectors, services
from ..models import LocationService, WorkshopLocation
from ..serializers import (
    LocationImageSerializer,
    LocationReadSerializer,
    LocationServiceReadSerializer,
    LocationServiceWriteSerializer,
    LocationWriteSerializer,
    WorkingHourSerializer,
)


def _owned_workshop(request, workshop_id):
    workshop = selectors.get_workshop(workshop_id)
    services.ensure_owner(workshop, request.user)
    return workshop


def _get_location(workshop_id, location_id) -> WorkshopLocation:
    return WorkshopLocation.objects.get(id=location_id, workshop_id=workshop_id)


# --- Locations ---------------------------------------------------------------
@extend_schema(tags=["Locations"], responses=LocationReadSerializer(many=True), summary="List workshop locations")
@api_view(["GET"])
@permission_classes([AllowAny])
def location_list(request, workshop_id):
    qs = selectors.locations_for_workshop(workshop_id)
    return Response(LocationReadSerializer(qs, many=True).data)


@extend_schema(tags=["Locations"], request=LocationWriteSerializer, responses=LocationReadSerializer, summary="Create location")
@api_view(["POST"])
@permission_classes([IsWorkshopOwner])
def location_create(request, workshop_id):
    workshop = _owned_workshop(request, workshop_id)
    serializer = LocationWriteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    location = services.create_location(workshop=workshop, data=serializer.validated_data)
    return Response(LocationReadSerializer(location).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Locations"], responses=LocationReadSerializer, summary="Location detail")
@api_view(["GET"])
@permission_classes([AllowAny])
def location_detail(request, workshop_id, location_id):
    location = _get_location(workshop_id, location_id)
    return Response(LocationReadSerializer(location).data)


@extend_schema(tags=["Locations"], request=LocationWriteSerializer, responses=LocationReadSerializer, summary="Update location")
@api_view(["PATCH"])
@permission_classes([IsWorkshopOwner])
def location_update(request, workshop_id, location_id):
    _owned_workshop(request, workshop_id)
    location = _get_location(workshop_id, location_id)
    serializer = LocationWriteSerializer(location, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    location = services.update_location(location=location, data=serializer.validated_data)
    return Response(LocationReadSerializer(location).data)


@extend_schema(tags=["Locations"], summary="Delete location")
@api_view(["DELETE"])
@permission_classes([IsWorkshopOwner])
def location_delete(request, workshop_id, location_id):
    _owned_workshop(request, workshop_id)
    services.delete_location(location=_get_location(workshop_id, location_id))
    return Response(status=status.HTTP_204_NO_CONTENT)


# --- Working hours -----------------------------------------------------------
@extend_schema(tags=["Locations"], request=WorkingHourSerializer(many=True), responses=WorkingHourSerializer(many=True), summary="Set working hours")
@api_view(["PUT"])
@permission_classes([IsWorkshopOwner])
def location_working_hours(request, workshop_id, location_id):
    _owned_workshop(request, workshop_id)
    location = _get_location(workshop_id, location_id)
    serializer = WorkingHourSerializer(data=request.data, many=True)
    serializer.is_valid(raise_exception=True)
    hours = services.set_working_hours(location=location, hours=serializer.validated_data)
    return Response(WorkingHourSerializer(hours, many=True).data)


# --- Images ------------------------------------------------------------------
@extend_schema(tags=["Locations"], request=LocationImageSerializer, responses=LocationImageSerializer, summary="Add location image")
@api_view(["POST"])
@permission_classes([IsWorkshopOwner])
def location_add_image(request, workshop_id, location_id):
    _owned_workshop(request, workshop_id)
    location = _get_location(workshop_id, location_id)
    serializer = LocationImageSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    image = services.add_location_image(location=location, data=serializer.validated_data)
    return Response(LocationImageSerializer(image).data, status=status.HTTP_201_CREATED)


# --- Offerings (location services) -------------------------------------------
@extend_schema(tags=["Offerings"], responses=LocationServiceReadSerializer(many=True), summary="List location offerings")
@api_view(["GET"])
@permission_classes([AllowAny])
def offering_list(request, workshop_id, location_id):
    qs = selectors.location_services_for_location(location_id)
    return Response(LocationServiceReadSerializer(qs, many=True).data)


@extend_schema(tags=["Offerings"], request=LocationServiceWriteSerializer, responses=LocationServiceReadSerializer, summary="Add offering")
@api_view(["POST"])
@permission_classes([IsWorkshopOwner])
def offering_create(request, workshop_id, location_id):
    _owned_workshop(request, workshop_id)
    location = _get_location(workshop_id, location_id)
    serializer = LocationServiceWriteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    offering = services.add_location_service(location=location, data=serializer.validated_data)
    return Response(LocationServiceReadSerializer(offering).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Offerings"], request=LocationServiceWriteSerializer, responses=LocationServiceReadSerializer, summary="Update offering")
@api_view(["PATCH"])
@permission_classes([IsWorkshopOwner])
def offering_update(request, workshop_id, location_id, offering_id):
    _owned_workshop(request, workshop_id)
    offering = LocationService.objects.get(id=offering_id, location_id=location_id)
    serializer = LocationServiceWriteSerializer(offering, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    offering = services.update_location_service(offering=offering, data=serializer.validated_data)
    return Response(LocationServiceReadSerializer(offering).data)


@extend_schema(tags=["Offerings"], summary="Delete offering")
@api_view(["DELETE"])
@permission_classes([IsWorkshopOwner])
def offering_delete(request, workshop_id, location_id, offering_id):
    _owned_workshop(request, workshop_id)
    LocationService.objects.filter(id=offering_id, location_id=location_id).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
