"""Accounts Models — BeautyMap Congo"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import random, string


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email requis')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPES = [
        ('client', 'Client'),
        ('pro', 'Professionnel'),
        ('admin', 'Administrateur'),
    ]

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='client')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_initials(self):
        fn = self.first_name[:1].upper() if self.first_name else ''
        ln = self.last_name[:1].upper() if self.last_name else ''
        return fn + ln or self.email[:2].upper()

    @property
    def is_pro(self):
        return self.user_type == 'pro'

    @property
    def is_client(self):
        return self.user_type == 'client'


class OTPCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(null=True, blank=True)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, default='login')
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"OTP {self.code}"

    @staticmethod
    def generate_code(length=6):
        return ''.join(random.choices(string.digits, k=length))

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profil client de {self.user.get_full_name()}"


class ProProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pro_profile')
    bio = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    certifications = models.TextField(blank=True)

    subscription = models.CharField(
        max_length=20,
        default='free',
        choices=[
            ('free', 'Gratuit'),
            ('premium', 'Premium'),
            ('enterprise', 'Enterprise')
        ]
    )

    subscription_expires = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Profil pro de {self.user.get_full_name()}"