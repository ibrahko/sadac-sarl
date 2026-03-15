# CI/CD — Guide de mise en place SADAC SARL

## Architecture du pipeline

```
push develop ──► CI (lint → test → security → docker build) ──► Deploy Staging (auto)
push main    ──► CI (lint → test → security → docker build) ──► Deploy Production (approval)
pull request ──► CI (lint → test → security) ──► Review
```

## Fichiers créés

```
.github/
  workflows/
    ci.yml              ← Intégration continue (lint, tests, security, docker)
    cd.yml              ← Déploiement continu (staging + production)
.flake8                 ← Configuration du linter
pytest.ini              ← Configuration des tests
setup.cfg               ← Configuration isort (tri des imports)
Dockerfile              ← Image Docker de production (multi-stage)
docker-compose.yml      ← Environnement de dev local avec PostgreSQL
.dockerignore           ← Fichiers exclus de l'image Docker
Makefile                ← Raccourcis (make lint, make test, etc.)
railway.json            ← Configuration Railway
```

## Étape 1 — Copier les fichiers dans ton projet

Copie tous ces fichiers à la racine de ton projet SADAC :

```bash
# Depuis le dossier où tu as téléchargé les fichiers
cp -r .github/ /chemin/vers/sadac/
cp .flake8 pytest.ini setup.cfg Dockerfile docker-compose.yml .dockerignore Makefile railway.json /chemin/vers/sadac/
```

## Étape 2 — Configurer les secrets GitHub

Va sur : **GitHub → ton repo → Settings → Secrets and variables → Actions**

### Secrets (obligatoires)

| Secret | Description |
|--------|-------------|
| `RAILWAY_TOKEN` | Token API Railway (Railway → Account Settings → Tokens) |

### Variables d'environnement (par environnement)

Crée deux environnements dans **Settings → Environments** :

**Environnement `staging` :**

| Variable | Valeur |
|----------|--------|
| `RAILWAY_STAGING_SERVICE` | Nom du service Railway staging |
| `STAGING_URL` | URL de ton app staging |

**Environnement `production` :**

| Variable | Valeur |
|----------|--------|
| `RAILWAY_PROD_SERVICE` | Nom du service Railway prod |
| `PRODUCTION_URL` | URL de ton app production |

Pour l'environnement production, active **Required reviewers** pour
demander une approbation avant chaque déploiement.

## Étape 3 — Configurer Railway

### Créer deux services sur Railway :

1. **sadac-staging** (branche `develop`)
2. **sadac-production** (branche `main`)

### Variables d'environnement Railway (pour chaque service) :

```
SECRET_KEY=<clé secrète unique>
DEBUG=False                          # True pour staging
ALLOWED_HOSTS=<ton-domaine>.railway.app
DJANGO_SETTINGS_MODULE=sadac.settings.prod

DB_NAME=<fourni par Railway>
DB_USER=<fourni par Railway>
DB_PASSWORD=<fourni par Railway>
DB_HOST=<fourni par Railway>
DB_PORT=5432

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=<ton email>
EMAIL_HOST_PASSWORD=<app password>
DEFAULT_FROM_EMAIL=<ton email>
SADAC_EMAIL=<email sadac>
```

### Obtenir le token Railway :

1. Va sur [railway.app](https://railway.app) → Account Settings → Tokens
2. Crée un token → copie-le
3. Colle-le dans les secrets GitHub sous `RAILWAY_TOKEN`

## Étape 4 — Workflow Git quotidien

```bash
# 1. Travailler sur une branche feature
git checkout develop
git checkout -b feature/ma-fonctionnalite

# 2. Développer, puis vérifier en local
make lint          # Vérifie le code
make test          # Lance les tests

# 3. Commit et push
git add .
git commit -m "feat: description de la fonctionnalité"
git push origin feature/ma-fonctionnalite

# 4. Créer une Pull Request vers develop
#    → Le CI se lance automatiquement
#    → Merge quand c'est vert ✅

# 5. Le merge sur develop déclenche le deploy staging automatiquement

# 6. Si staging OK, créer une PR develop → main
#    → Merge déclenche le deploy production (avec approval)
```

## Commandes utiles

```bash
make help          # Voir toutes les commandes
make lint          # Linter (flake8 + isort)
make format        # Formater le code
make test          # Tests + couverture
make ci-local      # Simuler le CI en local
make docker-up     # Lancer en Docker
make docker-down   # Arrêter Docker
make security      # Vérifier les vulnérabilités
```

## Branches

| Branche | Rôle | Déploiement |
|---------|------|-------------|
| `main` | Production stable | → Railway Production (avec approval) |
| `develop` | Intégration | → Railway Staging (auto) |
| `feature/*` | Développement | → CI uniquement (pas de deploy) |
| `fix/*` | Corrections | → CI uniquement (pas de deploy) |
