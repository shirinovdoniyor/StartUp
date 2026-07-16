from django.urls import path

from . import views

urlpatterns = [
    path("", views.request_list_create, name="request-list-create"),
    path("<uuid:pk>/", views.request_detail, name="request-detail"),
    path("<uuid:pk>/status/", views.request_update_status, name="request-status"),
]
