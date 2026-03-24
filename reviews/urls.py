from django.urls import path
from reviews.views import create_review, list_reviews

urlpatterns = [
    path('workshops/<int:workshop_id>/reviews/', create_review, name='create-review'),
    path('workshops/<int:workshop_id>/reviews/list/', list_reviews, name='list-reviews'),
]
