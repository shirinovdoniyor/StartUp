from django.shortcuts import render


from django.db.models import Avg
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

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

    dashboard = {
        "total_users": User.objects.count(),

        "total_workshops": Workshop.objects.count(),

        "premium_workshops": Workshop.objects.filter(
            premium=True
        ).count(),

        "total_services": WorkshopService.objects.count(),

        "total_reviews": Review.objects.count(),

        "average_rating": round(
            Workshop.objects.aggregate(
                average=Avg("rating")
            )["average"] or 0,
            1
        ),
    }

    return Response(dashboard)