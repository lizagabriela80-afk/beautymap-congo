# ═══════════════════════════════════════════════════════════════
#  apps/shops/views.py — AJOUTS (ajouter à la fin du fichier existant)
# ═══════════════════════════════════════════════════════════════

# Ajouter ces imports en haut du fichier existant :
# from apps.payments.models import Subscription

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
