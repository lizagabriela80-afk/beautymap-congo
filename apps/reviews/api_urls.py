# ═══════════════════════════════════════════════════════════════
#  apps/reviews/api_urls.py  — API Avis (mobile)
# ═══════════════════════════════════════════════════════════════
from django.urls import path
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from django.utils import timezone
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    author_name     = serializers.CharField(source='client.get_full_name', read_only=True)
    author_initials = serializers.CharField(source='client.get_initials',  read_only=True)
    stars           = serializers.SerializerMethodField()
    shop_name       = serializers.CharField(source='shop.name', read_only=True)
    shop_slug       = serializers.CharField(source='shop.slug', read_only=True)

    class Meta:
        model  = Review
        fields = [
            'id', 'shop', 'shop_name', 'shop_slug',
            'author_name', 'author_initials',
            'rating', 'title', 'comment', 'stars',
            'is_approved', 'owner_reply', 'owner_reply_at',
            'created_at',
        ]
        read_only_fields = ['id', 'is_approved', 'owner_reply', 'owner_reply_at', 'created_at']

    def get_stars(self, obj):
        return '★' * obj.rating + '☆' * (5 - obj.rating)


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Review
        fields = ['shop', 'rating', 'title', 'comment']

    def validate_rating(self, v):
        if not 1 <= v <= 5:
            raise serializers.ValidationError("La note doit être entre 1 et 5.")
        return v

    def validate(self, data):
        user = self.context['request'].user
        if Review.objects.filter(client=user, shop=data['shop']).exists():
            raise serializers.ValidationError("Vous avez déjà laissé un avis pour ce salon.")
        return data

    def create(self, validated_data):
        return Review.objects.create(client=self.context['request'].user, **validated_data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    GET    /api/v1/reviews/               → Mes avis (client) ou avis de mes salons (pro)
    POST   /api/v1/reviews/               → Soumettre un avis
    GET    /api/v1/reviews/{id}/          → Détail d'un avis
    POST   /api/v1/reviews/{id}/reply/    → Répondre (pro uniquement)
    GET    /api/v1/reviews/shop/{slug}/   → Avis d'un salon (public)
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        return ReviewCreateSerializer if self.action == 'create' else ReviewSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Review.objects.filter(is_approved=True)
        if user.is_pro:
            return Review.objects.filter(shop__owner=user).select_related('client', 'shop')
        return Review.objects.filter(client=user).select_related('shop')

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reply(self, request, pk=None):
        review = self.get_object()
        if review.shop.owner != request.user:
            return Response({'error': 'Non autorisé.'}, status=403)
        reply_text = request.data.get('reply', '').strip()
        if not reply_text:
            return Response({'error': 'La réponse est requise.'}, status=400)
        review.owner_reply    = reply_text
        review.owner_reply_at = timezone.now()
        review.save(update_fields=['owner_reply', 'owner_reply_at'])
        return Response(ReviewSerializer(review).data)

    @action(detail=False, methods=['get'], url_path='shop/(?P<slug>[^/.]+)',
            permission_classes=[permissions.AllowAny])
    def by_shop(self, request, slug=None):
        from apps.shops.models import Shop
        from django.shortcuts import get_object_or_404
        shop    = get_object_or_404(Shop, slug=slug)
        reviews = Review.objects.filter(shop=shop, is_approved=True).select_related('client')
        serializer = ReviewSerializer(reviews, many=True)
        return Response({'count': reviews.count(), 'results': serializer.data})


_router = DefaultRouter()
_router.register(r'', ReviewViewSet, basename='review')
from django.urls import include
urlpatterns = [path('', include(_router.urls))]
