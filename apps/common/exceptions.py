"""Centralised DRF exception handling and domain exceptions."""

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


class ApplicationError(APIException):
    """Base class for business-rule violations raised from the service layer."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A business rule was violated."
    default_code = "application_error"


class NotFoundError(ApplicationError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found."
    default_code = "not_found"


class PermissionError(ApplicationError):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have permission to perform this action."
    default_code = "permission_denied"


def api_exception_handler(exc, context):
    """Wrap DRF's handler and translate common Django exceptions."""
    if isinstance(exc, ObjectDoesNotExist):
        exc = NotFoundError()
    elif isinstance(exc, DjangoPermissionDenied):
        exc = PermissionError()
    elif isinstance(exc, DjangoValidationError):
        exc = ApplicationError(detail=getattr(exc, "messages", str(exc)))

    response = drf_exception_handler(exc, context)
    if response is None:
        return response

    detail = response.data
    payload = {
        "error": {
            "code": getattr(exc, "default_code", "error"),
            "detail": detail,
        }
    }
    return Response(payload, status=response.status_code, headers=response.headers)
