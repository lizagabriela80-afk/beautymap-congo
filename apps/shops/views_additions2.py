# ═══════════════════════════════════════════════════════════════
#  À AJOUTER dans apps/shops/views.py
#  (juste avant la fonction pros_page)
# ═══════════════════════════════════════════════════════════════

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
