from apps.accounts.enums import UserStatus
from apps.accounts.models import User
from apps.accounts.selectors import list_users
from apps.catalog.models import Service
from apps.common.pagination import DefaultPagination
from apps.common.permissions import IsSuperAdmin
from apps.notifications.services import broadcast_to_users
from apps.reviews.models import Review
from apps.workshops.enums import WorkshopStatus
from apps.workshops.models import LocationService, Workshop
from django.db.models import Avg
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from ..serializers import AdminUserSerializer, AdminUserUpdateSerializer, BroadcastSerializer, AdminWorkshopStatusSerializer


@extend_schema(tags=["Admin"], summary="Admin dashboard")
@api_view(["GET"])
@permission_classes([IsSuperAdmin])
def dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)
    data = {
        "total_users": User.objects.count(),
        "active_users": User.objects.filter(status=UserStatus.ACTIVE, deleted_at__isnull=True).count(),
        "new_users_today": User.objects.filter(created_at__date=today).count(),
        "new_users_this_month": User.objects.filter(created_at__date__gte=month_start).count(),
        "total_workshops": Workshop.objects.filter(deleted_at__isnull=True).count(),
        "pending_workshops": Workshop.objects.filter(status=WorkshopStatus.PENDING).count(),
        "premium_workshops": Workshop.objects.filter(premium=True).count(),
        "avg_location_rating": round(
            LocationService.objects.aggregate(a=Avg("location__rating"))["a"] or 0, 2
        ),
        "total_offerings": LocationService.objects.count(),
        "total_services": Service.objects.count(),
        "total_reviews": Review.objects.count(),
    }
    return Response(data)


@extend_schema(tags=["Admin"], responses=AdminUserSerializer(many=True), summary="List users")
@api_view(["GET"])
@permission_classes([IsSuperAdmin])
def user_list(request):
    qs = list_users(
        search=request.query_params.get("search", ""),
        role=request.query_params.get("role", ""),
        status=request.query_params.get("status", ""),
    )
    paginator = DefaultPagination()
    page = paginator.paginate_queryset(qs, request)
    return paginator.get_paginated_response(AdminUserSerializer(page, many=True).data)


@extend_schema(tags=["Admin"], responses=AdminUserSerializer, summary="User detail")
@api_view(["GET"])
@permission_classes([IsSuperAdmin])
def user_detail(request, user_id):
    user = User.objects.get(id=user_id)
    return Response(AdminUserSerializer(user).data)


@extend_schema(tags=["Admin"], request=AdminUserUpdateSerializer, responses=AdminUserSerializer, summary="Update user role/status")
@api_view(["PATCH"])
@permission_classes([IsSuperAdmin])
def user_update(request, user_id):
    user = User.objects.get(id=user_id)
    serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(AdminUserSerializer(user).data)


@extend_schema(tags=["Admin"], request = AdminWorkshopStatusSerializer, summary="Approve/reject/block a workshop")
@api_view(["PATCH"])
@permission_classes([IsSuperAdmin])
def workshop_moderate(request, workshop_id):
    new_status = request.data.get("status")
    if new_status not in WorkshopStatus.values:
        return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
    workshop = Workshop.objects.get(id=workshop_id)
    workshop.status = new_status
    if new_status == WorkshopStatus.APPROVED:
        workshop.is_verified = True
    workshop.save(update_fields=["status", "is_verified", "updated_at"])
    return Response({"id": str(workshop.id), "status": workshop.status, "is_verified": workshop.is_verified})


@extend_schema(tags=["Admin"], request=BroadcastSerializer, summary="Broadcast notification to all active users")
@api_view(["POST"])
@permission_classes([IsSuperAdmin])
def broadcast_notification(request):
    serializer = BroadcastSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    users = User.objects.filter(status=UserStatus.ACTIVE, deleted_at__isnull=True)
    count = broadcast_to_users(
        users, title=serializer.validated_data["title"], message=serializer.validated_data["message"]
    )
    return Response({"message": "Notification sent.", "count": count}, status=status.HTTP_201_CREATED)
