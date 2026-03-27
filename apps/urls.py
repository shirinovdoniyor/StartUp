from django.urls import path
from .views import (
    hello_world_api_view,
    workshop_create,
    workshop_list,
    workshop_detail,
    workshop_update,
    workshop_delete,
)

urlpatterns = [
    # test
    path('', hello_world_api_view),

    # workshops
    path('workshops/', workshop_list, name='workshop-list'),
    path('workshops/create/', workshop_create, name='workshop-create'),
    path('workshops/<int:pk>/', workshop_detail, name='workshop-detail'),
    path('workshops/<int:pk>/update/', workshop_update, name='workshop-update'),
    path('workshops/<int:pk>/delete/', workshop_delete, name='workshop-delete'),
]
