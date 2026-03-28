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
from .models import ShopPost, ShopPostImage, PostLike


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


def pros_page(request):
    """Page Pour les professionnels"""
    features = [
        {'icon':'🏪','title':'Vitrine digitale','desc':'Photos, services, horaires et tarifs — tout sur un profil professionnel visible par des milliers de clients.'},
        {'icon':'📅','title':'Gestion des RDV','desc':'Recevez des demandes, confirmez ou refusez en un clic. Calendrier intégré et rappels automatiques.'},
        {'icon':'💬','title':'Messagerie directe','desc':'Communiquez directement avec vos clients via la messagerie intégrée ou WhatsApp.'},
        {'icon':'⭐','title':'Avis & réputation','desc':'Collectez des avis vérifiés et répondez pour bâtir votre réputation en ligne.'},
        {'icon':'📊','title':'Tableau de bord','desc':'Statistiques, revenus, taux de remplissage — pilotez votre activité en temps réel.'},
        {'icon':'🗺️','title':'Carte interactive','desc':'Apparaissez sur la carte de Brazzaville et soyez trouvé par les clients près de chez vous.'},
        {'icon':'📱','title':'Application mobile','desc':'Gérez votre activité depuis votre smartphone avec l\'app BeautyMap Congo (bientôt disponible).'},
        {'icon':'🔒','title':'Badge vérifié','desc':'Obtenez le badge ✓ Vérifié pour inspirer confiance et vous démarquer de la concurrence.'},
    ]
    return render(request, 'public/pros.html', {'features': features})


def contact_page(request):
    """Page de contact"""
    sent = False
    if request.method == 'POST':
        # Simple formulaire de contact — intégrer un vrai envoi email en prod
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        if name and email and message:
            from django.core.mail import send_mail
            from django.conf import settings
            try:
                send_mail(
                    f"[BeautyMap Contact] {subject or 'Message de contact'}",
                    f"De: {name} <{email}>\n\n{message}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                )
            except Exception:
                pass
            sent = True
    return render(request, 'public/contact.html', {'sent': sent})


# ─────────────────────────────────────────────────────────────
#  beautymap_project/views.py (nouveau fichier à créer)
# ─────────────────────────────────────────────────────────────
"""Vues d'erreur personnalisées"""
from django.shortcuts import render

def error_404(request, exception=None):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)


def api_search(request):
    """
    GET /api/search/?q=<query>&limit=5
    Endpoint JSON pour la live search du frontend.
    """
    q     = request.GET.get('q', '').strip()
    limit = min(int(request.GET.get('limit', 5)), 20)

    if len(q) < 2:
        return JsonResponse({'shops': []})

    from django.db.models import Avg, Q

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
    """Page de contact"""
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

def feed_view(request):
    """
    GET /decouverte/
    Défilement des publications de toutes les boutiques — style réseau social.
    Supporte le filtre par catégorie et le chargement infini (AJAX).
    """
    category = request.GET.get('category', '')
    page     = int(request.GET.get('page', 1))
    per_page = 12

    posts = ShopPost.objects.filter(
        is_published=True, shop__is_active=True
    ).select_related('shop').prefetch_related('images', 'likes')

    if category:
        posts = posts.filter(post_type=category)

    from django.core.paginator import Paginator
    paginator  = Paginator(posts, per_page)
    page_obj   = paginator.get_page(page)

    # Retourner JSON pour le chargement infini AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.template.loader import render_to_string
        html = render_to_string('public/_post_cards.html', {
            'posts': page_obj, 'request': request
        })
        return JsonResponse({
            'html':     html,
            'has_next': page_obj.has_next(),
            'next_page': page + 1,
        })

    return render(request, 'public/feed.html', {
        'posts':      page_obj,
        'categories': ShopPost.POST_TYPES,
        'current_cat': category,
    })


# ── CRÉER UNE PUBLICATION ────────────────────────────────────────────────────

@login_required
@require_POST
def create_post(request, shop_slug):
    """
    POST /boutique/<slug>/publier/
    Crée une publication avec texte + photos multiples.
    """
    shop = get_object_or_404(Shop, slug=shop_slug, owner=request.user)

    caption   = request.POST.get('caption', '').strip()
    post_type = request.POST.get('post_type', 'realisation')
    price_raw = request.POST.get('price', '').strip()
    images    = request.FILES.getlist('images')  # plusieurs fichiers

    if not caption and not images:
        return JsonResponse({'error': 'Ajoutez une description ou une photo.'}, status=400)

    price = None
    if price_raw:
        try:
            price = int(price_raw)
        except ValueError:
            pass

    post = ShopPost.objects.create(
        shop=shop, caption=caption, post_type=post_type, price=price
    )

    for i, img in enumerate(images[:10]):  # max 10 images par post
        ShopPostImage.objects.create(post=post, image=img, order=i)

    # Notification aux favoris (optionnel)
    try:
        from apps.notifications.models import Notification
        favs = shop.favorited_by.select_related('user')
        for fav in favs[:50]:  # max 50 notifs
            Notification.send(
                user=fav.user,
                notif_type='promo',
                title=f"Nouvelle publication de {shop.name}",
                message=caption[:80] if caption else "Regardez notre nouvelle réalisation !",
                link=f"/boutique/{shop.slug}/#posts",
            )
    except Exception:
        pass

    return JsonResponse({
        'success':  True,
        'post_id':  str(post.id),
        'message':  'Publication créée avec succès !',
    })


# ── SUPPRIMER UNE PUBLICATION ────────────────────────────────────────────────

@login_required
@require_POST
def delete_post(request, post_id):
    """POST /post/<uuid>/supprimer/"""
    post = get_object_or_404(ShopPost, pk=post_id, shop__owner=request.user)
    post.delete()
    return JsonResponse({'success': True})


# ── LIKER UNE PUBLICATION ────────────────────────────────────────────────────

@login_required
@require_POST
def like_post(request, post_id):
    """POST /post/<uuid>/like/ — Toggle like"""
    post  = get_object_or_404(ShopPost, pk=post_id, is_published=True)
    like  = PostLike.objects.filter(post=post, user=request.user).first()

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


# ── POSTS D'UNE BOUTIQUE (AJAX) ──────────────────────────────────────────────

def shop_posts_api(request, shop_slug):
    """GET /boutique/<slug>/posts/?page=1 — Posts paginés d'un salon"""
    shop  = get_object_or_404(Shop, slug=shop_slug, is_active=True)
    posts = ShopPost.objects.filter(
        shop=shop, is_published=True
    ).prefetch_related('images')

    from django.core.paginator import Paginator
    page_obj = Paginator(posts, 9).get_page(request.GET.get('page', 1))

    data = []
    for p in page_obj:
        main_img = p.get_main_image()
        data.append({
            'id':        str(p.id),
            'type':      p.get_post_type_display(),
            'caption':   p.caption,
            'price':     int(p.price) if p.price else None,
            'likes':     p.likes_count,
            'image':     request.build_absolute_uri(main_img.image.url) if main_img else None,
            'images_count': p.images.count(),
            'created_at': p.created_at.strftime('%d/%m/%Y'),
        })
    return JsonResponse({'posts': data, 'has_next': page_obj.has_next()})

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
