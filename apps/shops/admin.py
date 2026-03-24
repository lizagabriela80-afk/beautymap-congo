from django.contrib import admin
from .models import Shop, Service, Schedule, ShopPhoto, ShopPromotion

class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1

class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 0

class PhotoInline(admin.TabularInline):
    model = ShopPhoto
    extra = 1

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'quartier', 'owner', 'is_active', 'is_verified', 'is_featured', 'views_count', 'average_rating']
    list_filter = ['category', 'quartier', 'is_active', 'is_verified', 'is_featured']
    search_fields = ['name', 'description', 'owner__email']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ServiceInline, ScheduleInline, PhotoInline]
    list_editable = ['is_active', 'is_verified', 'is_featured']
    raw_id_fields = ['owner']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'shop', 'price', 'duration_minutes', 'is_active']
    list_filter = ['is_active', 'shop__category']
    search_fields = ['name', 'shop__name']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['shop', 'day', 'open_time', 'close_time', 'is_closed']
    list_filter = ['day', 'is_closed']
