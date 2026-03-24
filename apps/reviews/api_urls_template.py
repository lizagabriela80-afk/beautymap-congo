# Stub api_urls for reviews, messaging, notifications, payments

# reviews/api_urls.py -> same file used for multiple
REVIEWS_URLS = """
from django.urls import path
from rest_framework import serializers, generics, permissions
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    stars = serializers.CharField(source='stars_display', read_only=True)
    class Meta:
        model = Review
        fields = ['id','shop','client_name','rating','stars','title','comment',
                  'owner_reply','created_at','is_approved']

class ReviewListCreate(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    def get_queryset(self):
        shop = self.request.query_params.get('shop')
        qs = Review.objects.filter(is_approved=True)
        if shop: qs = qs.filter(shop=shop)
        return qs
    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

urlpatterns = [path('', ReviewListCreate.as_view(), name='api_reviews')]
"""
