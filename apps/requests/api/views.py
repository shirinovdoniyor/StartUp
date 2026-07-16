from apps.accounts.enums import UserRole
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import ServiceRequest
from ..serializers import (
    ServiceRequestCreateSerializer,
    ServiceRequestSerializer,
    ServiceRequestStatusSerializer,
)


@extend_schema(tags=["Service Requests"], responses=ServiceRequestSerializer(many=True), summary="List / create service requests")
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def request_list_create(request):
    if request.method == "POST":
        serializer = ServiceRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = ServiceRequest.objects.create(user=request.user, **serializer.validated_data)
        return Response(ServiceRequestSerializer(obj).data, status=status.HTTP_201_CREATED)

    # Customers see their own; workshop owners and admins see all open requests.
    if request.user.role == UserRole.CUSTOMER:
        qs = ServiceRequest.objects.filter(user=request.user)
    else:
        qs = ServiceRequest.objects.all()
    return Response(ServiceRequestSerializer(qs, many=True).data)


@extend_schema(tags=["Service Requests"], responses=ServiceRequestSerializer, summary="Service request detail")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def request_detail(request, pk):
    obj = ServiceRequest.objects.get(id=pk)
    return Response(ServiceRequestSerializer(obj).data)


@extend_schema(tags=["Service Requests"], request=ServiceRequestStatusSerializer, responses=ServiceRequestSerializer, summary="Update request status")
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def request_update_status(request, pk):
    obj = ServiceRequest.objects.get(id=pk)
    if obj.user_id != request.user.id and request.user.role == UserRole.CUSTOMER:
        return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
    serializer = ServiceRequestStatusSerializer(obj, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(ServiceRequestSerializer(obj).data)
