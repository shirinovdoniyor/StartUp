from django.urls import path
from .views import search_services

urlpatterns = [
    path('search/', search_services),
]