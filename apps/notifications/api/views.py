from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .. import services
from ..models import Notification
from ..serializers import NotificationSerializer


@extend_schema(tags=["Notifications"], responses=NotificationSerializer(many=True), summary="My unread notifications")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_notifications(request):
    qs = Notification.objects.filter(user=request.user, is_read=False).order_by("-created_at")
    return Response({"count": qs.count(), "results": NotificationSerializer(qs, many=True).data})


@extend_schema(tags=["Notifications"], summary="Delete a notification")
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_notification(request, notification_id):
    if services.delete_notification(user=request.user, notification_id=notification_id):
        return Response({"message": "Notification deleted."})
    return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
