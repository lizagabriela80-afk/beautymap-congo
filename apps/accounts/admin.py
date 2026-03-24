from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPCode, ClientProfile, ProProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'get_full_name', 'user_type', 'is_active', 'is_verified', 'date_joined']
    list_filter = ['user_type', 'is_active', 'is_verified']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Infos', {'fields': ('first_name', 'last_name', 'phone', 'avatar')}),
        ('Statut', {'fields': ('user_type', 'is_active', 'is_verified', 'is_staff', 'is_superuser')}),
        ('Dates', {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = ((None, {'classes': ('wide',), 'fields': ('email','first_name','last_name','user_type','password1','password2')}),)
    readonly_fields = ['date_joined', 'last_login']

@admin.register(OTPCode)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['phone', 'email', 'code', 'purpose', 'is_used', 'created_at']
    list_filter = ['purpose', 'is_used']

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'created_at']

@admin.register(ProProfile)
class ProProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscription', 'subscription_expires']
    list_filter = ['subscription']
