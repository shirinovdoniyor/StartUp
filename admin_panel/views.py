from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

from admin_panel.filters import AdminUserFilter
from admin_panel.serializer import AdminUserSerializer, AdminUserUpdateSerializer, AdminWorkshopSerializer, \
    AdminWorkshopPatchSerializer
from users.models import User
from apps.models import Workshop
from services.models import WorkshopService
from reviews.models import Review



@extend_schema(
    tags=["Admin"],
    summary="Admin Dashboard"
)
@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    dashboard = {
        # User statistics
        "total_users": User.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "new_users_today": User.objects.filter(
            created_at__date=today
        ).count(),
        "new_users_this_month": User.objects.filter(
            created_at__date__gte=month_start
        ).count(),

        # Workshop statistics
        "premium_workshops": Workshop.objects.filter(premium=True).count(),
        "normal_workshops": Workshop.objects.filter(premium=False).count(),
        "average_rating": round(
            Workshop.objects.aggregate(average=Avg("rating"))["average"] or 0,
            1
        ),

        # Service and Review statistics
        "total_services": WorkshopService.objects.count(),
        "total_reviews": Review.objects.count(),
    }

    return Response(dashboard)




# -------------------------GET admin/users---------------
# @extend_schema(
#     tags=["Admin"],
#     summary="Users List"
# )
@extend_schema(
    tags=["Admin"],
    summary="Users List",
    parameters=[
        OpenApiParameter(
            name="search",
            description="Search by name or phone",
            required=False,
            type=OpenApiTypes.STR,
        ),
        OpenApiParameter(
            name="page",
            description="Page number",
            required=False,
            type=OpenApiTypes.INT,
        ),
        OpenApiParameter(
            name="page_size",
            description="Items per page",
            required=False,
            type=OpenApiTypes.INT,
        ),
        OpenApiParameter(
            name="ordering",
            description="Ordering: name, -name, created_at, -created_at",
            required=False,
            type=OpenApiTypes.STR,
        ),
        OpenApiParameter(
            name="is_active",
            description="Filter active users",
            required=False,
            type=OpenApiTypes.BOOL,
        ),
        OpenApiParameter(
            name="is_staff",
            description="Filter admin users",
            required=False,
            type=OpenApiTypes.BOOL,
        ),
    ],
    responses=AdminUserSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_users(request):

    queryset = User.objects.all().order_by("-created_at")

    # ---------------- Filter ----------------

    queryset = AdminUserFilter(
        request.GET,
        queryset=queryset
    ).qs

    # ---------------- Search ----------------

    search = request.GET.get("search")

    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(phone__icontains=search)
        )

    # ---------------- Ordering ----------------

    ordering = request.GET.get("ordering")

    allowed_ordering = [
        "created_at",
        "-created_at",
        "name",
        "-name",
        "phone",
        "-phone",
    ]

    if ordering in allowed_ordering:
        queryset = queryset.order_by(ordering)

    # ---------------- Pagination ----------------

    paginator = PageNumberPagination()

    paginator.page_size = int(
        request.GET.get("page_size", 10)
    )

    page = paginator.paginate_queryset(
        queryset,
        request
    )

    serializer = AdminUserSerializer(
        page,
        many=True
    )

    return paginator.get_paginated_response(
        serializer.data
    )



# -------------------------GET admin/users{id}---------------


@extend_schema(
    tags=["Admin"],
    summary="User Detail",
    responses=AdminUserSerializer,
)
@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_user_detail(request, id):

    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=404
        )

    serializer = AdminUserSerializer(user)

    return Response(serializer.data)



# ---------------------PATCH /admin/users/{id}/-------------------


@extend_schema(
    tags=["Admin"],
    summary="Update User",
    request=AdminUserUpdateSerializer,
    responses=AdminUserSerializer,
)
@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def admin_user_update(request, id):

    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=404
        )

    serializer = AdminUserUpdateSerializer(
        user,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()

        return Response(
            AdminUserSerializer(user).data
        )

    return Response(serializer.errors, status=400)

# -------------GET /api/v1/admin/workshops/-----------------


@extend_schema(
    tags=["Admin"],
    summary="Workshop List",
    responses=AdminWorkshopSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_workshops(request):

    workshops = Workshop.objects.all().order_by("-created_at")

    serializer = AdminWorkshopSerializer(
        workshops,
        many=True
    )

    return Response(serializer.data)



# ------------GET /api/v1/admin/workshops/{id}/-----------------
@extend_schema(
    tags=["Admin"],
    summary="Workshop Detail",
    responses=AdminWorkshopSerializer,
)
@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_workshop_detail(request, id):

    try:
        workshop = Workshop.objects.get(id=id)
    except Workshop.DoesNotExist:
        return Response(
            {"error": "Workshop not found"},
            status=404
        )

    serializer = AdminWorkshopSerializer(workshop)

    return Response(serializer.data)



# ---------------------DELETE /api/v1/admin/workshops/{id}/--------------
@extend_schema(
    tags=["Admin"],
    summary="Delete Workshop",
)
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def admin_workshop_delete(request, id):

    try:
        workshop = Workshop.objects.get(id=id)
    except Workshop.DoesNotExist:
        return Response(
            {"error": "Workshop not found"},
            status=404
        )

    workshop.delete()

    return Response(
        {"message": "Workshop deleted successfully"},
        status=204
    )


# -------------PATCH /api/v1/admin/workshops/{id}/-------------------
from apps.utils import get_coordinates  # siz ishlatayotgan funksiya

@extend_schema(
    tags=["Admin"],
    summary="Update Workshop",
    request=AdminWorkshopPatchSerializer,
    responses=AdminWorkshopSerializer,
)
@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def admin_workshop_update(request, id):

    try:
        workshop = Workshop.objects.get(id=id)
    except Workshop.DoesNotExist:
        return Response(
            {"error": "Workshop not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    data = request.data.copy()

    # Address o'zgarsa koordinatalarni ham yangilash
    if "address" in data:
        lat, lng = get_coordinates(data["address"])
        data["latitude"] = lat
        data["longitude"] = lng

    serializer = AdminWorkshopPatchSerializer(
        workshop,
        data=data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()

        return Response(
            AdminWorkshopSerializer(workshop).data
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# ===================================
# ADMIN SEARCH ENDPOINT
# ===================================

@extend_schema(
    tags=["Admin"],
    summary="Global Admin Search",
    parameters=[
        OpenApiParameter(
            name='q',
            description='Search query for users, workshops, and services',
            required=True,
            type=OpenApiTypes.STR,
        ),
    ]
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_search(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return Response({
            "users": [],
            "workshops": [],
            "services": []
        })

    # Search users
    users = User.objects.filter(
        Q(name__icontains=query) | 
        Q(phone__icontains=query)
    ).values('id', 'phone', 'name')[:5]

    # Search workshops
    workshops = Workshop.objects.filter(
        Q(name__icontains=query) | 
        Q(address__icontains=query)
    ).values('id', 'name', 'address', 'rating')[:5]

    # Search services
    services = WorkshopService.objects.filter(
        Q(service_name__icontains=query)
    ).select_related('workshop').values(
        'id', 'service_name', 'workshop__name', 'price'
    )[:5]

    return Response({
        "users": list(users),
        "workshops": list(workshops),
        "services": list(services),
    })