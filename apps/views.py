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



# ----------------GET id bilan-------------------
class WorkshopDetailView(generics.RetrieveAPIView):
    queryset = Workshop.objects.all()
    serializer_class = WorkshopSerializer


# -------------------POST--------------------
class WorkshopCreateView(generics.CreateAPIView):
    queryset = Workshop.objects.all()
    serializer_class = WorkshopSerializer



# --------------GET+SEARCH---------------
@api_view(['GET'])
def workshop_list(request):
    from fuzzywuzzy import fuzz

    # ORMdan tartiblangan QuerySet → list
    workshops = list(Workshop.objects.all().order_by('-premium', '-rating'))

    # General q
    q = request.GET.get('q')
    if q:
        workshops = [ws for ws in workshops if fuzz.partial_ratio(q.lower(), ws.services.lower()) > 80]

    # Location
    location_query = request.GET.get('location')
    if location_query:
        workshops = [ws for ws in workshops if fuzz.partial_ratio(location_query.lower(), ws.location.lower()) > 80]

    # Services
    services_query = request.GET.get('services')
    if services_query:
        workshops = [ws for ws in workshops if fuzz.partial_ratio(services_query.lower(), ws.services.lower()) > 80]

    # Minimum rating
    min_rating = request.GET.get('min_rating')
    if min_rating:
        try:
            min_rating = float(min_rating)
            workshops = [ws for ws in workshops if ws.rating >= min_rating]
        except ValueError:
            pass

    serializer = WorkshopSerializer(workshops, many=True)
    return Response(serializer.data)