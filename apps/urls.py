from django.urls import path
from .views import (
    hello_world_api_view,
    workshop_create,
    workshop_list,
    workshop_detail,
    owner_dashboard,
    workshop_delete, workshop_put, workshop_patch,
)


urlpatterns = [
    path('', hello_world_api_view),

    path('workshops/', workshop_list, name='workshop-list'),
    path('workshops/create/', workshop_create, name='workshop-create'),
    path('workshops/<uuid:pk>/', workshop_detail, name='workshop-detail'),

    path('workshops/<uuid:pk>/put/', workshop_put, name='workshop-put'),
    path('workshops/<uuid:pk>/patch/', workshop_patch, name='workshop-patch'),

    path('workshops/<uuid:pk>/delete/', workshop_delete, name='workshop-delete'),
    path('workshops/owner/dashboard/', owner_dashboard, name='owner-dashboard'),
]
