from django.urls import path
from apps.views import hello_world_api_view, WorkshopDetailView, WorkshopCreateView, workshop_list

urlpatterns = [
    path('', hello_world_api_view),
    path('workshops/create/', WorkshopCreateView.as_view(), name='workshop-create'),
    path('api/workshops/', workshop_list, name='workshop-list-api'),

    path('workshops/<int:pk>/', WorkshopDetailView.as_view(), name='workshop-detail'),
]
