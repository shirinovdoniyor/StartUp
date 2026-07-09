from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import Problem
from .serializer import (
    ProblemSerializer,
    ProblemCreateSerializer,
    ProblemUpdateSerializer,
)


# ==========================================================
# LIST PROBLEMS
# ==========================================================

@extend_schema(
    tags=["Problems"],
    summary="Problems List",
    responses=ProblemSerializer(many=True),
)
@api_view(["GET"])
def problem_list(request):

    problems = Problem.objects.all()

    serializer = ProblemSerializer(
        problems,
        many=True,
    )

    return Response(serializer.data)


# ==========================================================
# DETAIL
# ==========================================================

@extend_schema(
    tags=["Problems"],
    summary="Problem Detail",
    responses=ProblemSerializer,
)
@api_view(["GET"])
def problem_detail(request, id):

    try:
        problem = Problem.objects.get(id=id)

    except Problem.DoesNotExist:
        return Response(
            {
                "error": "Problem topilmadi."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = ProblemSerializer(problem)

    return Response(serializer.data)


# ==========================================================
# CREATE
# ==========================================================

@extend_schema(
    tags=["Problems"],
    summary="Create Problem",
    request=ProblemCreateSerializer,
    responses=ProblemSerializer,
)
@api_view(["POST"])
@permission_classes([IsAdminUser])
def problem_create(request):

    serializer = ProblemCreateSerializer(
        data=request.data
    )

    if serializer.is_valid():

        problem = serializer.save()

        return Response(
            ProblemSerializer(problem).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


# ==========================================================
# UPDATE
# ==========================================================

@extend_schema(
    tags=["Problems"],
    summary="Update Problem",
    request=ProblemUpdateSerializer,
    responses=ProblemSerializer,
)
@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def problem_update(request, id):

    try:
        problem = Problem.objects.get(id=id)

    except Problem.DoesNotExist:
        return Response(
            {
                "error": "Problem topilmadi."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = ProblemUpdateSerializer(
        problem,
        data=request.data,
        partial=True,
    )

    if serializer.is_valid():

        problem = serializer.save()

        return Response(
            ProblemSerializer(problem).data,
            status=status.HTTP_200_OK,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


# ==========================================================
# DELETE
# ==========================================================

@extend_schema(
    tags=["Problems"],
    summary="Delete Problem",
)
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def problem_delete(request, id):

    try:
        problem = Problem.objects.get(id=id)

    except Problem.DoesNotExist:
        return Response(
            {
                "error": "Problem topilmadi."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    problem.delete()

    return Response(
        {
            "message": "Problem muvaffaqiyatli o'chirildi."
        },
        status=status.HTTP_204_NO_CONTENT,
    )