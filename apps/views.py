from django.http import JsonResponse
from .serializer import WorkshopSerializer, ReviewSerializer
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Workshop
from rapidfuzz import fuzz
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




@api_view(['GET'])
def workshop_list(request):
    """
    GET request bilan barcha ustaxonalarni olish va fuzzy filterlash:
    ?location=Mirobot&services=diagnostika&min_rating=3
    """
    workshops = Workshop.objects.all()

    # Location filter (fuzzy)
    location_query = request.GET.get('location')
    if location_query:
        workshops = [
            ws for ws in workshops
            if fuzz.partial_ratio(location_query.lower(), ws.location.lower()) > 80
        ]

    # Services filter (fuzzy)
    services_query = request.GET.get('services')
    if services_query:
        workshops = [
            ws for ws in workshops
            if fuzz.partial_ratio(services_query.lower(), ws.services.lower()) > 80
        ]

    # Minimum rating filter
    min_rating = request.GET.get('min_rating')
    if min_rating:
        try:
            min_rating = float(min_rating)
            workshops = [ws for ws in workshops if ws.rating >= min_rating]
        except ValueError:
            pass

    serializer = WorkshopSerializer(workshops, many=True)
    return Response(serializer.data)




# Review Create
class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer