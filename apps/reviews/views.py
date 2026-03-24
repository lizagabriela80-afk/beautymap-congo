"""Reviews Views"""
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Review
from apps.shops.models import Shop


@login_required
@require_POST
def submit_review(request, shop_slug):
    import json
    shop = get_object_or_404(Shop, slug=shop_slug)
    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    rating = int(data.get('rating', 0))
    comment = data.get('comment', '').strip()
    title = data.get('title', '').strip()

    if not (1 <= rating <= 5):
        return JsonResponse({'error': 'Note invalide (1-5)'}, status=400)
    if not comment:
        return JsonResponse({'error': 'Commentaire requis'}, status=400)

    review, created = Review.objects.update_or_create(
        client=request.user, shop=shop,
        defaults={'rating': rating, 'comment': comment, 'title': title, 'is_approved': False}
    )
    return JsonResponse({'success': True, 'created': created,
                         'message': 'Avis soumis ! Il sera publié après modération.'})


@login_required
@require_POST
def owner_reply(request, review_id):
    review = get_object_or_404(Review, pk=review_id, shop__owner=request.user)
    import json
    data = json.loads(request.body)
    review.owner_reply = data.get('reply', '')
    review.owner_reply_at = timezone.now()
    review.save()
    return JsonResponse({'success': True})
