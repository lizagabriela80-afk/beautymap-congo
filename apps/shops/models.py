"""Shops Models — BeautyMap Congo"""
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
import uuid
from django.conf import settings


CATEGORY_CHOICES = [
    ('coiffure', '✂️ Coiffure'),
    ('esthetique', '💆 Esthétique'),
    ('onglerie', '💅 Onglerie'),
    ('vetements', '👗 Vêtements'),
    ('barbier', '🪒 Barbier'),
    ('maquillage', '💄 Maquillage'),
    ('spa', '🛁 Spa & Bien-être'),
    ('autre', '🏪 Autre'),
]

QUARTIER_CHOICES = [
    ('bacongo', 'Bacongo'),
    ('poto_poto', 'Poto-Poto'),
    ('moungali', 'Moungali'),
    ('ouenze', 'Ouenzé'),
    ('talangai', 'Talangaï'),
    ('makelekele', 'Makélékélé'),
    ('mfilou', 'Mfilou'),
    ('djiri', 'Djiri'),
    ('autre', 'Autre'),
]


class Shop(models.Model):
    """Main shop/boutique model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ✅ CORRECTION ICI
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shops'
    )

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    address = models.CharField(max_length=250)
    quartier = models.CharField(max_length=20, choices=QUARTIER_CHOICES)
    city = models.CharField(max_length=80, default='Brazzaville')

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    phone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    cover_image = models.ImageField(upload_to='shops/covers/', null=True, blank=True)
    logo = models.ImageField(upload_to='shops/logos/', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    views_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Boutique'
        verbose_name_plural = 'Boutiques'
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            n = 1
            while Shop.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shops:detail', kwargs={'slug': self.slug})

    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if not reviews.exists():
            return 0
        return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)

    @property
    def is_open(self):
        from django.utils import timezone
        now = timezone.localtime()
        day_name = now.strftime('%A').lower()
        schedule = self.schedules.filter(day=day_name, is_closed=False).first()
        if not schedule:
            return False
        current_time = now.time()
        return schedule.open_time <= current_time <= schedule.close_time

    @property
    def category_emoji(self):
        emojis = {
            'coiffure': '✂️', 'esthetique': '💆', 'onglerie': '💅',
            'vetements': '👗', 'barbier': '🪒', 'maquillage': '💄',
            'spa': '🛁', 'autre': '🏪'
        }
        return emojis.get(self.category, '🏪')


class ShopPhoto(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='shops/photos/')
    caption = models.CharField(max_length=200, blank=True)
    is_cover = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']


class Schedule(models.Model):
    DAYS = [
        ('monday', 'Lundi'), ('tuesday', 'Mardi'), ('wednesday', 'Mercredi'),
        ('thursday', 'Jeudi'), ('friday', 'Vendredi'),
        ('saturday', 'Samedi'), ('sunday', 'Dimanche'),
    ]

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='schedules')
    day = models.CharField(max_length=10, choices=DAYS)
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['shop', 'day']
        ordering = ['day']


class Service(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    duration_minutes = models.PositiveIntegerField(default=60)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']


class ShopPromotion(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='promotions')
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    discount_percent = models.PositiveIntegerField(default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    code = models.CharField(max_length=20, blank=True)
    valid_from = models.DateField()
    valid_until = models.DateField()
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    uses_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)


class Favorite(models.Model):
    """Boutiques favorites d'un client"""

    # ✅ CORRECTION ICI
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'shop']


# ═══════════════════════════════════════════════════════════════
#  À AJOUTER à la fin de apps/shops/models.py
# ═══════════════════════════════════════════════════════════════

class ShopPost(models.Model):
    """
    Publication d'un professionnel (style Facebook/Instagram).
    Peut contenir du texte, des photos, et un tag de catégorie.
    """
    POST_TYPES = [
        ('realisation', '✨ Réalisation'),
        ('produit',     '🛒 Produit'),
        ('promo',       '🎉 Promotion'),
        ('soin',        '💆 Soin'),
        ('avant_apres', '🔄 Avant / Après'),
        ('annonce',     '📢 Annonce'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shop        = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='posts')
    post_type   = models.CharField(max_length=20, choices=POST_TYPES, default='realisation')
    caption     = models.TextField(blank=True, help_text="Description de la publication")
    price       = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True,
                                      help_text="Prix si c'est un produit ou service")
    is_published = models.BooleanField(default=True)
    likes_count  = models.PositiveIntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Publication'
        verbose_name_plural = 'Publications'
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.shop.name} — {self.get_post_type_display()} ({self.created_at:%d/%m/%Y})"

    def get_main_image(self):
        return self.images.first()


class ShopPostImage(models.Model):
    """Images attachées à une publication (une pub peut avoir plusieurs photos)"""
    post    = models.ForeignKey(ShopPost, on_delete=models.CASCADE, related_name='images')
    image   = models.ImageField(upload_to='shops/posts/%Y/%m/')
    order   = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image de {self.post}"


class PostLike(models.Model):
    """Like sur une publication (unique par utilisateur)"""
    post       = models.ForeignKey(ShopPost, on_delete=models.CASCADE, related_name='likes')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['post', 'user']
