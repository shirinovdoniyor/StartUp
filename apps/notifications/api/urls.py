from django.urls import path

from . import views

urlpatterns = [
    path("", views.list_notifications, name="notification-list"),
    path("<uuid:notification_id>/", views.delete_notification, name="notification-delete"),
]
