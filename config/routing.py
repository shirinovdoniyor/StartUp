"""WebSocket URL routing for Channels."""

from apps.notifications.consumers import NotificationConsumer
from django.urls import path

websocket_urlpatterns = [
    path("ws/notifications/", NotificationConsumer.as_asgi()),
]
