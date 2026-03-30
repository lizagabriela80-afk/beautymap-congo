# apps/shops/urls.py — VERSION FINALE NETTOYÉE
from django.urls import path
from . import views

app_name = 'shops'

urlpatterns = [
    # ── Pages publiques ─────────────────────────────────────────────
    path('',                                    views.home,             name='home'),
    path('explorer/',                           views.explore,          name='explore'),
    path('decouverte/',                         views.feed_view,        name='feed'),
    path('carte/',                              views.map_view,         name='map'),
    path('boutique/<slug:slug>/',               views.shop_detail,      name='detail'),
    path('pros/',                               views.pros_page,        name='pros'),
    path('contact/',                            views.contact_page,     name='contact'),

    # ── Actions ─────────────────────────────────────────────────────
    path('boutique/<uuid:shop_id>/favori/',     views.toggle_favorite,  name='toggle_favorite'),
    path('creer-ma-boutique/',                  views.create_shop,      name='create_shop'),

    # ── Publications ────────────────────────────────────────────────
    path('boutique/<slug:shop_slug>/publier/',  views.create_post,      name='create_post'),
    path('boutique/<slug:shop_slug>/posts/',    views.shop_posts_api,   name='shop_posts_api'),
    path('post/<uuid:post_id>/like/',           views.like_post,        name='like_post'),
    path('post/<uuid:post_id>/supprimer/',      views.delete_post,      name='delete_post'),

    # ── API JSON ─────────────────────────────────────────────────────
    path('api/map-data/',                       views.map_data_api,     name='map_data'),
    path('api/search/',                         views.api_search,       name='api_search'),
]