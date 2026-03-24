from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['client', 'shop', 'rating', 'title', 'is_approved', 'is_featured', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_featured']
    search_fields = ['client__email', 'shop__name', 'comment']
    list_editable = ['is_approved', 'is_featured']
    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "✅ Approuver les avis sélectionnés"

    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    reject_reviews.short_description = "❌ Rejeter les avis sélectionnés"
