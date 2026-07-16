from django.urls import path

from . import user_views

urlpatterns = [
    path("me/", user_views.me, name="user-me"),
    path("me/update/", user_views.update_me, name="user-me-update"),
]
