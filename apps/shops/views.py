"""Shops Views — BeautyMap Congo (version nettoyée)"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Avg, Count, Sum
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib import messages
import json

from .models import (
    Shop, Service, Favorite, ShopPromotion,
    ShopPost, ShopPostImage, PostLike,
    CATEGORY_CHOICES, QUARTIER_CHOICES,
)


# ══════════════════════════════════════════════════════════════
#  PAGE D'ACCUEIL
# ══════════════════════════════════════════════════════════════

def home(request):
    """Homepage — salons vedettes + publications récentes"""
    featured_shops = Shop.objects.filter(is_active=True, is_featured=True).annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
        review_count=Count('reviews', filter=Q(reviews__is_approved=True)),
    ).order_by('-avg_rating')[:6]

    top_shops = Shop.objects.filter(is_active=True).annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
        review_count=Count('reviews', filter=Q(reviews__is_approved=True)),
    ).order_by('-avg_rating', '-review_count')[:8]

    # Publications récentes pour l'aperçu sur l'accueil
    recent_posts = ShopPost.objects.filter(
        is_published=True, shop__is_active=True
    ).select_related('shop').prefetch_related('images').order_by('?')[:6]

    stats = {
        'shops_count':    Shop.objects.filter(is_active=True).count(),
        'bookings_count': 5400,   # placeholder — remplacer par une vraie requête
        'clients_count':  1800,
    }

    return render(request, 'public/home.html', {
        'featured_shops': featured_shops,
        'top_shops':      top_shops,
        'recent_posts':   recent_posts,
        'categories':     CATEGORY_CHOICES,
        'stats':          stats,
    })


# ══════════════════════════════════════════════════════════════
#  EXPLORER
# ══════════════════════════════════════════════════════════════

def explore(request):
    """Page Explorer — liste + filtres"""
    shops = Shop.objects.filter(is_active=True).annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
        reviews_count=Count('reviews', filter=Q(reviews__is_approved=True)),
    )

    q        = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    quartier = request.GET.get('quartier', '')
    sort     = request.GET.get('sort', 'rating')
    open_now = request.GET.get('open_now', '')

    if q:
        shops = shops.filter(
            Q(name__icontains=q) | Q(description__icontains=q) |
            Q(address__icontains=q) | Q(services__name__icontains=q)
        ).distinct()

    if category:
        shops = shops.filter(category=category)
    if quartier:
        shops = shops.filter(quartier=quartier)

    if sort == 'rating':
        shops = shops.order_by('-avg_rating', '-reviews_count')
    elif sort == 'newest':
        shops = shops.order_by('-created_at')
    elif sort == 'name':
        shops = shops.order_by('name')
    else:
        shops = shops.order_by('-avg_rating')

    paginator   = Paginator(shops, 12)
    shops_page  = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'public/explore.html', {
        'shops':             shops_page,
        'categories':        CATEGORY_CHOICES,
        'quartiers':         QUARTIER_CHOICES,
        'current_q':         q,
        'current_category':  category,
        'current_quartier':  quartier,
        'current_sort':      sort,
        'total_count':       paginator.count,
    })


# ══════════════════════════════════════════════════════════════
#  DÉTAIL BOUTIQUE
# ══════════════════════════════════════════════════════════════

def shop_detail(request, slug):
    """Page détail d'un salon"""
    shop = get_object_or_404(Shop, slug=slug, is_active=True)
    Shop.objects.filter(pk=shop.pk).update(views_count=shop.views_count + 1)

    reviews  = shop.reviews.filter(is_approved=True).select_related('client').order_by('-created_at')[:10]
    services = shop.services.filter(is_active=True).order_by('order', 'name')
    photos   = shop.photos.order_by('order')
    schedules = shop.schedules.all()
    posts    = ShopPost.objects.filter(shop=shop, is_published=True).prefetch_related('images').order_by('-created_at')[:9]

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, shop=shop).exists()

    related_shops = Shop.objects.filter(
        category=shop.category, is_active=True
    ).exclude(pk=shop.pk).annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
    ).order_by('-avg_rating')[:4]

    return render(request, 'public/shop_detail.html', {
        'shop':          shop,
        'reviews':       reviews,
        'services':      services,
        'photos':        photos,
        'schedules':     schedules,
        'posts':         posts,
        'is_favorite':   is_favorite,
        'related_shops': related_shops,
    })


# ══════════════════════════════════════════════════════════════
#  CARTE
# ══════════════════════════════════════════════════════════════

def map_view(request):
    """Page Carte"""
    shops = Shop.objects.filter(is_active=True, latitude__isnull=False).annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
    )
    shops_json = json.dumps([{
        'id': str(s.id), 'name': s.name, 'category': s.category,
        'category_emoji': s.category_emoji, 'quartier': s.get_quartier_display(),
        'lat': float(s.latitude), 'lng': float(s.longitude),
        'rating': float(s.avg_rating or 0), 'slug': s.slug, 'phone': s.phone,
        'is_open': s.is_open,
    } for s in shops])
    return render(request, 'public/map.html', {
        'shops_json': shops_json, 'categories': CATEGORY_CHOICES,
    })


# ══════════════════════════════════════════════════════════════
#  FEED — PAGE DÉCOUVERTE
# ══════════════════════════════════════════════════════════════

def feed_view(request):
    """
    GET /decouverte/
    Défilement des publications — style réseau social.
    Supporte filtre + scroll infini (AJAX).
    """
    category = request.GET.get('category', '')
    page     = int(request.GET.get('page', 1))

    posts = ShopPost.objects.filter(
        is_published=True, shop__is_active=True
    ).select_related('shop').prefetch_related('images', 'likes').order_by('-created_at')

    if category:
        posts = posts.filter(post_type=category)

    paginator = Paginator(posts, 12)
    page_obj  = paginator.get_page(page)

    # Réponse AJAX pour le scroll infini
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.template.loader import render_to_string
        html = render_to_string('public/_post_cards.html', {
            'posts': page_obj, 'request': request
        })
        return JsonResponse({
            'html':      html,
            'has_next':  page_obj.has_next(),
            'next_page': page + 1,
        })

    return render(request, 'public/feed.html', {
        'posts':       page_obj,
        'categories':  ShopPost.POST_TYPES,
        'current_cat': category,
    })


# ══════════════════════════════════════════════════════════════
#  ACTIONS BOUTIQUE
# ══════════════════════════════════════════════════════════════

@login_required
@require_POST
def toggle_favorite(request, shop_id):
    shop = get_object_or_404(Shop, pk=shop_id, is_active=True)
    fav  = Favorite.objects.filter(user=request.user, shop=shop).first()
    if fav:
        fav.delete()
        return JsonResponse({'is_favorite': False})
    Favorite.objects.create(user=request.user, shop=shop)
    return JsonResponse({'is_favorite': True})


def map_data_api(request):
    """JSON endpoint pour la carte"""
    shops    = Shop.objects.filter(is_active=True, latitude__isnull=False).annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
    )
    category = request.GET.get('category', '')
    if category:
        shops = shops.filter(category=category)
    return JsonResponse({'shops': [{
        'id': str(s.id), 'name': s.name, 'category': s.category,
        'category_emoji': s.category_emoji,
        'quartier': s.get_quartier_display(),
        'lat': float(s.latitude), 'lng': float(s.longitude),
        'rating': float(s.avg_rating or 0), 'slug': s.slug,
        'phone': s.phone, 'is_open': s.is_open,
    } for s in shops]})


def api_search(request):
    """GET /api/search/?q=... — Live search JSON"""
    q     = request.GET.get('q', '').strip()
    limit = min(int(request.GET.get('limit', 6)), 20)
    if len(q) < 2:
        return JsonResponse({'shops': []})
    shops = Shop.objects.filter(is_active=True).filter(
        Q(name__icontains=q) | Q(description__icontains=q) |
        Q(address__icontains=q) | Q(services__name__icontains=q)
    ).annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
    ).distinct()[:limit]
    return JsonResponse({'shops': [{
        'name':           s.name,
        'slug':           s.slug,
        'category':       s.get_category_display(),
        'category_emoji': s.category_emoji,
        'quartier':       s.get_quartier_display(),
        'rating':         float(s.avg_rating) if s.avg_rating else None,
        'is_open':        s.is_open,
    } for s in shops]})


# ══════════════════════════════════════════════════════════════
#  CRÉER UNE BOUTIQUE
# ══════════════════════════════════════════════════════════════

@login_required
def create_shop(request):
    if not request.user.is_pro:
        messages.info(request, "Vous devez être professionnel pour créer une boutique.")
        return redirect('client_dashboard')

    if request.method == 'POST':
        name        = request.POST.get('name', '').strip()
        category    = request.POST.get('category', '')
        quartier    = request.POST.get('quartier', '')
        address     = request.POST.get('address', '').strip()
        description = request.POST.get('description', '').strip()
        phone       = request.POST.get('phone', '').strip()
        whatsapp    = request.POST.get('whatsapp', '').strip()
        email       = request.POST.get('email', '').strip()

        errors = []
        if not name:     errors.append("Le nom est obligatoire.")
        if not category: errors.append("La catégorie est obligatoire.")
        if not quartier: errors.append("Le quartier est obligatoire.")
        if not phone:    errors.append("Le téléphone est obligatoire.")

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'dashboard/pro_no_shop.html',
                          {'categories': CATEGORY_CHOICES, 'quartiers': QUARTIER_CHOICES})

        try:
            shop = Shop(
                owner=request.user, name=name, category=category,
                quartier=quartier, phone=phone, whatsapp=whatsapp, email=email,
                address=address or f"{quartier.replace('_','-').title()}, Brazzaville",
                description=description or f"Bienvenue chez {name}.",
            )
            if 'cover_image' in request.FILES:
                shop.cover_image = request.FILES['cover_image']
            if 'logo' in request.FILES:
                shop.logo = request.FILES['logo']
            shop.save()
            messages.success(request, f"🎉 Votre boutique « {shop.name} » a été créée !")
            return redirect('pro_dashboard')
        except Exception as e:
            messages.error(request, f"Erreur : {str(e)}")

    return render(request, 'dashboard/pro_no_shop.html',
                  {'categories': CATEGORY_CHOICES, 'quartiers': QUARTIER_CHOICES})


# ══════════════════════════════════════════════════════════════
#  PUBLICATIONS (POSTS)
# ══════════════════════════════════════════════════════════════

@login_required
@require_POST
def create_post(request, shop_slug):
    """POST /boutique/<slug>/publier/ — créer une publication"""
    shop      = get_object_or_404(Shop, slug=shop_slug, owner=request.user)
    caption   = request.POST.get('caption', '').strip()
    post_type = request.POST.get('post_type', 'realisation')
    price_raw = request.POST.get('price', '').strip()
    images    = request.FILES.getlist('images')

    if not caption and not images:
        return JsonResponse({'error': 'Ajoutez une description ou une photo.'}, status=400)

    price = None
    if price_raw:
        try:
            price = int(float(price_raw))
        except (ValueError, TypeError):
            pass

    post = ShopPost.objects.create(
        shop=shop, caption=caption, post_type=post_type, price=price
    )
    for i, img in enumerate(images[:10]):
        ShopPostImage.objects.create(post=post, image=img, order=i)

    # Notifier les abonnés (favoris)
    try:
        from apps.notifications.models import Notification
        for fav in shop.favorited_by.select_related('user')[:50]:
            Notification.send(
                user=fav.user, notif_type='promo',
                title=f"Nouvelle publication de {shop.name}",
                message=caption[:80] if caption else "Regardez notre nouvelle réalisation !",
                link=f"/boutique/{shop.slug}/#posts",
            )
    except Exception:
        pass

    return JsonResponse({'success': True, 'post_id': str(post.id),
                         'message': 'Publication créée !'})


@login_required
@require_POST
def delete_post(request, post_id):
    """POST /post/<uuid>/supprimer/"""
    post = get_object_or_404(ShopPost, pk=post_id, shop__owner=request.user)
    post.delete()
    return JsonResponse({'success': True})


@login_required
@require_POST
def like_post(request, post_id):
    """POST /post/<uuid>/like/ — toggle like"""
    post = get_object_or_404(ShopPost, pk=post_id, is_published=True)
    like = PostLike.objects.filter(post=post, user=request.user).first()
    if like:
        like.delete()
        post.likes_count = max(0, post.likes_count - 1)
        liked = False
    else:
        PostLike.objects.create(post=post, user=request.user)
        post.likes_count += 1
        liked = True
    post.save(update_fields=['likes_count'])
    return JsonResponse({'liked': liked, 'count': post.likes_count})


def shop_posts_api(request, shop_slug):
    """GET /boutique/<slug>/posts/?page=1"""
    shop     = get_object_or_404(Shop, slug=shop_slug, is_active=True)
    posts    = ShopPost.objects.filter(shop=shop, is_published=True).prefetch_related('images')
    page_obj = Paginator(posts, 9).get_page(request.GET.get('page', 1))
    data = []
    for p in page_obj:
        img = p.get_main_image()
        data.append({
            'id':       str(p.id), 'type': p.get_post_type_display(),
            'caption':  p.caption, 'price': int(p.price) if p.price else None,
            'likes':    p.likes_count,
            'image':    request.build_absolute_uri(img.image.url) if img else None,
            'images_count': p.images.count(),
            'created_at':   p.created_at.strftime('%d/%m/%Y'),
        })
    return JsonResponse({'posts': data, 'has_next': page_obj.has_next()})


# ══════════════════════════════════════════════════════════════
#  PAGES STATIQUES
# ══════════════════════════════════════════════════════════════

def pros_page(request):
    features = [
        {'icon': '🏪', 'title': 'Vitrine digitale',    'desc': 'Photos, services, prix, horaires — tout sur un profil visible par des milliers de clients.'},
        {'icon': '📅', 'title': 'Gestion des RDV',     'desc': 'Recevez des demandes, confirmez en un clic. Calendrier intégré et rappels SMS.'},
        {'icon': '📸', 'title': 'Publications',         'desc': 'Partagez vos réalisations, produits et promos comme sur Instagram.'},
        {'icon': '💬', 'title': 'Messagerie directe',   'desc': 'Communiquez avec vos clients en temps réel via la messagerie intégrée.'},
        {'icon': '⭐', 'title': 'Avis & réputation',    'desc': 'Collectez des avis vérifiés et bâtissez votre réputation en ligne.'},
        {'icon': '📊', 'title': 'Tableau de bord',      'desc': 'Stats, revenus, avis — pilotez votre activité depuis votre smartphone.'},
        {'icon': '🗺️', 'title': 'Carte interactive',    'desc': 'Apparaissez sur la carte de Brazzaville et soyez trouvé par les clients proches.'},
        {'icon': '📱', 'title': 'Application mobile',   'desc': 'Gérez tout depuis votre téléphone avec l\'app BeautyMap Congo (bientôt).'},
    ]
    return render(request, 'public/pros.html', {'features': features})


def contact_page(request):
    sent = False
    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', 'Contact')
        message = request.POST.get('message', '').strip()
        if name and email and message:
            from django.core.mail import send_mail
            from django.conf import settings as dj_settings
            try:
                send_mail(
                    f"[BeautyMap Contact] {subject}",
                    f"De : {name} <{email}>\n\n{message}",
                    dj_settings.DEFAULT_FROM_EMAIL,
                    [dj_settings.DEFAULT_FROM_EMAIL],
                )
            except Exception:
                pass
            sent = True
    return render(request, 'public/contact.html', {'sent': sent})