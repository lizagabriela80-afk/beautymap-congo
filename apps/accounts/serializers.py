# apps/accounts/serializers.py
from rest_framework import serializers
from .models import User, ClientProfile, ProProfile


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    initials = serializers.CharField(source='get_initials', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'initials',
                  'phone', 'user_type', 'avatar', 'is_verified', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'is_verified']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
    shop_name = serializers.CharField(required=False, allow_blank=True)
    shop_category = serializers.CharField(required=False, allow_blank=True)
    shop_quartier = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name',
                  'phone', 'user_type', 'shop_name', 'shop_category', 'shop_quartier']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Les mots de passe ne correspondent pas.'})
        if data.get('user_type') == 'pro' and not data.get('shop_name'):
            raise serializers.ValidationError({'shop_name': 'Nom de boutique requis pour les pros.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        shop_name = validated_data.pop('shop_name', '')
        shop_category = validated_data.pop('shop_category', 'coiffure')
        shop_quartier = validated_data.pop('shop_quartier', 'bacongo')
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if user.user_type == 'client':
            ClientProfile.objects.create(user=user)
        elif user.user_type == 'pro':
            ProProfile.objects.create(user=user)
            from apps.shops.models import Shop
            Shop.objects.create(
                owner=user, name=shop_name, category=shop_category,
                quartier=shop_quartier, phone=user.phone,
                description=f"Bienvenue chez {shop_name}",
                address=f"{shop_quartier.title()}, Brazzaville"
            )
        return user


# apps/accounts/api_urls.py
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer, RegisterSerializer
from .models import User


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
        }, status=201)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except Exception:
            pass
        return Response({'success': True})
