# apps/shops/urls.py — VERSION COMPLÈTE
from django.urls import path
from . import views

app_name = 'shops'

urlpatterns = [
    # Pages publiques
    path('',                                    views.home,             name='home'),
    path('explorer/',                           views.explore,          name='explore'),
    path('carte/',                              views.map_view,         name='map'),
    path('boutique/<slug:slug>/',               views.shop_detail,      name='detail'),
    path('pros/',                               views.pros_page,        name='pros'),
    path('contact/',                            views.contact_page,     name='contact'),

    # Actions authentifiées
    path('boutique/<uuid:shop_id>/favori/',     views.toggle_favorite,  name='toggle_favorite'),
    path('creer-ma-boutique/',                  views.create_shop,      name='create_shop'),

    # API JSON (pour JS frontend)
    path('api/map-data/',                       views.map_data_api,     name='map_data'),
    path('api/search/',                         views.api_search,       name='api_search'),
]
