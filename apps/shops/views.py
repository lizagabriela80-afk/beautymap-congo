"""Shop Views — BeautyMap Congo"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .models import Shop, Service, CATEGORY_CHOICES, QUARTIER_CHOICES
from django.db.models import Count
from django.contrib import messages


def home(request):
    """Homepage"""
    featured_shops = Shop.objects.filter(is_active=True, is_featured=True).annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
        review_count=Count('reviews', filter=Q(reviews__is_approved=True))
    ).order_by('-avg_rating')[:6]


    top_shops = Shop.objects.annotate(
    reviews_count=Count('reviews')  # 🔥 change le nom
    )

    stats = {
        'shops_count': Shop.objects.filter(is_active=True).count(),
        'categories': CATEGORY_CHOICES,
    }

    return render(request, 'public/home.html', {
        'featured_shops': featured_shops,
        'top_shops': top_shops,
        'categories': CATEGORY_CHOICES,
        'stats': stats,
    })


def explore(request):
    """Explore/search page"""
    shops = Shop.objects.filter(is_active=True).annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
        reviews_count=Count('reviews', filter=Q(reviews__is_approved=True))
    )

    # Filters
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    quartier = request.GET.get('quartier', '')
    sort = request.GET.get('sort', 'rating')
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

    # Sorting
    if sort == 'rating':
        shops = shops.order_by('-avg_rating', '-reviews_count')
    elif sort == 'price_asc':
        shops = shops.order_by('services__price')
    elif sort == 'name':
        shops = shops.order_by('name')
    elif sort == 'newest':
        shops = shops.order_by('-created_at')
    else:
        shops = shops.order_by('-avg_rating')

    paginator = Paginator(shops, 12)
    page = request.GET.get('page', 1)
    shops_page = paginator.get_page(page)

    return render(request, 'public/explore.html', {
        'shops': shops_page,
        'categories': CATEGORY_CHOICES,
        'quartiers': QUARTIER_CHOICES,
        'current_q': q,
        'current_category': category,
        'current_quartier': quartier,
        'current_sort': sort,
        'total_count': paginator.count,
    })


def shop_detail(request, slug):
    """Shop detail page"""
    shop = get_object_or_404(Shop, slug=slug, is_active=True)
    # Increment views
    Shop.objects.filter(pk=shop.pk).update(views_count=shop.views_count + 1)

    reviews = shop.reviews.filter(is_approved=True).select_related('client').order_by('-created_at')[:10]
    services = shop.services.filter(is_active=True).order_by('order', 'name')
    photos = shop.photos.order_by('order')
    schedules = shop.schedules.all()

    is_favorite = False
    if request.user.is_authenticated and hasattr(request.user, 'client_profile'):
        is_favorite = request.user.client_profile.favorites.filter(pk=shop.pk).exists()

    related_shops = Shop.objects.filter(
        category=shop.category, is_active=True
    ).exclude(pk=shop.pk).annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
    ).order_by('-avg_rating')[:4]

    return render(request, 'public/shop_detail.html', {
        'shop': shop,
        'reviews': reviews,
        'services': services,
        'photos': photos,
        'schedules': schedules,
        'is_favorite': is_favorite,
        'related_shops': related_shops,
    })


def map_view(request):
    """Map page"""
    shops = Shop.objects.filter(is_active=True, latitude__isnull=False).annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
    ).values('id', 'name', 'category', 'quartier', 'latitude', 'longitude',
             'phone', 'slug', 'avg_rating')
    import json
    from decimal import Decimal

    shops_json = []
    for s in shops:
        shops_json.append({
            'id': str(s['id']),
            'name': s['name'],
            'category': s['category'],
            'quartier': s['quartier'],
            'lat': float(s['latitude'] or 0),
            'lng': float(s['longitude'] or 0),
            'phone': s['phone'],
            'slug': s['slug'],
            'rating': float(s['avg_rating'] or 0),
        })

    return render(request, 'public/map.html', {
        'shops_json': json.dumps(shops_json),
        'categories': CATEGORY_CHOICES,
    })


@login_required
@require_POST
def toggle_favorite(request, shop_id):
    from .models import Favorite
    shop = get_object_or_404(Shop, pk=shop_id, is_active=True)
    fav = Favorite.objects.filter(user=request.user, shop=shop).first()
    if fav:
        fav.delete()
        return JsonResponse({'is_favorite': False})
    else:
        Favorite.objects.create(user=request.user, shop=shop)
        return JsonResponse({'is_favorite': True})
    

def map_data_api(request):
    """JSON endpoint for map markers"""
    from django.db.models import Avg
    shops = Shop.objects.filter(is_active=True, latitude__isnull=False).annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
    )
    category = request.GET.get('category', '')
    if category:
        shops = shops.filter(category=category)

    data = []
    for s in shops:
        data.append({
            'id': str(s.id),
            'name': s.name,
            'category': s.category,
            'category_emoji': s.category_emoji,
            'quartier': s.get_quartier_display(),
            'lat': float(s.latitude),
            'lng': float(s.longitude),
            'rating': float(s.avg_rating or 0),
            'slug': s.slug,
            'phone': s.phone,
            'is_open': s.is_open,
        })
    return JsonResponse({'shops': data})



# ─────────────────────────────────────────────
# CRÉATION DE BOUTIQUE (depuis le dashboard pro)
# ─────────────────────────────────────────────
@login_required
def create_shop(request):
    """Formulaire de création de boutique pour un pro sans boutique."""
    from django.contrib.auth.decorators import login_required
    from django.contrib import messages

    if not request.user.is_pro:
       messages.info(request, "Vous devez être un professionnel pour créer une boutique.")
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

        # Validations
        errors = []
        if not name:        errors.append("Le nom de la boutique est obligatoire.")
        if not category:    errors.append("La catégorie est obligatoire.")
        if not quartier:    errors.append("Le quartier est obligatoire.")
        if not phone:       errors.append("Le numéro de téléphone est obligatoire.")

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'dashboard/pro_no_shop.html')

        try:
            shop = Shop.objects.create(
                owner       = request.user,
                name        = name,
                category    = category,
                quartier    = quartier,
                address     = address or f"{quartier.replace('_','-').title()}, Brazzaville",
                description = description or f"Bienvenue chez {name}.",
                phone       = phone,
                whatsapp    = whatsapp,
                email       = email,
            )
            messages.success(
                request,
                f"🎉 Votre boutique « {shop.name} » a été créée avec succès ! "
                f"Complétez-la en ajoutant vos services et horaires."
            )
            return redirect('pro_dashboard')
        except Exception as e:
            messages.error(request, f"Erreur lors de la création : {str(e)}")

    return render(request, 'dashboard/pro_no_shop.html')

def pros_page(request):
    return render(request, 'public/pros.html')

def api_search(request):
    """GET /api/search/?q=<query>&limit=5 — Live search JSON pour le frontend"""
    from django.db.models import Avg, Q
    q     = request.GET.get('q', '').strip()
    limit = min(int(request.GET.get('limit', 5)), 20)
    if len(q) < 2:
        return JsonResponse({'shops': []})
    shops = Shop.objects.filter(
        is_active=True
    ).filter(
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(address__icontains=q) |
        Q(services__name__icontains=q)
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


def contact_page(request):
    """Page de contact avec formulaire d'envoi d'email"""
    sent = False
    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', 'Contact BeautyMap')
        message = request.POST.get('message', '').strip()
        if name and email and message:
            from django.core.mail import send_mail
            from django.conf import settings
            try:
                send_mail(
                    f"[BeautyMap Contact] {subject}",
                    f"De : {name} <{email}>\n\n{message}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                )
            except Exception:
                pass
            sent = True
    return render(request, 'public/contact.html', {'sent': sent})