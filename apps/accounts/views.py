"""Accounts Views — BeautyMap Congo"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Avg, Q, Sum
from .models import User, OTPCode, ClientProfile, ProProfile
from .otp_service import generate_code, send_otp
from apps.shops.models import Shop, Favorite, CATEGORY_CHOICES, QUARTIER_CHOICES
from apps.bookings.models import Booking
from apps.reviews.models import Review
from apps.notifications.models import Notification
from datetime import timedelta
import json


# ══════════════════════════════════════════════
#  HELPERS OTP
# ══════════════════════════════════════════════

from django.core.mail import send_mail
from django.conf import settings

def _create_and_send_otp(phone: str = None, email: str = None) -> dict:
    """Crée un OTP et l'envoie par SMS ou Email"""

    OTPCode.objects.filter(
        Q(phone=phone) | Q(email=email),
        is_used=False
    ).delete()

    code    = generate_code(6)
    expires = timezone.now() + timedelta(minutes=5)

    otp = OTPCode.objects.create(
        phone      = phone,
        email      = email,  # ⚠️ ajoute ce champ dans ton modèle !
        code       = code,
        purpose    = 'login',
        is_used    = False,
        expires_at = expires,
    )

    # ── EMAIL ──
    if email:
        send_mail(
            '🔐 Votre code BeautyMap',
            f'Votre code OTP est : {code}\nValable 5 minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )
        return {'channel': 'email', 'code': code}

    # ── SMS ──
    if phone:
        result = send_otp(phone, code)
        result['channel'] = 'sms'
        result['code']    = code
        return result

    return {'error': 'Aucun canal fourni'}

# ══════════════════════════════════════════════
#  INSCRIPTION  →  enregistrement en base MySQL
# ══════════════════════════════════════════════

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    ctx = {'categories': CATEGORY_CHOICES, 'quartiers': QUARTIER_CHOICES}

    if request.method == 'POST':
        user_type  = request.POST.get('user_type', 'client').strip()
        email      = request.POST.get('email', '').strip().lower()
        password   = request.POST.get('password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        phone      = request.POST.get('phone', '').strip()

        # ── Validations ──────────────────────────
        errors = []
        if not first_name:
            errors.append("Le prénom est obligatoire.")
        if not email:
            errors.append("L'adresse email est obligatoire.")
        if not password:
            errors.append("Le mot de passe est obligatoire.")
        elif len(password) < 8:
            errors.append("Le mot de passe doit contenir au moins 8 caractères.")
        if User.objects.filter(email=email).exists():
            errors.append("Cette adresse email est déjà utilisée. Connectez-vous.")

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'accounts/register.html', ctx)

        # ── Création de l'utilisateur en base ────
        try:
            user = User.objects.create_user(
                email      = email,
                password   = password,
                first_name = first_name,
                last_name  = last_name,
                phone      = phone,
                user_type  = user_type,
            )

            # ── Profil selon le type ──────────────
            if user_type == 'client':
                ClientProfile.objects.create(user=user)

            elif user_type == 'pro':
                shop_name = request.POST.get('shop_name', '').strip()
                category  = request.POST.get('category',  'coiffure')
                quartier  = request.POST.get('quartier',  'bacongo')

                if not shop_name:
                    user.delete()
                    messages.error(request, "Le nom de la boutique est obligatoire.")
                    return render(request, 'accounts/register.html', ctx)

                ProProfile.objects.create(user=user, subscription='free')

                Shop.objects.create(
                    owner       = user,
                    name        = shop_name,
                    category    = category,
                    quartier    = quartier,
                    phone       = phone,
                    description = (
                        f"Bienvenue chez {shop_name}. "
                        f"Modifiez cette description depuis votre tableau de bord."
                    ),
                    address = f"{quartier.replace('_', '-').title()}, Brazzaville",
                )

            # ── Connexion automatique après inscription ──
            login(request, user,
                  backend='django.contrib.auth.backends.ModelBackend')

            messages.success(
                request,
                f"🎉 Bienvenue {user.first_name} ! "
                f"Votre compte a été créé et enregistré avec succès."
            )
            return redirect('dashboard')

        except Exception as e:
            messages.error(request, f"Erreur lors de la création du compte : {str(e)}")
            return render(request, 'accounts/register.html', ctx)

    return render(request, 'accounts/register.html', ctx)


# ══════════════════════════════════════════════
#  CONNEXION PAR EMAIL
# ══════════════════════════════════════════════

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email    = request.POST.get('email',    '').strip().lower()
        password = request.POST.get('password', '').strip()

        if not email or not password:
            messages.error(request, "Veuillez renseigner votre email et votre mot de passe.")
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, "Ce compte est désactivé. Contactez le support.")
            else:
                login(request, user)
                messages.success(request, f"✅ Bienvenue {user.first_name} !")
                next_url = request.GET.get('next', '')
                return redirect(next_url if next_url else 'dashboard')
        else:
            messages.error(
                request,
                "Email ou mot de passe incorrect. Vérifiez vos identifiants."
            )

    return render(request, 'accounts/login.html')


# ══════════════════════════════════════════════
#  DÉCONNEXION
# ══════════════════════════════════════════════

def logout_view(request):
    logout(request)
    messages.info(request, "👋 Vous avez été déconnecté. À bientôt !")
    return redirect('shops:home')


# ══════════════════════════════════════════════
#  OTP — ENVOI PAR SMS
# ══════════════════════════════════════════════

def send_otp_view(request):
    """Crée un OTP en base et l'envoie par SMS (ou l'affiche en mode DEBUG)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    try:
        data  = json.loads(request.body)
        phone = data.get('phone', '').strip().replace(' ', '').replace('-', '')

        if not phone:
            return JsonResponse({'success': False,
                                 'message': 'Numéro de téléphone requis.'})

        result = _create_and_send_otp(phone)

        response = {
            'success': True,
            'message': 'Code envoyé ! Vérifiez vos SMS.',
            'channel': result.get('channel', 'sms'),
        }

        # En mode DEBUG : renvoyer le code pour l'afficher dans la page
        from django.conf import settings
        if settings.DEBUG:
            response['code']    = result.get('code')
            response['message'] = '🧪 Mode dev — Code affiché ci-dessous'

        return JsonResponse(response)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Données invalides.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


# ══════════════════════════════════════════════
#  OTP — VÉRIFICATION
# ══════════════════════════════════════════════

def verify_otp_view(request):
    """Vérifie le code OTP et connecte l'utilisateur s'il est valide."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    try:
        data  = json.loads(request.body)
        phone = data.get('phone', '').strip().replace(' ', '').replace('-', '')
        code  = data.get('code',  '').strip()

        if not phone or not code:
            return JsonResponse({'success': False,
                                 'message': 'Numéro et code requis.'})

        otp = OTPCode.objects.filter(
            phone=phone, code=code, is_used=False
        ).order_by('-created_at').first()

        if not otp:
            return JsonResponse({'success': False,
                                 'message': '❌ Code incorrect. Réessayez.'})

        if not otp.is_valid():
            return JsonResponse({'success': False,
                                 'message': '⏱️ Code expiré. Demandez un nouveau code.'})

        # Marquer l'OTP comme utilisé
        otp.is_used = True
        otp.save()

        # Connecter l'utilisateur correspondant au numéro
        try:
            user = User.objects.get(phone=phone, is_active=True)
            login(request, user,
                  backend='django.contrib.auth.backends.ModelBackend')
            return JsonResponse({
                'success':  True,
                'message':  f'Bienvenue {user.first_name} !',
                'redirect': '/dashboard/',
            })
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': "Aucun compte trouvé avec ce numéro. "
                           "Créez d'abord un compte.",
                'action':  'register',
            })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Données invalides.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


# ══════════════════════════════════════════════
#  DASHBOARDS
# ══════════════════════════════════════════════

@login_required
def dashboard(request):
    user = request.user
    if user.user_type == 'admin':
        return redirect('admin_dashboard')
    elif user.user_type == 'pro':
        return redirect('pro_dashboard')
    return redirect('client_dashboard')


@login_required
def pro_dashboard(request):
    user = request.user
    if not user.is_pro:
        return redirect('client_dashboard')

    shops = user.shops.filter(is_active=True)
    shop  = shops.first()

    if not shop:
        return render(request, 'dashboard/pro_no_shop.html')

    today            = timezone.now().date()
    this_month_start = today.replace(day=1)

    bookings_today   = Booking.objects.filter(
        shop=shop, date=today
    ).order_by('start_time')

    bookings_pending = Booking.objects.filter(
        shop=shop, status='pending'
    ).order_by('date', 'start_time')

    bookings_month   = Booking.objects.filter(
        shop=shop, date__gte=this_month_start
    )

    recent_reviews = Review.objects.filter(
        shop=shop, is_approved=True
    ).select_related('client').order_by('-created_at')[:5]

    from apps.messaging.models import Conversation
    conversations = Conversation.objects.filter(
        pro=user
    ).order_by('-updated_at')[:10]

    notifs = Notification.objects.filter(
        user=user, is_read=False
    ).order_by('-created_at')[:20]

    # ── Publications ────────────────────────────────────────────
    from apps.shops.models import ShopPost
    shop_posts       = ShopPost.objects.filter(shop=shop).prefetch_related('images').order_by('-created_at')
    posts_count      = shop_posts.count()
    posts_this_month = shop_posts.filter(created_at__gte=this_month_start).count()

    from django.db.models import Sum as DSum
    total_likes = shop_posts.aggregate(total=DSum('likes_count'))['total'] or 0

    stats = {
        'bookings_month':     bookings_month.count(),
        'bookings_confirmed': bookings_month.filter(status='confirmed').count(),
        'revenue_month': bookings_month.filter(
            status__in=['confirmed', 'completed']
        ).aggregate(total=Sum('total_price'))['total'] or 0,
        'avg_rating':      shop.average_rating,
        'review_count':    shop.review_count,
        'views_month':     shop.views_count,
        'unread_messages': sum(c.get_unread_count(user) for c in conversations),
        'unread_notifs':   notifs.count(),
    }

    return render(request, 'dashboard/pro.html', {
        'shop':             shop,
        'shops':            shops,
        'bookings_today':   bookings_today,
        'bookings_pending': bookings_pending,
        'recent_reviews':   recent_reviews,
        'conversations':    conversations,
        'notifications':    notifs,
        'stats':            stats,
        'active_tab':       request.GET.get('tab', 'overview'),
        # Publications
        'shop_posts':       shop_posts,
        'posts_count':      posts_count,
        'posts_this_month': posts_this_month,
        'total_likes':      total_likes,
    })


@login_required
def client_dashboard(request):
    user      = request.user
    bookings  = Booking.objects.filter(
        client=user
    ).select_related('shop', 'service').order_by('-date', '-start_time')[:10]

    favorites = Shop.objects.filter(
        favorited_by__user=user, is_active=True
    ).annotate(
        avg_rating=Avg('reviews__rating',
                       filter=Q(reviews__is_approved=True))
    )[:6]

    notifs = Notification.objects.filter(user=user, is_read=False)[:10]

    return render(request, 'dashboard/client.html', {
        'bookings':      bookings,
        'favorites':     favorites,
        'notifications': notifs,
        'active_tab':    request.GET.get('tab', 'overview'),
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    stats = {
        'users':           User.objects.count(),
        'clients':         User.objects.filter(user_type='client').count(),
        'pros':            User.objects.filter(user_type='pro').count(),
        'shops':           Shop.objects.count(),
        'shops_active':    Shop.objects.filter(is_active=True).count(),
        'bookings':        Booking.objects.count(),
        'bookings_today':  Booking.objects.filter(
            date=timezone.now().date()).count(),
        'reviews_pending': Review.objects.filter(is_approved=False).count(),
        'revenue': Booking.objects.filter(
            status__in=['confirmed', 'completed']
        ).aggregate(total=Sum('total_price'))['total'] or 0,
    }

    return render(request, 'dashboard/admin.html', {
        'stats':           stats,
        'recent_users':    User.objects.order_by('-date_joined')[:10],
        'recent_shops':    Shop.objects.order_by('-created_at')[:10],
        'pending_reviews': Review.objects.filter(
            is_approved=False
        ).select_related('client', 'shop')[:20],
        'active_tab': request.GET.get('tab', 'overview'),
    })


# ══════════════════════════════════════════════
#  PROFIL
# ══════════════════════════════════════════════

@login_required
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name  = request.POST.get('last_name',  user.last_name).strip()
        user.phone      = request.POST.get('phone',      user.phone).strip()
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        user.save()
        messages.success(request, "✅ Profil mis à jour avec succès !")
        return redirect('pro_dashboard' if user.is_pro else 'client_dashboard')
    return render(request, 'accounts/profile_edit.html', {'user': user})