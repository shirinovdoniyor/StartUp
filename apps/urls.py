from django.contrib import admin
from django.urls import path

from apps.views import hello_world_api_view, WorkshopListView, WorkshopDetailView, ReviewCreateView, WorkshopCreateView

urlpatterns = [
    path('', hello_world_api_view),
    path('workshops/create/', WorkshopCreateView.as_view(), name='workshop-create'),  # Yangi
    path('workshops/', WorkshopListView.as_view(), name='workshop-list'),
    path('workshops/<int:pk>/', WorkshopDetailView.as_view(), name='workshop-detail'),
    path('reviews/', ReviewCreateView.as_view(), name='review-create'),
]
