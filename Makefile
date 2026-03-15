# ============================================================
# Makefile — Raccourcis SADAC SARL
# ============================================================

.PHONY: help install lint format test run migrate docker-up docker-down

help: ## Afficher l'aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Dev local ──

install: ## Installer les dépendances
	pip install -r requirements.txt
	pip install flake8 isort pytest pytest-django pytest-cov pip-audit

lint: ## Vérifier la qualité du code
	flake8 .
	isort --check-only --diff .

format: ## Formater le code automatiquement
	isort .

test: ## Lancer les tests avec couverture
	pytest --cov=apps --cov-report=term-missing -v

test-fast: ## Lancer les tests sans couverture
	pytest -x -q

run: ## Lancer le serveur de dev
	python manage.py runserver 0.0.0.0:8000

migrate: ## Appliquer les migrations
	python manage.py makemigrations
	python manage.py migrate

check: ## Vérifications Django
	python manage.py check --deploy

# ── Docker ──

docker-up: ## Lancer avec Docker Compose
	docker-compose up -d --build

docker-down: ## Arrêter Docker Compose
	docker-compose down

docker-logs: ## Voir les logs Docker
	docker-compose logs -f web

docker-shell: ## Shell dans le conteneur
	docker-compose exec web python manage.py shell

# ── CI/CD local ──

ci-local: lint test ## Simuler le CI en local (lint + tests)
	@echo "✅ CI local passé avec succès"

security: ## Vérifier les vulnérabilités des dépendances
	pip-audit
