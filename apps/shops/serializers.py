# apps/shops/serializers.py
from rest_framework import serializers
from .models import Shop, Service, Schedule, ShopPhoto, ShopPromotion
from django.db.models import Avg, Count, Q


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'duration_minutes', 'is_active', 'order']


class ScheduleSerializer(serializers.ModelSerializer):
    day_display = serializers.CharField(source='get_day_display', read_only=True)

    class Meta:
        model = Schedule
        fields = ['id', 'day', 'day_display', 'open_time', 'close_time', 'is_closed']


class ShopPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopPhoto
        fields = ['id', 'image', 'caption', 'is_cover', 'order']


class ShopListSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    is_open = serializers.BooleanField(read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    quartier_display = serializers.CharField(source='get_quartier_display', read_only=True)
    category_emoji = serializers.CharField(read_only=True)
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = [
            'id', 'name', 'slug', 'category', 'category_display', 'category_emoji',
            'quartier', 'quartier_display', 'city', 'address',
            'latitude', 'longitude', 'phone', 'whatsapp',
            'cover_image', 'is_verified', 'is_featured',
            'average_rating', 'review_count', 'is_open', 'min_price',
            'views_count', 'created_at',
        ]

    def get_average_rating(self, obj):
        result = obj.reviews.filter(is_approved=True).aggregate(avg=Avg('rating'))
        return round(result['avg'] or 0, 1)

    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()

    def get_min_price(self, obj):
        svc = obj.services.filter(is_active=True).order_by('price').first()
        return int(svc.price) if svc else None


class ShopDetailSerializer(ShopListSerializer):
    services = ServiceSerializer(many=True, read_only=True)
    schedules = ScheduleSerializer(many=True, read_only=True)
    photos = ShopPhotoSerializer(many=True, read_only=True)

    class Meta(ShopListSerializer.Meta):
        fields = ShopListSerializer.Meta.fields + [
            'description', 'email', 'website', 'logo',
            'services', 'schedules', 'photos',
        ]


class ShopCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = [
            'name', 'category', 'description', 'address', 'quartier',
            'phone', 'whatsapp', 'email', 'website', 'latitude', 'longitude',
            'cover_image', 'logo',
        ]

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)
