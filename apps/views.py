from django.http import JsonResponse
from rest_framework.decorators import api_view

from .serializer import WorkshopSerializer, ReviewSerializer
from rest_framework import generics
from apps.models import Workshop

@api_view(['GET'])
def hello_world_api_view(request):
    return JsonResponse({"message": "helloworld"})



# Workshop create API
class WorkshopCreateView(generics.CreateAPIView):
    queryset = Workshop.objects.all()
    serializer_class = WorkshopSerializer

# Workshop List + Search
class WorkshopListView(generics.ListAPIView):
    serializer_class = WorkshopSerializer

    def get_queryset(self):
        queryset = Workshop.objects.all()
        q = self.request.GET.get('q', None)
        if q:
            queryset = queryset.filter(services__icontains=q)
        return queryset


# Workshop Detail
class WorkshopDetailView(generics.RetrieveAPIView):
    queryset = Workshop.objects.all()
    serializer_class = WorkshopSerializer


# Review Create
class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer