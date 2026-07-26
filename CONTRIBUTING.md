# 🤝 Guide de contribution — BeautyMap Congo

Merci de vouloir contribuer à **BeautyMap Congo** ! 🇨🇬

Ce guide vous aidera à comprendre comment participer au projet de manière efficace et respectueuse.

---

## 📋 Table des matières

1. [Code de conduite](#code-de-conduite)
2. [Comment contribuer](#comment-contribuer)
3. [Signalement de bugs](#signalement-de-bugs)
4. [Suggestion de fonctionnalités](#suggestion-de-fonctionnalités)
5. [Guide de développement](#guide-de-développement)
6. [Processus de Pull Request](#processus-de-pull-request)
7. [Style de code](#style-de-code)
8. [Bonnes pratiques](#bonnes-pratiques)
9. [Questions ?](#questions-)

---

## 📜 Code de conduite

En participant à ce projet, vous acceptez de respecter notre [Code de conduite](CODE_OF_CONDUCT.md) et de maintenir un environnement :
- **Respectueux** envers tous les contributeurs
- **Bienveillant** dans les échanges
- **Constructif** dans les critiques

---

## 🎯 Comment contribuer

Il existe plusieurs façons de contribuer, même sans écrire de code :

| Type de contribution | Compétences requises |
|----------------------|---------------------|
| 🐛 **Signaler un bug** | Aucune — simple observation |
| 💡 **Proposer une idée** | Aucune — créativité |
| 📝 **Améliorer la documentation** | Aucune — rédaction |
| 🎨 **Améliorer le design** | CSS/HTML |
| 🌍 **Traduire l'application** | Anglais/Français/Lingala |
| 💻 **Écrire du code** | Python/Django |
| 🧪 **Tester l'application** | Aucune — exploration |

---

## 🐛 Signalement de bugs

Si vous trouvez un bug, ouvrez une **issue** sur GitHub avec ces informations :

```markdown
### 🐛 Description du bug
Une description claire et concise de ce qui ne va pas.

### 🔄 Étapes pour reproduire
1. Aller sur '...'
2. Cliquer sur '...'
3. Descendre jusqu'à '...'
4. Voir l'erreur

### ✅ Comportement attendu
Une description de ce qui devrait se passer.

### 📸 Captures d'écran
Si possible, ajoutez des captures d'écran.

### 💻 Environnement
- OS : [ex: Windows 11, Ubuntu 22.04]
- Navigateur : [ex: Chrome 120, Firefox 119]
- Version du projet : [ex: v1.0.0]
```
---

### 💡 Suggestion de fonctionnalités

Pour proposer une nouvelle fonctionnalité :

- Vérifiez d'abord qu'elle n'existe pas déjà dans les issues

- Expliquez le besoin : quel problème cela résout-il ?

- Décrivez la solution : comment voyez-vous la fonctionnalité ?

- Ajoutez des exemples si possible

## 💡 Idée de fonctionnalité
Une description claire de la fonctionnalité

|Problème résolu|Solution proposée| Mockup (optionnel)|
|---------------|-----------------|-------------------|
|Quel est le problème que cette fonctionnalité corrige ?|Comment la fonctionnalité devrait-elle fonctionner ?|Ajoutez un croquis ou une maquette.|

---

## 💻 Guide de développement

## 🛠️ Prérequis
Avant de commencer à coder, assurez-vous d'avoir :

|Outil|	Version	|Lien|
|------|--------|---------|
|Python|	3.11+|	python.org|
|Git   |2.0+     |	git-scm.com|
|Docker (optionnel)|	24+|	docker.com|
|PostgreSQL	|15+	[postgresql.org[|


## 🔧 Installation pour le développement

### 1. Cloner le projet
git clone https://github.com/lizagabriela80-afk/beautymap-congo.git
cd beautymap_full

### 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

### 3. Installer les dépendances
pip install -r requirements.txt

### 4. Configurer .env
cp .env.example .env
#### Éditez .env avec vos valeurs

### 5. Migrer la base de données
python manage.py migrate

### 6. Charger les données de test
python manage.py seed_data

### 7. Lancer le serveur
python manage.py runserver


## 🔄 Worlflow de développement

### 1. Créer une branche
git checkout -b feature/nom-de-la-fonctionnalite
### ou
git checkout -b fix/nom-du-bug

### 2. Faire vos modifications

### 3. Tester vos modifications
python manage.py test

### 4. Commiter
git add .
git commit -m "feat: description claire du changement"

### 5. Pusher
git push origin feature/nom-de-la-fonctionnalite

### 6. Ouvrir une Pull Request

---

## 📤 Processus de Pull Request
✅ Critères d'acceptation

Votre PR doit respecter ces critères :

### Critère Exigence

| Tests|	Tous les tests doivent passer|
|Style|	Code conforme au PEP8 et au style du projet|
| Documentation|	Documentation mise à jour si nécessaire|
|Commits|	Messages de commit clairs et en anglais|
| Branche|	À jour avec master|
|Code review|	Au moins 1 approbation d'un mainteneur|



### ✨ Convention de nommage des commits

|Type|	Description	Exemple|
|-----|--------------------|
|feat|	Nouvelle fonctionnalité	feat: add shop search filters|
|fix|	Correction de bug	fix: resolve booking date issue|
|docs|	Documentation	docs: update README with Windows guide|
|style|	Formatage du code (sans impact fonctionnel)	style: format code with black|
|refactor|	Refactorisation (ni correction, ni nouvelle fonction)	refactor: simplify booking logic|
|test|	Ajout ou correction de tests	test: add tests for review model|
|chore|	Maintenance (dépendances, config, etc.)	chore: update requirements.txt|
|perf|	Optimisation des performances	perf: optimize database queries|


## 📝 Exemple de PR 

## 🎯 Objectif
Ajout d'un filtre de recherche par quartier.

## 🛠️ Changements apportés
- Ajout d'un champ `neighborhood` dans le modèle Shop
- Création d'un filtre dans l'API REST
- Mise à jour de la page d'exploration

## ✅ Tests effectués
- [x] Tests unitaires passent
- [x] Testé manuellement en local
- [x] Documentation mise à jour

## 📸 Captures d'écran
[Joindre si nécessaire]

## 🔗 Issue associée
Fixes #123

---

## 🎨 Style de code

|Python (PEP8)|
|python|

# ✅ Bon
def get_shop_by_id(shop_id: int) -> Shop | None:
    """Récupère une boutique par son ID."""
    try:
        return Shop.objects.get(id=shop_id)
    except Shop.DoesNotExist:
        return None

# ❌ Mauvais
def getShopById(id):
    try:
        return Shop.objects.get(id=id)
    except:
        pass
HTML/CSS

html
<!-- ✅ Bon -->
<div class="shop-card">
    <h2 class="shop-title">{{ shop.name }}</h2>
    <p class="shop-address">{{ shop.address }}</p>
</div>

<!-- ❌ Mauvais -->
<div>
    <h2>{{ shop.name }}</h2>
    <p>{{ shop.address }}</p>
</div>
JavaScript
javascript
// ✅ Bon
function toggleFavorite(shopId) {
    const url = `/api/v1/shops/${shopId}/toggle_favorite/`;
    fetch(url, { method: 'POST' })
        .then(response => response.json())
        .then(data => updateUI(data));
}

// ❌ Mauvais
function tf(id) {
    fetch('/api/' + id + '/fav/')
        .then(r => r.json())
        .then(d => { /* ... */ });
}

## 🧪 Bonnes pratiques

Avant de commencer à coder:

- Lisez la documentation du projet

- Vérifiez les issues existantes

- Discutez des changements majeurs avant de coder

- Testez votre code localement

Pendant le développement:

- Écrivez des tests pour chaque nouvelle fonctionnalité

- Documentez votre code (docstrings, commentaires)

- Utilisez des variables claires et explicites

- Optimisez les requêtes (évitez N+1)

- Validez les entrées utilisateur

Avant de soumettre: 

- Relisez votre code une dernière fois

- Exécutez les tests : python manage.py test

- Vérifiez le style : flake8 ou black

- Mettez à jour la documentation si besoin

## ❓ Questions ?

Canaux de communication
Canal	Utilisation
Issues GitHub	Bugs et suggestions
Pull Requests	Propositions de code
Discussions GitHub	Questions et échanges
Avant de demander de l'aide
Lisez la documentation existante

Recherchez dans les issues déjà posées

Essayez de résoudre par vous-même

🎉 Merci !
Votre contribution, aussi petite soit-elle, aide à faire grandir BeautyMap Congo.

"L'union fait la force" — Proverbe congolais 🇨🇬

<div align="center">
Made with ❤️ in Brazzaville, Congo
</div> ```
