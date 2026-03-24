#!/bin/bash
# ============================================================
# BEAUTYMAP CONGO — Script de démarrage
# ============================================================

set -e
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "  ██████╗ ███████╗ █████╗ ██╗   ██╗████████╗██╗   ██╗"
echo "  ██╔══██╗██╔════╝██╔══██╗██║   ██║╚══██╔══╝╚██╗ ██╔╝"
echo "  ██████╔╝█████╗  ███████║██║   ██║   ██║    ╚████╔╝ "
echo "  ██╔══██╗██╔══╝  ██╔══██║██║   ██║   ██║     ╚██╔╝  "
echo "  ██████╔╝███████╗██║  ██║╚██████╔╝   ██║      ██║   "
echo "  ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝    ╚═╝      ╚═╝   "
echo -e "  ${GREEN}MAP CONGO${BLUE} — Plateforme Beauté & Mode 🇨🇬${NC}"
echo ""

MODE=${1:-dev}

check_dependency() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 n'est pas installé.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ $1${NC}"
}

# ---- MODE DEV ----
if [ "$MODE" = "dev" ]; then
    echo -e "${YELLOW}🚀 Démarrage en mode DÉVELOPPEMENT${NC}"
    echo ""

    echo "🔍 Vérification des dépendances..."
    check_dependency python3
    check_dependency pip

    # Créer le .env si absent
    if [ ! -f .env ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Fichier .env créé depuis .env.example — veuillez le configurer${NC}"
    fi

    # Virtualenv
    if [ ! -d "venv" ]; then
        echo "🐍 Création du virtualenv..."
        python3 -m venv venv
    fi
    source venv/bin/activate

    # Install deps
    echo "📦 Installation des dépendances..."
    pip install -r requirements.txt -q

    # Use SQLite for dev
    export DJANGO_SETTINGS_MODULE=beautymap_project.settings
    sed -i 's/# DATABASES = {/DATABASES = {/' beautymap_project/settings.py 2>/dev/null || true
    
    echo "🗄️  Migration de la base de données..."
    python manage.py migrate --run-syncdb 2>&1 | tail -5

    echo "📁 Collecte des fichiers statiques..."
    python manage.py collectstatic --noinput -v 0

    echo "🌱 Seeding des données de test..."
    python manage.py seed_data 2>&1 | grep -E "(✓|❌|Error)"

    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}✅ BeautyMap Congo est prêt !${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "🌐 Site web:     ${BLUE}http://localhost:8000${NC}"
    echo -e "⚙️  Admin:        ${BLUE}http://localhost:8000/admin/${NC}"
    echo -e "🔑 Admin login:  ${BLUE}admin@beautymap.cg / Admin@123!${NC}"
    echo -e "👩 Pro login:    ${BLUE}marie.kouba@beautymap.cg / Pro@123!${NC}"
    echo -e "👤 Client login: ${BLUE}amelie.koumba@gmail.com / Client@123!${NC}"
    echo ""
    echo "▶️  Démarrage du serveur Django..."
    python manage.py runserver 0.0.0.0:8000

# ---- MODE DOCKER ----
elif [ "$MODE" = "docker" ]; then
    echo -e "${YELLOW}🐳 Démarrage avec Docker Compose${NC}"
    check_dependency docker

    if [ ! -f .env ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Configurez le fichier .env avant de continuer${NC}"
        exit 1
    fi

    docker compose up --build -d
    echo ""
    echo -e "${GREEN}✅ BeautyMap Congo démarre en arrière-plan.${NC}"
    echo -e "🌐 http://localhost (via Nginx)"
    echo -e "📊 Logs: docker compose logs -f web"

# ---- MODE PROD ----
elif [ "$MODE" = "prod" ]; then
    echo -e "${YELLOW}🔒 Démarrage en mode PRODUCTION${NC}"
    source venv/bin/activate
    python manage.py migrate --no-input
    python manage.py collectstatic --no-input
    gunicorn beautymap_project.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        --access-logfile - \
        --error-logfile - \
        --timeout 120

else
    echo "Usage: ./start.sh [dev|docker|prod]"
    exit 1
fi
