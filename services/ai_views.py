from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .ai_serializers import AIRequestSerializer, AISearchResponseSerializer
from .ai_search import AISearchService


@extend_schema(
    tags=["Search"],
    request=AIRequestSerializer,
    responses=AISearchResponseSerializer,
    summary="AI semantic search",
    description="Accepts a user query/prompt, extracts intent with AI, then searches workshops from the database.",
)
@api_view(["POST"])
def ai_search_view(request):
    serializer = AIRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    query = serializer.validated_data["query"].strip()

    service = AISearchService()
    try:
        response = service.search(query)
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    resp_serializer = AISearchResponseSerializer(response)
    return Response(resp_serializer.data)
