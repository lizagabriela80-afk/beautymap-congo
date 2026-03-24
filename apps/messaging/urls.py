# apps/messaging/urls.py
from django.urls import path
from . import views
urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('demarrer/<slug:shop_slug>/', views.start_conversation, name='start_conversation'),
    path('<uuid:conv_id>/envoyer/', views.send_message, name='send_message'),
]
