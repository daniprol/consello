.PHONY: help install dev-install run run-dev translations static lint format test clean migrations migrate

PYTHON = python
MANAGE = $(PYTHON) src/manage.py
DJANGO_SETTINGS = consello.settings
DEV_SETTINGS = consello.settings_dev

help:
	@echo "Available commands:"
	@echo "  run          - Run Django server with production settings"
	@echo "  dev      	  - Run Django server with development settings"
	@echo "  translations - Make and compile translations"
	@echo "  static       - Collect static files"
	@echo "  migrations   - Create database migrations"
	@echo "  migrate      - Apply database migrations"
	@echo "  lint         - Run linters (ruff, djlint)"
	@echo "  format       - Format code (ruff, djlint)"
	@echo "  test         - Run tests"
	@echo "  clean        - Remove generated files"


run:
	$(MANAGE) runserver

dev:
	DJANGO_SETTINGS_MODULE=$(DEV_SETTINGS) $(MANAGE) runserver

migrations:
	$(MANAGE) makemigrations core
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate auth
	$(MANAGE) migrate contenttypes
	$(MANAGE) migrate admin
	$(MANAGE) migrate sessions
	$(MANAGE) migrate core
	$(MANAGE) migrate

translations:
	# Make translations
	cd src && $(MANAGE) makemessages -l es -l gl --ignore=venv/* --ignore=static/*
	# Format .po files for better readability
	cd ..
	find src/locale -name "django.po" -exec msgcat {} -o {} \;
	# Compile translations
	cd src && $(MANAGE) compilemessages --ignore=venv/*

static:
	$(MANAGE) collectstatic --noinput

lint:
	ruff check src/
	djlint src/core/templates/ --check

format:
	ruff format src/
	djlint src/core/templates/ --reformat

test:
	pytest src/

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".ruff_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf src/static/
	rm -rf src/media/ 