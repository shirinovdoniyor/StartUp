from django.urls import path

from . import favorite_views

urlpatterns = [
    path("", favorite_views.favorite_list, name="favorite-list"),
    path("<uuid:location_id>/", favorite_views.favorite_add, name="favorite-add"),
    path("<uuid:location_id>/remove/", favorite_views.favorite_remove, name="favorite-remove"),
]
