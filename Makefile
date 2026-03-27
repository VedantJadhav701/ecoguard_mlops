# EcoGuard Development & Deployment Makefile (Render)

.PHONY: help install test lint format clean dev docker compose logs mlflow

help:
	@echo "EcoGuard Render Deployment - Development Commands"
	@echo "=================================================="
	@echo ""
	@echo "Development:"
	@echo "  make install          - Install dependencies"
	@echo "  make dev              - Run API locally with auto-reload"
	@echo "  make test             - Run all tests"
	@echo "  make lint             - Code quality checks"
	@echo "  make format           - Auto-format code"
	@echo "  make clean            - Clean build artifacts"
	@echo ""
	@echo "Docker & Local Stack:"
	@echo "  make docker           - Build Docker image"
	@echo "  make docker-run       - Run container locally"
	@echo "  make compose          - Start full stack with docker-compose"
	@echo "  make compose-down     - Stop docker-compose stack"
	@echo ""
	@echo "Deployment:"
	@echo "  git push origin main  - Auto-deploys to Render"
	@echo ""
	@echo "Utilities:"
	@echo "  make logs             - View API logs"
	@echo "  make mlflow           - Start MLflow UI"

# Development
install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v --cov=. --cov-report=html

test-fast:
	pytest tests/ -v -x

test-load:
	pytest tests/test_load.py -v -s

lint:
	flake8 app.py predictor.py mlops/ --max-line-length=120
	mypy app.py predictor.py mlops/ --ignore-missing-imports

format:
	black app.py predictor.py mlops/ tests/
	isort app.py predictor.py mlops/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov/ dist/ build/ *.egg-info/
	rm -rf .mypy_cache

# Docker
docker:
	docker build -t ecoguard:latest .

docker-run:
	docker run -d \
		--name ecoguard-api \
		-p 8000:8000 \
		--env-file .env \
		-v ${PWD}/models:/app/models \
		-v ${PWD}/logs:/app/logs \
		ecoguard:latest

docker-stop:
	docker stop ecoguard-api
	docker rm ecoguard-api

# Docker Compose
compose:
	docker-compose up -d

compose-down:
	docker-compose down

compose-logs:
	docker-compose logs -f api

# Utilities
mlflow:
	mlflow ui --host 0.0.0.0 --port 5000

logs:
	docker logs -f ecoguard-api

dev:
	uvicorn app:app --reload --host 0.0.0.0 --port 8000

setup: install lint test
	@echo "✓ Development environment ready!"

.DEFAULT_GOAL := help
