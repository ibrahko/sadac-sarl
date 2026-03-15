# ============================================================
# Dockerfile — Production SADAC SARL
# Multi-stage build pour une image légère
# ============================================================

# ── Stage 1 : Builder ──
FROM python:3.12-slim AS builder

WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2 : Production ──
FROM python:3.12-slim

# Créer un utilisateur non-root
RUN groupadd -r sadac && useradd -r -g sadac sadac

WORKDIR /app

# Dépendances runtime uniquement
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

# Copier les dépendances Python du builder
COPY --from=builder /install /usr/local

# Copier le code source
COPY . .

# Collecter les fichiers statiques
RUN SECRET_KEY=build-only \
    DEBUG=False \
    ALLOWED_HOSTS=* \
    CSRF_TRUSTED_ORIGINS=https://example.com \
    EMAIL_HOST=x EMAIL_PORT=587 \
    EMAIL_HOST_USER=x EMAIL_HOST_PASSWORD=x \
    DEFAULT_FROM_EMAIL=x SADAC_EMAIL=x \
    DB_NAME=x DB_USER=x DB_PASSWORD=x \
    DB_HOST=x DB_PORT=5432 \
    CLOUDINARY_CLOUD_NAME=x \
    CLOUDINARY_API_KEY=x \
    CLOUDINARY_API_SECRET=x \
    DJANGO_SETTINGS_MODULE=sadac.settings.prod \
    python manage.py collectstatic --no-input 2>&1 || true

RUN ls -la /app/staticfiles/ && ls -la /app/staticfiles/img/ || echo "STATIC FILES MISSING"


# Créer les dossiers nécessaires
RUN mkdir -p /app/media /app/staticfiles /app/logs && \
    chown -R sadac:sadac /app

# Passer à l'utilisateur non-root
USER sadac

# Exposer le port
EXPOSE ${PORT:-8000}



# Démarrage avec Gunicorn
CMD python manage.py migrate --no-input && gunicorn sadac.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120 --access-logfile - --error-logfile -
