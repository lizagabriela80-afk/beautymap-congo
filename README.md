# 💄 BeautyMap Congo

> La première plateforme congolaise dédiée aux professionnels de la beauté et de la mode à Brazzaville.

---

## 🚀 Démarrage rapide

### Option 1 — Développement local (recommandé)

```bash
git clone https://github.com/lizagabriela80-afk/beautymap-congo.git
cd beautymap_full
chmod +x start.sh
./start.sh dev
```

Accès : **http://localhost:8000**

### Option 2 — Docker (production-like)

```bash
cp .env.example .env
# Éditez .env avec vos vraies valeurs
./start.sh docker
```

---

## 🗂️ Structure du projet

```
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
└── start.sh
```

---

## 🧩 Fonctionnalités complètes

| Module | Fonctionnalités |
|--------|----------------|
| **Auth** | Inscription/connexion email + OTP SMS, JWT API, profils client/pro |
| **Boutiques** | CRUD complet, photos, services, horaires, géolocalisation |
| **Carte** | Leaflet + OSM, marqueurs par catégorie, popup interactifs |
| **Recherche** | Filtres catégorie, quartier, tri, pagination |
| **Réservations** | Créneaux dynamiques, confirmation, annulation, SMS |
| **Avis** | Notes 1-5★, commentaires, modération, réponse pro |
| **Messagerie** | Chat WebSocket temps réel, historique, pièces jointes |
| **Notifications** | Système push, badge temps réel, marquer comme lu |
| **Dashboard Pro** | Stats, RDV, services, avis, messages, profil, abonnement |
| **Dashboard Client** | RDV, favoris, profil, notifications |
| **Admin Django** | Gestion complète utilisateurs, boutiques, avis, statistiques |
| **API REST** | Endpoints pour apps mobiles (DRF + Token Auth) |

---

## 🛠️ Stack technique

| Couche | Technologie |
|--------|-------------|
| **Backend** | Django 4.2, Django REST Framework |
| **Base de données** | PostgreSQL 15 (SQLite pour dev) |
| **Cache/Queue** | Redis 7 |
| **WebSocket** | Django Channels 4 |
| **Tâches async** | Celery 5 |
| **Frontend** | HTML5, CSS3 custom, Vanilla JS |
| **Carte** | Leaflet.js + OpenStreetMap |
| **Serveur web** | Nginx + Daphne/Gunicorn |
| **Conteneurs** | Docker + Docker Compose |
| **Auth** | Session + Token (DRF) + OTP SMS |

---

## 🔑 Comptes de test

Après `./start.sh dev` :

| Rôle | Email | Mot de passe |
|------|-------|-------------|
| Admin | admin@beautymap.cg | Admin@123! |
| Pro (coiffure) | marie.kouba@beautymap.cg | Pro@123! |
| Pro (barbier) | pascal.barber@beautymap.cg | Pro@123! |
| Client | amelie.koumba@gmail.com | Client@123! |
| Client | sandra.mpanu@gmail.com | Client@123! |

---

## 🌐 API REST

Base URL : `/api/v1/`

```
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
```

---

## ⚙️ Configuration .env

```env
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

## 🇨🇬 Made in Brazzaville, Congo

BeautyMap Congo — © 2025 · Tous droits réservés


# 💄 BeautyMap Congo

> La première plateforme congolaise dédiée aux professionnels de la beauté et de la mode à Brazzaville.

---

## 🪟 Démarrage sur Windows avec VS Code

> Toutes les commandes sont à taper dans le **Terminal intégré de VS Code**
> Ouvre-le avec : `Ctrl + ù`  ou menu **Terminal → Nouveau terminal**

---

### ✅ Étape 1 — Installer les prérequis

| Logiciel | Lien | Note importante |
|----------|------|-----------------|
| **Python 3.11** | https://python.org/downloads | ⚠️ Cocher **"Add Python to PATH"** |
| **VS Code** | https://code.visualstudio.com | |
| **Git** | https://git-scm.com/download/win | Optionnel |

Vérifie Python dans le terminal VS Code :
```cmd
python --version
```
Résultat attendu : `Python 3.11.x`

---

### ✅ Étape 2 — Ouvrir le projet dans VS Code

1. Fais un clic droit sur le ZIP → **Extraire tout** → choisis `C:\beautymap`
2. Dans VS Code : **Fichier → Ouvrir le dossier** → sélectionne `C:\beautymap\beautymap_full`
3. Ouvre le terminal : `Ctrl + ù`

---

### ✅ Étape 3 — Modifier `settings.py` (obligatoire sur Windows)

Ouvre `beautymap_project\settings.py` dans VS Code et fais **2 modifications** :

**Modification 1 — Utiliser SQLite au lieu de PostgreSQL**

Trouve le bloc PostgreSQL (ligne ~73) et ajoute `#` devant chaque ligne :

```python
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('DB_NAME', default='beautymap_db'),
#         'USER': config('DB_USER', default='beautymap_user'),
#         'PASSWORD': config('DB_PASSWORD', default='beautymap_pass'),
#         'HOST': config('DB_HOST', default='localhost'),
#         'PORT': config('DB_PORT', default='5432'),
#     }
# }
```

Puis trouve le bloc SQLite commenté (ligne ~84) et enlève les `#` :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Modification 2 — Désactiver Redis (pas nécessaire en dev)**

Trouve `CHANNEL_LAYERS` (ligne ~139) et remplace tout le bloc par :

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
```

Sauvegarde : `Ctrl + S`

---

### ✅ Étape 4 — Créer le fichier `.env`

Dans le terminal VS Code, tape ces commandes **une par une** :

```cmd
echo SECRET_KEY=beautymap-secret-key-windows-dev-2025 > .env
echo DEBUG=True >> .env
echo ALLOWED_HOSTS=* >> .env
```

Vérifie le résultat :
```cmd
type .env
```

---

### ✅ Étape 5 — Créer le virtualenv

```cmd
python -m venv venv
```

```cmd
venv\Scripts\activate
```

Tu vois `(venv)` devant le prompt — c'est bon ✅

> ⚠️ **Erreur "l'exécution de scripts est désactivée"** ? Tape d'abord :
> ```cmd
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Réponds `O` (Oui), puis relance `venv\Scripts\activate`

---

### ✅ Étape 6 — Installer les dépendances

Installe par groupes (plus sûr sur Windows) :

```cmd
pip install django==4.2.7 djangorestframework==3.14.0
```

```cmd
pip install pillow django-cors-headers python-decouple
```

```cmd
pip install django-crispy-forms crispy-bootstrap5 django-filter
```

```cmd
pip install channels whitenoise
```

> ℹ️ Des erreurs sur `psycopg2-binary`, `channels-redis` ou `celery` ? **Ignore-les** — ce sont des packages de production non nécessaires sur Windows en dev local.

---

### ✅ Étape 7 — Créer les tables de la base de données

```cmd
python manage.py migrate
```

Tu verras une série de `OK` — normal ✅

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

Ouvre **http://127.0.0.1:8000** dans ton navigateur ✅

Pour arrêter : `Ctrl + C` dans le terminal.

---

## 🔄 Commandes du quotidien

À chaque fois que tu rouvres VS Code pour travailler sur le projet :

```cmd
venv\Scripts\activate
python manage.py runserver
```

---

## 📋 Installation complète en une fois (copier-coller)

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

## 🔑 Comptes de test

| Rôle | Email | Mot de passe | Accès |
|------|-------|-------------|-------|
| **Admin** | `admin@beautymap.cg` | `Admin@123!` | http://127.0.0.1:8000/admin/ |
| **Pro (coiffure)** | `marie.kouba@beautymap.cg` | `Pro@123!` | http://127.0.0.1:8000/dashboard/ |
| **Pro (barbier)** | `pascal.barber@beautymap.cg` | `Pro@123!` | http://127.0.0.1:8000/dashboard/ |
| **Client** | `amelie.koumba@gmail.com` | `Client@123!` | http://127.0.0.1:8000/dashboard/ |
| **Client** | `sandra.mpanu@gmail.com` | `Client@123!` | http://127.0.0.1:8000/dashboard/ |

---

## ❗ Erreurs fréquentes sur Windows

| Erreur | Cause | Solution |
|--------|-------|----------|
| `'python' n'est pas reconnu` | Python pas dans PATH | Réinstalle Python en cochant **"Add to PATH"** |
| `activate` bloqué | Politique d'exécution | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `No module named 'X'` | Package manquant | `pip install X` |
| `That port is already in use` | Port 8000 occupé | `python manage.py runserver 8080` |
| Erreur `psycopg2` | Package PostgreSQL | Normal, ignore (tu utilises SQLite) |
| Erreur `channels_redis` | Redis pas installé | Vérifie que tu as mis `InMemoryChannelLayer` (Étape 3) |
| `UnicodeDecodeError` | Encodage Windows | Tape `chcp 65001` avant de lancer le serveur |
| `(venv)` disparaît | Terminal fermé | Retape `venv\Scripts\activate` |

---

## 🌐 URLs importantes

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

---

## 🗂️ Structure du projet

```
beautymap_full/
├── beautymap_project/
│   ├── settings.py      ⚙️  Modifier SQLite + InMemoryChannelLayer
│   ├── urls.py          Routage principal
│   ├── asgi.py          WebSocket
│   └── wsgi.py          WSGI
├── apps/
│   ├── accounts/        Utilisateurs, Auth, OTP, Profils
│   ├── shops/           Boutiques, Services, Horaires
│   ├── bookings/        Réservations, Créneaux
│   ├── reviews/         Avis et notations
│   ├── messaging/       Chat WebSocket temps réel
│   ├── notifications/   Notifications système
│   └── payments/        Paiements, Abonnements
├── templates/           Pages HTML (home, explore, map, dashboard...)
├── static/
│   ├── css/main.css     Styles complets (1 500+ lignes)
│   └── js/main.js       JavaScript (WebSocket, AJAX, Leaflet)
├── fixtures/            Données de test JSON
├── .env                 ⚙️  À créer (voir Étape 4)
├── manage.py            Commandes Django
└── requirements.txt     Liste des dépendances
```

---

## 🧩 Fonctionnalités

| Module | Fonctionnalités |
|--------|----------------|
| **Auth** | Inscription/connexion email + OTP SMS, profils client/pro |
| **Boutiques** | CRUD complet, photos, services, horaires, géolocalisation |
| **Carte** | Leaflet + OpenStreetMap, marqueurs par catégorie |
| **Recherche** | Filtres catégorie, quartier, tri, pagination |
| **Réservations** | Créneaux dynamiques, confirmation, annulation |
| **Avis** | Notes 1-5★, commentaires, modération, réponse pro |
| **Messagerie** | Chat temps réel (WebSocket), historique |
| **Notifications** | Système push, badges, marquer comme lu |
| **Dashboard Pro** | Stats, RDV, services, avis, messages, abonnement |
| **Dashboard Client** | RDV, favoris, profil, notifications |
| **Admin Django** | Gestion complète via `/admin/` |
| **API REST** | Endpoints JSON pour applications mobiles |

---

## 🛠️ Stack technique

| Couche | Technologie |
|--------|-------------|
| **Backend** | Django 4.2, Django REST Framework |
| **Base de données** | SQLite (dev Windows) / PostgreSQL (production) |
| **WebSocket** | Django Channels 4 (InMemory en dev) |
| **Frontend** | HTML5, CSS3 custom, Vanilla JS |
| **Carte** | Leaflet.js + OpenStreetMap |
| **Serveur web** | Nginx + Gunicorn (production) |
| **Conteneurs** | Docker + Docker Compose (production) |

---

## 🌐 API REST

Base URL : `/api/v1/`

```
POST   /api/v1/auth/register/               Créer un compte
POST   /api/v1/auth/login/                  Connexion → token
GET    /api/v1/auth/me/                     Profil connecté

GET    /api/v1/shops/                       Liste boutiques (filtres: category, quartier)
GET    /api/v1/shops/{id}/                  Détail boutique
POST   /api/v1/shops/                       Créer boutique (pro auth)
GET    /api/v1/shops/map_markers/           Données carte lat/lng
POST   /api/v1/shops/{id}/toggle_favorite/  Ajouter/retirer favori

GET    /api/v1/bookings/                    Mes réservations
POST   /api/v1/bookings/                    Créer une réservation

GET    /api/v1/reviews/?shop={id}           Avis d'une boutique
POST   /api/v1/reviews/                     Soumettre un avis
```

---

## 🐳 Déploiement en production (Docker)

> Nécessite **Docker Desktop** : https://www.docker.com/products/docker-desktop/

```cmd
copy .env.example .env
docker compose up --build -d
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed_data
docker compose logs -f web
```

---

## ⚙️ Configuration `.env` pour la production

```env
SECRET_KEY=votre-cle-secrete-tres-longue-et-unique
DEBUG=False
ALLOWED_HOSTS=beautymapcongo.com,www.beautymapcongo.com

DB_NAME=beautymap_db
DB_USER=beautymap_user
DB_PASSWORD=mot-de-passe-fort
DB_HOST=localhost

REDIS_URL=redis://localhost:6379

AT_API_KEY=votre-cle-api-africastalking
AT_USERNAME=sandbox

EMAIL_HOST_USER=votre@gmail.com
EMAIL_HOST_PASSWORD=votre-app-password
```

---

## 🇨🇬 Made in Brazzaville, Congo

BeautyMap Congo — © 2025 · Tous droits réservés