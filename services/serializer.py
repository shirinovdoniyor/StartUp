from decimal import Decimal

from rest_framework import serializers

from apps.models import Workshop

from .models import WorkshopService


class WorkshopServiceSerializer(serializers.ModelSerializer):
    workshop_name = serializers.CharField(source='workshop.name', read_only=True)
    location = serializers.CharField(source='workshop.address', read_only=True)
    rating = serializers.FloatField(source='workshop.rating', read_only=True)
    premium = serializers.BooleanField(source='workshop.premium', read_only=True)

    class Meta:
        model = WorkshopService
        fields = [
            'id',
            'workshop_name',
            'service_name',
            'location',
            'price',
            'rating',
            'premium',
        ]


class WorkshopServiceCreateSerializer(serializers.ModelSerializer):
    workshop = serializers.PrimaryKeyRelatedField(queryset=Workshop.objects.all())
    service_name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))

    class Meta:
        model = WorkshopService
        fields = ['id', 'workshop', 'service_name', 'price']

    def validate_service_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Service nomi majburiy.')
        return value

    def validate(self, attrs):
        workshop = attrs.get('workshop')
        service_name = attrs.get('service_name')

        if WorkshopService.objects.filter(workshop=workshop, service_name__iexact=service_name).exists():
            raise serializers.ValidationError('Bu service ushbu workshopga oldin qo\'shilgan.')

        return attrs

    def create(self, validated_data):
        return WorkshopService.objects.create(**validated_data)


class WorkshopServiceCreateResponseSerializer(serializers.ModelSerializer):
    workshop_name = serializers.CharField(source='workshop.name', read_only=True)

    class Meta:
        model = WorkshopService
        fields = ['id', 'workshop_name', 'service_name', 'price']


class WorkshopServiceUpdateSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))

    class Meta:
        model = WorkshopService
        fields = ['id', 'service_name', 'price']

    def validate_service_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Service nomi majburiy.')
        return value

    def validate(self, attrs):
        return attrs

    def update(self, instance, validated_data):
        service_name = validated_data.pop('service_name', instance.service_name)
        instance.service_name = service_name
        instance.price = validated_data.get('price', instance.price)
        instance.save()
        return instance
