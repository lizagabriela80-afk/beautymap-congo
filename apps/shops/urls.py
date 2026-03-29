# apps/shops/urls.py — VERSION FINALE avec Publications + Feed
from django.urls import path
from . import views

app_name = 'shops'

urlpatterns = [
    # ── Pages publiques ──────────────────────────────────────
    path('',                                    views.home,             name='home'),
    path('explorer/',                           views.explore,          name='explore'),
    path('decouverte/',                         views.feed_view,        name='feed'),      # ← page Découverte
    path('carte/',                              views.map_view,         name='map'),
    path('boutique/<slug:slug>/',               views.shop_detail,      name='detail'),
    path('pros/',                               views.pros_page,        name='pros'),
    path('contact/',                            views.contact_page,     name='contact'),

    # ── Actions boutique ─────────────────────────────────────
    path('boutique/<uuid:shop_id>/favori/',     views.toggle_favorite,  name='toggle_favorite'),
    path('creer-ma-boutique/',                  views.create_shop,      name='create_shop'),

    # ── Publications ─────────────────────────────────────────
    path('boutique/<slug:shop_slug>/publier/',  views.create_post,      name='create_post'),   # créer
    path('boutique/<slug:shop_slug>/posts/',    views.shop_posts_api,   name='shop_posts_api'),# liste JSON
    path('post/<uuid:post_id>/like/',           views.like_post,        name='like_post'),     # liker
    path('post/<uuid:post_id>/supprimer/',      views.delete_post,      name='delete_post'),   # supprimer

    # ── API JSON ─────────────────────────────────────────────
    path('api/map-data/',                       views.map_data_api,     name='map_data'),
    path('api/search/',                         views.api_search,       name='api_search'),
]
