# apps/shops/urls.py
from django.urls import path
from . import views

app_name = 'shops'
urlpatterns = [
    path('', views.home, name='home'),
    path('explorer/', views.explore, name='explore'),
    path('carte/', views.map_view, name='map'),
    path('boutique/<slug:slug>/', views.shop_detail, name='detail'),
    path('boutique/<uuid:shop_id>/favori/', views.toggle_favorite, name='toggle_favorite'),
    path('api/map-data/', views.map_data_api, name='map_data'),
    path('creer-ma-boutique/',            views.create_shop,     name='create_shop'),
    path('pros/', views.pros_page, name='pros'),
]


