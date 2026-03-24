# apps/payments/urls.py
from django.urls import path
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def subscription_plans(request):
    plans = [
        {'id': 'free', 'name': 'Gratuit', 'price': 0, 'features': ['Profil de base', '5 réservations/mois', 'Présence sur la carte']},
        {'id': 'premium', 'name': 'Premium', 'price': 15000, 'features': ['Tout le gratuit', 'Réservations illimitées', 'Statistiques avancées', 'Messagerie', 'Badge vérifié']},
        {'id': 'enterprise', 'name': 'Enterprise', 'price': None, 'features': ['Multi-boutiques', 'API dédiée', 'Support prioritaire', 'Formation']},
    ]
    return JsonResponse({'plans': plans})

urlpatterns = [
    path('abonnements/', subscription_plans, name='subscription_plans'),
]
