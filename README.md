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

```markdown

---

## 📜 Licence Open Source

Ce projet est publié sous la **licence MIT**. Vous êtes libre de :

| Droits | Détails |
|--------|---------|
| ✅ **Usage commercial** | Utiliser le projet dans un cadre professionnel |
| ✅ **Modification** | Adapter le code à vos besoins |
| ✅ **Redistribution** | Partager le projet avec d'autres |
| ✅ **Intégration** | L'incorporer dans vos propres projets (même fermés) |

**La seule condition** est de conserver la mention de copyright et la licence dans vos copies ou redistributions.

> 📄 Voir le fichier [`LICENSE.md`](./LICENSE.md) pour le texte intégral.

---

## 🚀 Démarrage rapide

### Option 1 — Développement local (recommandé)

```bash
git clone https://github.com/lizagabriela80-afk/beautymap-congo.git
cd beautymap_full
chmod +x start.sh
./start.sh dev
```

**Accès :** [http://localhost:8000](http://localhost:8000)

---

### Option 2 — Docker (production-like)

```bash
cp .env.example .env
# Éditez .env avec vos vraies valeurs
./start.sh docker
```

---

### Option 3 — Windows

> 🪟 Un guide détaillé pour Windows avec VS Code est disponible [en bas de ce README](#-guide-windows-avec-vs-code).

---

## 🗂️ Structure du projet

```
beautymap_full/
│
├── beautymap_project/          # ⚙️ Configuration Django
│   ├── settings.py             # Paramètres (DB, Redis, Email, SMS)
│   ├── urls.py                 # Routage principal
│   ├── asgi.py                 # WebSocket (Channels)
│   └── wsgi.py                 # WSGI pour déploiement classique
│
├── apps/                       # 📦 Applications Django
│   ├── accounts/               # Utilisateurs, Auth, OTP, Profils
│   ├── shops/                  # Boutiques, Services, Horaires
│   ├── bookings/               # Réservations, Créneaux
│   ├── reviews/                # Avis et notations
│   ├── messaging/              # Chat WebSocket temps réel
│   ├── notifications/          # Notifications système
│   └── payments/               # Paiements, Abonnements
│
├── templates/                  # 🎨 Templates HTML
│   ├── base/                   # Layout maître et composants
│   ├── public/                 # Pages publiques (home, explore, map, detail)
│   ├── accounts/               # Login, Register, Profile
│   ├── bookings/               # Formulaire + Confirmation RDV
│   ├── dashboard/              # Dashboard pro + client + admin
│   └── messaging/              # Messagerie
│
├── static/                     # 🖌️ Fichiers statiques
│   ├── css/main.css            # Styles complets (1500+ lignes)
│   └── js/main.js              # JavaScript (WebSocket, AJAX, Map)
│
├── fixtures/                   # 📊 Données de test
├── media/                      # 🖼️ Uploads (images boutiques/avatars)
│
├── docker-compose.yml          # 🐳 Orchestration Docker
├── Dockerfile                  # 🐳 Image Docker
├── nginx.conf                  # 🌐 Configuration Nginx
├── requirements.txt            # 📦 Dépendances Python
├── .env.example                # 🔐 Exemple de configuration
├── LICENSE.md                  # 📄 Licence MIT
└── start.sh                    # 🚀 Script de démarrage
```

---

## 🧩 Fonctionnalités complètes

| Module | Fonctionnalités |
|--------|-----------------|
| 🔐 **Auth** | Inscription/connexion email + OTP SMS, JWT API, profils client/pro |
| 🏪 **Boutiques** | CRUD complet, photos, services, horaires, géolocalisation |
| 🗺️ **Carte** | Leaflet + OSM, marqueurs par catégorie, popup interactifs |
| 🔍 **Recherche** | Filtres catégorie, quartier, tri, pagination |
| 📅 **Réservations** | Créneaux dynamiques, confirmation, annulation, SMS |
| ⭐ **Avis** | Notes 1-5★, commentaires, modération, réponse pro |
| 💬 **Messagerie** | Chat WebSocket temps réel, historique, pièces jointes |
| 🔔 **Notifications** | Système push, badge temps réel, marquer comme lu |
| 📊 **Dashboard Pro** | Stats, RDV, services, avis, messages, profil, abonnement |
| 👤 **Dashboard Client** | RDV, favoris, profil, notifications |
| 🛠️ **Admin Django** | Gestion complète utilisateurs, boutiques, avis, statistiques |
| 🌐 **API REST** | Endpoints pour apps mobiles (DRF + Token Auth) |

---

## 🛠️ Stack technique

| Couche | Technologie |
|--------|-------------|
| 🐍 **Backend** | Django 4.2, Django REST Framework |
| 🗄️ **Base de données** | PostgreSQL 15 (SQLite pour dev) |
| ⚡ **Cache/Queue** | Redis 7 |
| 🔌 **WebSocket** | Django Channels 4 |
| 📬 **Tâches async** | Celery 5 |
| 🎨 **Frontend** | HTML5, CSS3 custom, Vanilla JS |
| 🗺️ **Carte** | Leaflet.js + OpenStreetMap |
| 🌐 **Serveur web** | Nginx + Daphne/Gunicorn |
| 🐳 **Conteneurs** | Docker + Docker Compose |
| 🔑 **Auth** | Session + Token (DRF) + OTP SMS |

---

## 🔑 Comptes de test

Après `./start.sh dev` :

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| 👑 **Admin** | `admin@beautymap.cg` | `Admin@123!` |
| 💇 **Pro (coiffure)** | `marie.kouba@beautymap.cg` | `Pro@123!` |
| ✂️ **Pro (barbier)** | `pascal.barber@beautymap.cg` | `Pro@123!` |
| 👩 **Client** | `amelie.koumba@gmail.com` | `Client@123!` |
| 👩 **Client** | `sandra.mpanu@gmail.com` | `Client@123!` |

---

## 🌐 API REST

**Base URL :** `/api/v1/`

### 🔐 Authentification

```
POST   /api/v1/auth/register/          Créer un compte
POST   /api/v1/auth/login/             Connexion → token
GET    /api/v1/auth/me/                Profil connecté
```

### 🏪 Boutiques

```
GET    /api/v1/shops/                  Liste boutiques (filtres: category, quartier)
GET    /api/v1/shops/{id}/             Détail boutique
POST   /api/v1/shops/                  Créer boutique (pro auth)
GET    /api/v1/shops/map_markers/      Données carte (lat/lng)
POST   /api/v1/shops/{id}/toggle_favorite/  Favori
```

### 📅 Réservations

```
GET    /api/v1/bookings/               Mes réservations
POST   /api/v1/bookings/               Créer réservation
```

### ⭐ Avis

```
GET    /api/v1/reviews/?shop={id}      Avis d'une boutique
POST   /api/v1/reviews/                Soumettre un avis
```

---

## ⚙️ Configuration `.env`

```env
# Django
SECRET_KEY=votre-clé-secrète
DEBUG=False
ALLOWED_HOSTS=beautymapcongo.com,www.beautymapcongo.com

# Base de données
DB_NAME=beautymap_db
DB_USER=beautymap_user
DB_PASSWORD=mot-de-passe
DB_HOST=localhost

# Cache
REDIS_URL=redis://localhost:6379

# SMS (Africa's Talking)
AT_API_KEY=votre-clé-api
AT_USERNAME=sandbox

# Email SMTP
EMAIL_HOST_USER=votre@gmail.com
EMAIL_HOST_PASSWORD=votre-app-password
```

---

## 📱 Déploiement en production

```bash
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
```

---

# 🪟 Guide Windows avec VS Code

> Toutes les commandes sont à taper dans le **Terminal intégré de VS Code** (`Ctrl + ù`)

---

### ✅ Étape 1 — Installer les prérequis

| Logiciel | Lien | Note importante |
|----------|------|-----------------|
| **Python 3.11** | https://python.org/downloads | ⚠️ Cocher **"Add Python to PATH"** |
| **VS Code** | https://code.visualstudio.com | |
| **Git** | https://git-scm.com/download/win | Optionnel |

Vérifie Python :

```cmd
python --version
```
Résultat attendu : `Python 3.11.x`

---

### ✅ Étape 2 — Ouvrir le projet

1. Fais un clic droit sur le ZIP → **Extraire tout** → choisis `C:\beautymap`
2. Dans VS Code : **Fichier → Ouvrir le dossier** → sélectionne `C:\beautymap\beautymap_full`
3. Ouvre le terminal : `Ctrl + ù`

---

### ✅ Étape 3 — Modifier `settings.py` (obligatoire sur Windows)

Ouvre `beautymap_project\settings.py` et fais **2 modifications** :

**1️⃣ Utiliser SQLite au lieu de PostgreSQL**

Commente le bloc PostgreSQL :

```python
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         ...
#     }
# }
```

Décommente le bloc SQLite :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**2️⃣ Désactiver Redis**

Remplace `CHANNEL_LAYERS` par :

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
```

**Sauvegarde :** `Ctrl + S`

---

### ✅ Étape 4 — Créer le fichier `.env`

```cmd
echo SECRET_KEY=beautymap-secret-key-windows-dev-2025 > .env
echo DEBUG=True >> .env
echo ALLOWED_HOSTS=* >> .env
```

Vérifie :

```cmd
type .env
```

---

### ✅ Étape 5 — Créer le virtualenv

```cmd
python -m venv venv
venv\Scripts\activate
```

Tu vois `(venv)` devant le prompt ✅

> ⚠️ **Erreur "l'exécution de scripts est désactivée" ?**
> ```cmd
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Réponds `O` (Oui), puis relance `venv\Scripts\activate`

---

### ✅ Étape 6 — Installer les dépendances

```cmd
pip install django==4.2.7 djangorestframework==3.14.0
pip install pillow django-cors-headers python-decouple
pip install django-crispy-forms crispy-bootstrap5 django-filter
pip install channels whitenoise
```

> ℹ️ Les erreurs sur `psycopg2-binary`, `channels-redis` ou `celery` sont **normales** — ignorez-les !

---

### ✅ Étape 7 — Créer les tables

```cmd
python manage.py migrate
```

---

### ✅ Étape 8 — Charger les données de test

```cmd
python manage.py seed_data
```

Résultat attendu :

```
🌱 Seeding BeautyMap Congo data...
  Creating users...    ✓ 3 professionals, 5 clients
  Creating shops...    ✓ 6 shops with services and schedules
✅ Data seeded successfully!
```

---

### ✅ Étape 9 — Préparer les fichiers statiques

```cmd
python manage.py collectstatic --noinput
```

---

### ✅ Étape 10 — Lancer le serveur 🚀

```cmd
python manage.py runserver
```

Ouvre **http://127.0.0.1:8000** ✅

Pour arrêter : `Ctrl + C`

---

### 🔄 Commandes du quotidien

```cmd
venv\Scripts\activate
python manage.py runserver
```

---

### 📋 Installation en une fois (copier-coller)

```cmd
python -m venv venv
venv\Scripts\activate
pip install django==4.2.7 djangorestframework==3.14.0 pillow django-cors-headers python-decouple django-crispy-forms crispy-bootstrap5 django-filter channels whitenoise
python manage.py migrate
python manage.py seed_data
python manage.py collectstatic --noinput
python manage.py runserver
```

---

### ❗ Erreurs fréquentes sur Windows

| Erreur | Cause | Solution |
|--------|-------|----------|
| `'python' n'est pas reconnu` | Python pas dans PATH | Réinstalle Python en cochant **"Add to PATH"** |
| `activate` bloqué | Politique d'exécution | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `No module named 'X'` | Package manquant | `pip install X` |
| `That port is already in use` | Port 8000 occupé | `python manage.py runserver 8080` |
| Erreur `psycopg2` | Package PostgreSQL | Normal, ignore (tu utilises SQLite) |
| Erreur `channels_redis` | Redis pas installé | Vérifie `InMemoryChannelLayer` (Étape 3) |
| `UnicodeDecodeError` | Encodage Windows | `chcp 65001` avant de lancer |
| `(venv)` disparaît | Terminal fermé | Retape `venv\Scripts\activate` |

---

### 🌐 URLs importantes

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/ | Page d'accueil |
| http://127.0.0.1:8000/explorer/ | Rechercher des boutiques |
| http://127.0.0.1:8000/carte/ | Carte interactive |
| http://127.0.0.1:8000/auth/login/ | Connexion |
| http://127.0.0.1:8000/auth/register/ | Inscription |
| http://127.0.0.1:8000/dashboard/ | Dashboard (redirige selon le rôle) |
| http://127.0.0.1:8000/admin/ | Interface admin Django |
| http://127.0.0.1:8000/api/v1/shops/ | API REST boutiques |


## 🤝 Contribuer

Les contributions sont les bienvenues ! 🎉

1. 🍴 **Fork** le projet
2. 🌿 Créez une branche : `git checkout -b feature/amazing-feature`
3. 💾 **Commit** : `git commit -m 'Add some amazing feature'`
4. 📤 **Push** : `git push origin feature/amazing-feature`
5. 🔄 Ouvrez une **Pull Request**

> Consultez notre [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) avant de contribuer.

---

## 🙏 Remerciements

Un grand merci à :

- [Django](https://www.djangoproject.com/) & [Django REST Framework](https://www.django-rest-framework.org/) — pour ce framework exceptionnel
- [Leaflet](https://leafletjs.com/) & [OpenStreetMap](https://www.openstreetmap.org/) — pour la cartographie libre
- [Africa's Talking](https://africastalking.com/) — pour les solutions SMS en Afrique
- **Toutes les personnes** qui ont contribué, testé ou soutenu ce projet 🇨🇬

---

## 📞 Contact & Support

| | |
|---|---|
| **Auteur** | [@lizagabriela80-afk](https://github.com/lizagabriela80-afk) |
| **Email** | lizagabriela84@gmail.com |
| **Issues** | [Signaler un problème](https://github.com/lizagabriela80-afk/beautymap-congo/issues) |

---

## 🇨🇬 Made in Brazzaville, Congo

<div align="center">

**BeautyMap Congo** — © 2026 · Sous licence MIT

*Fierté congolaise* ❤️💛💚

</div>

---

