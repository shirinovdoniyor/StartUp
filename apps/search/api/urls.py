from django.urls import path

from . import views

urlpatterns = [
    path("nearby/", views.nearby, name="search-nearby"),
    path("ai/", views.ai_search, name="search-ai"),
]
