from django.contrib import admin
from django.urls import path

from apps.views import hello_world_api_view

urlpatterns = [
    path('', hello_world_api_view),
]
