from apps.common.permissions import ReadOnlyOrSuperAdmin
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Category, Service
from ..selectors import list_categories, list_services
from ..serializers import ServiceAliasSerializer, CategorySerializer, ServiceSerializer


@extend_schema_view(list=extend_schema(tags=["Catalog"]), retrieve=extend_schema(tags=["Catalog"]))
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrSuperAdmin]
    queryset = Category.objects.all()

    def get_queryset(self):
        return list_categories()


@extend_schema_view(list=extend_schema(tags=["Catalog"]), retrieve=extend_schema(tags=["Catalog"]))
class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [ReadOnlyOrSuperAdmin]
    queryset = Service.objects.all()

    def get_queryset(self):
        return list_services(
            category_id=self.request.query_params.get("category"),
            search=self.request.query_params.get("search", ""),
        )

    @extend_schema(tags=["Catalog"], request=ServiceAliasSerializer, responses=ServiceAliasSerializer)
    @action(detail=True, methods=["post"], url_path="aliases")
    def add_alias(self, request, pk=None):
        service = self.get_object()
        serializer = ServiceAliasSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(service=service)
        return Response(serializer.data, status=201)
