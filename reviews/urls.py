from django.urls import path
from reviews.views import create_review, list_reviews, delete_review

urlpatterns = [
    path('workshops/<int:workshop_id>/reviews/', list_reviews),
    path('workshops/<int:workshop_id>/reviews/create/', create_review),
    path('reviews/<int:review_id>/delete/', delete_review),
]