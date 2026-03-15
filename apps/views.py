from django.http import JsonResponse
from rest_framework.decorators import api_view


@api_view(['GET'])
def hello_world_api_view(request):
    return JsonResponse({"message": "helloworld"})