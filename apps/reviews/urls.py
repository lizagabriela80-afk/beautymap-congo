# apps/reviews/urls.py
from django.urls import path
from . import views
urlpatterns = [
    path('boutique/<slug:shop_slug>/avis/', views.submit_review, name='submit_review'),
    path('<int:review_id>/repondre/', views.owner_reply, name='owner_reply'),
]
