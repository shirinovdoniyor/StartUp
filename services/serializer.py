from decimal import Decimal

from rest_framework import serializers

from apps.models import Workshop

from .models import WorkshopService, Problem, Service


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProblemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['name', 'description']

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Problem nomi majburiy.')
        if Problem.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError('Bu nom allaqachon mavjud.')
        return value


class ProblemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['name', 'description']
        partial = True

    def validate_name(self, value):
        if value:
            value = value.strip()
            if not value:
                raise serializers.ValidationError('Problem nomi majburiy.')
            # Check if name exists (excluding current instance)
            if Problem.objects.filter(name__iexact=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError('Bu nom allaqachon mavjud.')
        return value

class WorkshopServiceSerializer(serializers.ModelSerializer):
    workshop_name = serializers.CharField(source="workshop.name", read_only=True)
    service_name = serializers.CharField(source="service.name", read_only=True)
    location = serializers.CharField(source="workshop.address", read_only=True)
    rating = serializers.FloatField(source="workshop.rating", read_only=True)
    premium = serializers.BooleanField(source="workshop.premium", read_only=True)

    class Meta:
        model = WorkshopService
        fields = [
            "id",
            "workshop",
            "workshop_name",
            "service",
            "service_name",
            "location",
            "price",
            "rating",
            "premium",
        ]



class WorkshopServiceCreateSerializer(serializers.ModelSerializer):

    workshop = serializers.PrimaryKeyRelatedField(
        queryset=Workshop.objects.all()
    )

    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all()
    )

    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    class Meta:
        model = WorkshopService
        fields = [
            "id",
            "workshop",
            "service",
            "price",
        ]

    def validate(self, attrs):

        workshop = attrs["workshop"]
        service = attrs["service"]

        if WorkshopService.objects.filter(
            workshop=workshop,
            service=service,
        ).exists():

            raise serializers.ValidationError(
                "Bu service ushbu workshopga oldin qo'shilgan."
            )

        return attrs




class WorkshopServiceCreateResponseSerializer(serializers.ModelSerializer):

    workshop_name = serializers.CharField(
        source="workshop.name",
        read_only=True,
    )

    service_name = serializers.CharField(
        source="service.name",
        read_only=True,
    )

    class Meta:
        model = WorkshopService
        fields = [
            "id",
            "workshop_name",
            "service_name",
            "price",
        ]

class WorkshopServiceUpdateSerializer(serializers.ModelSerializer):

    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all()
    )

    class Meta:
        model = WorkshopService
        fields = [
            "service",
            "price",
        ]

    def validate(self, attrs):

        workshop = self.instance.workshop
        service = attrs.get("service", self.instance.service)

        if WorkshopService.objects.filter(
            workshop=workshop,
            service=service,
        ).exclude(id=self.instance.id).exists():

            raise serializers.ValidationError(
                "Bu service ushbu workshopga oldin qo'shilgan."
            )

        return attrs

from rest_framework import serializers
from .models import Service, Problem


class ServiceSerializer(serializers.ModelSerializer):
    problems = serializers.PrimaryKeyRelatedField(
        queryset=Problem.objects.all(),
        many=True,
    )

    problem_names = serializers.StringRelatedField(
        source="problems",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "description",
            "problems",
            "problem_names",
            "created_at",
            "updated_at",
        ]