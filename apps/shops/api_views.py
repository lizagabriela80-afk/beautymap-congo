# apps/shops/api_views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Q
from .models import Shop, Service, Schedule, ShopPhoto
from .serializers import ShopListSerializer, ShopDetailSerializer, ShopCreateSerializer, ServiceSerializer, ScheduleSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        shop = obj if isinstance(obj, Shop) else obj.shop
        return shop.owner == request.user


class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'quartier', 'is_verified', 'is_featured']
    search_fields = ['name', 'description', 'address', 'services__name']
    ordering_fields = ['created_at', 'views_count', 'name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ShopListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ShopCreateSerializer
        return ShopDetailSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrReadOnly()]
        return [permissions.AllowAny()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Shop.objects.filter(pk=instance.pk).update(views_count=instance.views_count + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_shops(self, request):
        """Return authenticated pro's shops"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentification requise'}, status=401)
        shops = Shop.objects.filter(owner=request.user)
        serializer = ShopDetailSerializer(shops, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_favorite(self, request, pk=None):
        shop = self.get_object()
        if not hasattr(request.user, 'client_profile'):
            return Response({'error': 'Profil client requis'}, status=403)
        profile = request.user.client_profile
        if profile.favorites.filter(pk=shop.pk).exists():
            profile.favorites.remove(shop)
            return Response({'is_favorite': False})
        profile.favorites.add(shop)
        return Response({'is_favorite': True})

    @action(detail=True, methods=['get'])
    def available_slots(self, request, pk=None):
        from apps.bookings.views import get_available_slots
        return get_available_slots(request)

    @action(detail=False, methods=['get'])
    def map_markers(self, request):
        """Optimized endpoint for map markers"""
        shops = Shop.objects.filter(is_active=True, latitude__isnull=False).annotate(
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
        )
        category = request.query_params.get('category', '')
        if category:
            shops = shops.filter(category=category)

        data = [{
            'id': str(s.id), 'name': s.name, 'slug': s.slug,
            'category': s.category, 'category_emoji': s.category_emoji,
            'quartier': s.get_quartier_display(),
            'lat': float(s.latitude), 'lng': float(s.longitude),
            'rating': float(s.avg_rating or 0), 'phone': s.phone,
            'is_open': s.is_open,
        } for s in shops]
        return Response({'shops': data})


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return Service.objects.filter(shop__owner=self.request.user, is_active=True)

    def perform_create(self, serializer):
        shop_id = self.request.data.get('shop')
        shop = Shop.objects.get(pk=shop_id, owner=self.request.user)
        serializer.save(shop=shop)
