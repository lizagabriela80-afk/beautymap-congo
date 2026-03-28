# apps/notifications/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',                        views.notifications_list, name='notifications'),
    path('json/',                   views.list_notifs_json,   name='notifications_json'),
    path('<uuid:notif_id>/lue/',    views.mark_read,          name='mark_read'),
    path('tout-lire/',              views.mark_all_read,      name='mark_all_read'),
]
