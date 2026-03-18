from rest_framework import generics

from apps.serializer import ReviewSerializer

# Review Create
class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer