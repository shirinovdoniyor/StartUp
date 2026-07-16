from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="admin-dashboard"),
    path("users/", views.user_list, name="admin-users"),
    path("users/<uuid:user_id>/", views.user_detail, name="admin-user-detail"),
    path("users/<uuid:user_id>/update/", views.user_update, name="admin-user-update"),
    path("workshops/<uuid:workshop_id>/moderate/", views.workshop_moderate, name="admin-workshop-moderate"),
    path("notifications/broadcast/", views.broadcast_notification, name="admin-broadcast"),
]
