# ═══════════════════════════════════════════════════════════════
#  apps/accounts/api_urls.py  — API Auth (mobile)
# ═══════════════════════════════════════════════════════════════
from django.urls import path
from rest_framework import generics, permissions, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User, OTPCode, ClientProfile, ProProfile
from .serializers import UserSerializer, RegisterSerializer


# ─── Serializers supplémentaires ────────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['email'].lower(), password=data['password'])
        if not user:
            raise serializers.ValidationError("Email ou mot de passe incorrect.")
        if not user.is_active:
            raise serializers.ValidationError("Ce compte est désactivé.")
        data['user'] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password     = serializers.CharField(write_only=True)
    new_password     = serializers.CharField(write_only=True, min_length=8)
    new_password2    = serializers.CharField(write_only=True)

    def validate_old_password(self, v):
        if not self.context['request'].user.check_password(v):
            raise serializers.ValidationError("Ancien mot de passe incorrect.")
        return v

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': 'Les mots de passe ne correspondent pas.'})
        return data


class OTPSendSerializer(serializers.Serializer):
    phone   = serializers.CharField(required=False, allow_blank=True)
    email   = serializers.EmailField(required=False, allow_null=True)
    purpose = serializers.ChoiceField(choices=['login', 'verify', 'reset'], default='verify')

    def validate(self, data):
        if not data.get('phone') and not data.get('email'):
            raise serializers.ValidationError("Un téléphone ou un email est requis.")
        return data


class OTPVerifySerializer(serializers.Serializer):
    code    = serializers.CharField(min_length=6, max_length=6)
    phone   = serializers.CharField(required=False, allow_blank=True)
    email   = serializers.EmailField(required=False, allow_null=True)
    purpose = serializers.CharField(default='verify')


# ─── Vues ────────────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """POST /api/v1/auth/register/"""
    serializer_class   = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        user  = s.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user':  UserSerializer(user, context={'request': request}).data,
            'message': f"Bienvenue {user.first_name} ! Votre compte a été créé.",
        }, status=201)


class LoginView(APIView):
    """POST /api/v1/auth/login/"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        return Response({
            'token': token.key,
            'user':  UserSerializer(user, context={'request': request}).data,
        })


class LogoutView(APIView):
    """POST /api/v1/auth/logout/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except Exception:
            pass
        return Response({'message': 'Déconnexion réussie.'})


class MeView(generics.RetrieveUpdateAPIView):
    """GET / PATCH /api/v1/auth/me/"""
    serializer_class   = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class ChangePasswordView(APIView):
    """POST /api/v1/auth/change-password/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        s = ChangePasswordSerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)
        request.user.set_password(s.validated_data['new_password'])
        request.user.save()
        # Révoquer l'ancien token et en créer un nouveau
        try:
            request.user.auth_token.delete()
        except Exception:
            pass
        token, _ = Token.objects.get_or_create(user=request.user)
        return Response({'token': token.key, 'message': 'Mot de passe mis à jour.'})


class DeleteAccountView(APIView):
    """DELETE /api/v1/auth/delete-account/"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        try:
            user.auth_token.delete()
        except Exception:
            pass
        user.is_active = False
        user.email     = f"deleted_{user.pk}_{user.email}"
        user.save(update_fields=['is_active', 'email'])
        return Response({'message': 'Votre compte a été supprimé.'})


class OTPSendView(APIView):
    """POST /api/v1/auth/otp/send/"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from datetime import timedelta
        s = OTPSendSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d       = s.validated_data
        expires = timezone.now() + timedelta(minutes=10)

        # Invalider les anciens OTP
        OTPCode.objects.filter(
            phone=d.get('phone', ''), is_used=False
        ).update(is_used=True)

        from .otp_service import generate_code, send_otp
        code = generate_code(6)
        OTPCode.objects.create(
            phone=d.get('phone', ''), email=d.get('email'),
            code=code, purpose=d['purpose'], expires_at=expires
        )

        # Envoi SMS
        if d.get('phone'):
            send_otp(d['phone'], code)

        resp = {'message': 'Code OTP envoyé.', 'expires_in_minutes': 10}
        if request.user.is_authenticated and request.user.is_staff:
            resp['debug_code'] = code  # Admins uniquement
        from django.conf import settings
        if settings.DEBUG:
            resp['debug_code'] = code
        return Response(resp)


class OTPVerifyView(APIView):
    """POST /api/v1/auth/otp/verify/"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = OTPVerifySerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        filters = {'code': d['code'], 'purpose': d['purpose'], 'is_used': False}
        if d.get('phone'): filters['phone'] = d['phone']
        if d.get('email'): filters['email'] = d['email']

        otp = OTPCode.objects.filter(**filters).order_by('-created_at').first()
        if not otp or not otp.is_valid():
            return Response({'error': 'Code OTP invalide ou expiré.'}, status=400)

        otp.is_used = True
        otp.save()

        # Connecter l'utilisateur si son compte existe
        user = None
        if d.get('phone'):
            user = User.objects.filter(phone=d['phone'], is_active=True).first()
        if d.get('email'):
            user = User.objects.filter(email=d['email'], is_active=True).first()

        resp = {'verified': True, 'message': 'Code vérifié avec succès.'}
        if user:
            user.is_verified = True
            user.save(update_fields=['is_verified'])
            token, _ = Token.objects.get_or_create(user=user)
            resp['token'] = token.key
            resp['user']  = UserSerializer(user, context={'request': request}).data

        return Response(resp)


class PublicUserProfileView(APIView):
    """GET /api/v1/auth/users/{id}/profile/"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        from django.shortcuts import get_object_or_404
        user = get_object_or_404(User, pk=pk, is_active=True)
        return Response({
            'id':        user.pk,
            'full_name': user.get_full_name(),
            'initials':  user.get_initials(),
            'avatar':    request.build_absolute_uri(user.avatar.url) if user.avatar else None,
            'user_type': user.user_type,
        })


class HealthCheckView(APIView):
    """GET /api/v1/health/"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            'status':    'ok',
            'service':   'BeautyMap Congo API',
            'version':   'v1',
            'timestamp': timezone.now().isoformat(),
        })


# ─── URL patterns ─────────────────────────────────────────────────────────────
urlpatterns = [
    path('register/',        RegisterView.as_view(),      name='api-register'),
    path('login/',           LoginView.as_view(),         name='api-login'),
    path('logout/',          LogoutView.as_view(),        name='api-logout'),
    path('me/',              MeView.as_view(),            name='api-me'),
    path('change-password/', ChangePasswordView.as_view(),name='api-change-password'),
    path('delete-account/',  DeleteAccountView.as_view(), name='api-delete-account'),
    path('otp/send/',        OTPSendView.as_view(),       name='api-otp-send'),
    path('otp/verify/',      OTPVerifyView.as_view(),     name='api-otp-verify'),
    path('users/<int:pk>/profile/', PublicUserProfileView.as_view(), name='api-user-profile'),
]
