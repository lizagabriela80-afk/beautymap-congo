# 💄 BeautyMap Congo

> La première plateforme congolaise dédiée aux professionnels de la beauté et de la mode à Brazzaville.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)

---

## 📜 Licence Open Source

Ce projet est publié sous la **licence MIT**, ce qui signifie que vous êtes libre de :
- ✅ L'utiliser à des fins commerciales
- ✅ Le modifier et l'adapter à vos besoins
- ✅ Le distribuer
- ✅ L'intégrer dans d'autres projets (même fermés)

**La seule condition** est de conserver la mention de copyright et la licence dans vos copies ou redistributions.

> Voir le fichier [`LICENSE.md`](./LICENSE.md) pour le texte intégral.

---

## 🚀 Démarrage rapide

### Option 1 — Développement local (recommandé)

```bash
git clone https://github.com/lizagabriela80-afk/beautymap-congo.git

Option 2 — Docker (production-like)
bash
cp .env.example .env
# Éditez .env avec vos vraies valeurs
./start.sh docker
cd beautymap_full
chmod +x start.sh
./start.sh dev

🗂️ Structure du projet
text
beautymap_full/
├── beautymap_project/          # Config Django
│   ├── settings.py             # Paramètres (DB, Redis, Email, SMS)
│   ├── urls.py                 # Routage principal
│   ├── asgi.py                 # WebSocket (Channels)
│   └── wsgi.py                 # WSGI pour déploiement classique
│
├── apps/
│   ├── accounts/               # Utilisateurs, Auth, OTP, Profils
│   ├── shops/                  # Boutiques, Services, Horaires
│   ├── bookings/               # Réservations, Créneaux
│   ├── reviews/                # Avis et notations
│   ├── messaging/              # Chat WebSocket temps réel
│   ├── notifications/          # Notifications système
│   └── payments/               # Paiements, Abonnements
│
├── templates/
│   ├── base/base.html          # Layout maître
│   ├── base/shop_card.html     # Carte boutique réutilisable
│   ├── public/                 # Pages publiques (home, explore, map, detail)
│   ├── accounts/               # Login, Register, Profile
│   ├── bookings/               # Formulaire + Confirmation RDV
│   ├── dashboard/              # Dashboard pro + client + admin
│   └── messaging/              # Messagerie
│
├── static/
│   ├── css/main.css            # Styles complets (1500+ lignes)
│   └── js/main.js              # JavaScript (WebSocket, AJAX, Map)
│
├── fixtures/                   # Données de test
├── media/                      # Uploads (images boutiques/avatars)
├── docker-compose.yml
├── Dockerfile
├── nginx.conf
├── requirements.txt
├── .env.example
├── LICENSE.md                  # Licence MIT
└── start.sh
🧩 Fonctionnalités complètes
Module	Fonctionnalités
Auth	Inscription/connexion email + OTP SMS, JWT API, profils client/pro
Boutiques	CRUD complet, photos, services, horaires, géolocalisation
Carte	Leaflet + OSM, marqueurs par catégorie, popup interactifs
Recherche	Filtres catégorie, quartier, tri, pagination
Réservations	Créneaux dynamiques, confirmation, annulation, SMS
Avis	Notes 1-5★, commentaires, modération, réponse pro
Messagerie	Chat WebSocket temps réel, historique, pièces jointes
Notifications	Système push, badge temps réel, marquer comme lu
Dashboard Pro	Stats, RDV, services, avis, messages, profil, abonnement
Dashboard Client	RDV, favoris, profil, notifications
Admin Django	Gestion complète utilisateurs, boutiques, avis, statistiques
API REST	Endpoints pour apps mobiles (DRF + Token Auth)
🛠️ Stack technique
Couche	Technologie
Backend	Django 4.2, Django REST Framework
Base de données	PostgreSQL 15 (SQLite pour dev)
Cache/Queue	Redis 7
WebSocket	Django Channels 4
Tâches async	Celery 5
Frontend	HTML5, CSS3 custom, Vanilla JS
Carte	Leaflet.js + OpenStreetMap
Serveur web	Nginx + Daphne/Gunicorn
Conteneurs	Docker + Docker Compose
Auth	Session + Token (DRF) + OTP SMS
🔑 Comptes de test
Après ./start.sh dev :

Rôle	Email	Mot de passe
Admin	admin@beautymap.cg	Admin@123!
Pro (coiffure)	marie.kouba@beautymap.cg	Pro@123!
Pro (barbier)	pascal.barber@beautymap.cg	Pro@123!
Client	amelie.koumba@gmail.com	Client@123!
Client	sandra.mpanu@gmail.com	Client@123!
🌐 API REST
Base URL : /api/v1/

text
POST   /api/v1/auth/register/          Créer un compte
POST   /api/v1/auth/login/             Connexion → token
GET    /api/v1/auth/me/                Profil connecté

GET    /api/v1/shops/                  Liste boutiques (filtres: category, quartier)
GET    /api/v1/shops/{id}/             Détail boutique
POST   /api/v1/shops/                  Créer boutique (pro auth)
GET    /api/v1/shops/map_markers/      Données carte (lat/lng)
POST   /api/v1/shops/{id}/toggle_favorite/  Favori

GET    /api/v1/bookings/               Mes réservations
POST   /api/v1/bookings/               Créer réservation

GET    /api/v1/reviews/?shop={id}      Avis d'une boutique
POST   /api/v1/reviews/                Soumettre un avis
⚙️ Configuration .env
env
SECRET_KEY=votre-clé-secrète
DEBUG=False
ALLOWED_HOSTS=beautymapcongo.com,www.beautymapcongo.com

DB_NAME=beautymap_db
DB_USER=beautymap_user
DB_PASSWORD=mot-de-passe
DB_HOST=localhost

REDIS_URL=redis://localhost:6379

# SMS (Africa's Talking)
AT_API_KEY=votre-clé-api
AT_USERNAME=sandbox

# Email SMTP
EMAIL_HOST_USER=votre@gmail.com
EMAIL_HOST_PASSWORD=votre-app-password
📱 Déploiement en production
bash
# 1. Configurer le .env
cp .env.example .env && nano .env

# 2. Lancer avec Docker
docker compose up --build -d

# 3. Créer le superadmin
docker compose exec web python manage.py createsuperuser

# 4. Charger les données de test (optionnel)
docker compose exec web python manage.py seed_data

# 5. Vérifier les logs
docker compose logs -f web
🤝 Contribuer
Les contributions sont les bienvenues ! Voici comment faire :

- Fork le projet

- Créez une branche pour votre fonctionnalité (git checkout -b feature/amazing-feature)

- Commit vos changements (git commit -m 'Add some amazing feature')

- Push sur la branche (git push origin feature/amazing-feature)

- Ouvrez une Pull Request

- Consultez notre CODE_OF_CONDUCT.md avant de contribuer.



🙏 Remerciements
Django & Django REST Framework

Leaflet & OpenStreetMap

Africa's Talking pour les SMS

Toutes les personnes qui ont contribué, testé ou soutenu ce projet 🇨🇬

🇨🇬 Made in Brazzaville, Congo
BeautyMap Congo — © 2026 · Sous licence MIT
