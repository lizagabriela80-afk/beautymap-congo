from django.urls import path
from . import views

urlpatterns = [
    path('login/',           views.login_view,       name='login'),
    path('register/',        views.register_view,    name='register'),
    path('logout/',          views.logout_view,       name='logout'),
    path('otp/send/',        views.send_otp_view,     name='send_otp'),
    path('otp/verify/',      views.verify_otp_view,   name='verify_otp'),
    path('profil/modifier/', views.profile_edit,      name='profile_edit'),
]