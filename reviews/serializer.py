from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        # workshopni read-only qilib qo‘ymaymiz, POSTda serializer orqali belgilaymiz
        fields = ['id', 'user_name', 'rating', 'comment', 'workshop']
        # workshopni POSTda tashqi data  orqali belgilash uchun required=True bo‘lishi kerak