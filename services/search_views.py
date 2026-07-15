from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
)
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import (
    WorkshopService,
)
from .search_serializer import WorkshopFindResponseSerializer, FindWorkshopRequestSerializer

from .utils import calculate_distance
@extend_schema(
    tags=["Search"],
    summary="Find nearest workshops by problem",
    description="""
User problem tanlaydi.

Backend:

Problem
↓

Service
↓

WorkshopService
↓

Workshop
↓

Distance
↓

Premium
↓

Rating

User problem ni tanlaydi kn beckend qaysi service turiga mos ekanligini topadi va 
shu servicni workshopservices ichidan qidirib javob qaytaradi.
    """,
    request=None,
    responses={
        200: WorkshopFindResponseSerializer(many=True),
        400: OpenApiResponse(description="Invalid request"),
        404: OpenApiResponse(description="Problem not found"),
    },
)
@api_view(["GET"])
def find_workshops(request):
    serializer = FindWorkshopRequestSerializer(
        data=request.query_params
    )

    serializer.is_valid(
        raise_exception=True
    )

    problem = serializer.validated_data["problem_id"]

    user_latitude = serializer.validated_data["latitude"]

    user_longitude = serializer.validated_data["longitude"]

    radius = serializer.validated_data["radius"]

    services = problem.services.all()

    if not services.exists():

        return Response(
            {
                "message": "Bu muammo uchun service topilmadi."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    workshop_services = (
        WorkshopService.objects
        .select_related(
            "workshop",
            "service",
        )
        .filter(
            service__in=services
        )
    )

    if not workshop_services.exists():

        return Response(
            {
                "message": "Mos workshop topilmadi."
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    workshops = {}

    for workshop_service in workshop_services:

        workshop = workshop_service.workshop

        # Latitude yoki longitude yo'q bo'lsa o'tkazib yuboramiz
        if (
            workshop.latitude is None
            or workshop.longitude is None
        ):
            continue

        distance = calculate_distance(
            user_latitude,
            user_longitude,
            workshop.latitude,
            workshop.longitude,
        )

        # Radiusdan tashqaridagilarni o'tkazib yuboramiz
        if distance > radius:
            continue

        workshop_id = str(workshop.id)

        if workshop_id not in workshops:

            workshops[workshop_id] = {
                "id": workshop.id,
                "name": workshop.name,
                "address": workshop.address,
                "phone": workshop.phone,
                "photo": workshop.photo,
                "premium": workshop.premium,
                "rating": workshop.rating,
                "rating_count": workshop.rating_count,
                "distance": round(distance, 2),
                "price": workshop_service.price,
                "matched_services": [
                    workshop_service.service.name
                ],
                "opening_time": workshop.opening_time,
                "closing_time": workshop.closing_time,
                "latitude": workshop.latitude,
                "longitude": workshop.longitude,
            }

        else:

            # Bir workshopda bir nechta mos service bo'lishi mumkin
            workshops[workshop_id]["matched_services"].append(
                workshop_service.service.name
            )

            # Eng arzon service narxini saqlaymiz
            if (
                workshop_service.price
                < workshops[workshop_id]["price"]
            ):
                workshops[workshop_id]["price"] = (
                    workshop_service.price
                )
    # Dictionary ni listga aylantiramiz
    results = list(workshops.values())

    # Radius ichida workshop topilmagan bo'lsa
    if not results:
        return Response(
            {
                "message": f"{radius} km radius ichida mos workshop topilmadi."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    # Sort:
    # 1. Premium
    # 2. Rating
    # 3. Distance
    # 4. Price

    results.sort(
        key=lambda workshop: (
            not workshop["premium"],          # Premium birinchi
            -workshop["rating"],              # Rating katta bo'lsa tepada
            workshop["distance"],             # Eng yaqin
            float(workshop["price"]),         # Eng arzon
        )
    )

    response_serializer = WorkshopFindResponseSerializer(
        results,
        many=True,
    )

    return Response(
        response_serializer.data,
        status=status.HTTP_200_OK,
    )
