# =============================================================================
# AI Podcast Engine 2.0 — Makefile
# =============================================================================

.PHONY: install install-backend install-frontend dev backend frontend \
        test lint format ci docker-build docker-up docker-down clean help

PYTHON  := python3
PIP     := pip
VENV    := backend/venv
ACTIVATE := source $(VENV)/bin/activate

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo ""
	@echo "  AI Podcast Engine 2.0"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

install: install-backend install-frontend ## Install all dependencies
	@echo ""
	@echo "✅ Setup complete! Run 'make dev' to start."

install-backend: ## Set up Python virtual environment and install dependencies
	@echo "📦 Setting up Python backend..."
	cd backend && $(PYTHON) -m venv venv
	cd backend && $(ACTIVATE) && $(PIP) install --upgrade pip && $(PIP) install -r requirements.txt
	@echo "✅ Backend dependencies installed."

install-frontend: ## Install Node.js frontend dependencies
	@echo "📦 Setting up Next.js frontend..."
	cd frontend && npm install
	@echo "✅ Frontend dependencies installed."

# ---------------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------------

dev: ## Start both backend and frontend in development mode
	@echo "🚀 Starting AI Podcast Engine 2.0..."
	@trap 'kill 0' EXIT; \
		(cd backend && $(ACTIVATE) && uvicorn main:app --reload --port 8000) & \
		(cd frontend && npm run dev) & \
		wait

backend: ## Start backend only
	@echo "🔧 Starting FastAPI backend on port 8000..."
	cd backend && $(ACTIVATE) && uvicorn main:app --reload --host 0.0.0.0 --port 8000

frontend: ## Start frontend only
	@echo "🌐 Starting Next.js frontend on port 3000..."
	cd frontend && npm run dev

# ---------------------------------------------------------------------------
# Testing & Quality
# ---------------------------------------------------------------------------

test: ## Run the test suite
	@echo "🧪 Running tests..."
	cd backend && $(ACTIVATE) && pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage report
	@echo "🧪 Running tests with coverage..."
	cd backend && $(ACTIVATE) && pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

lint: ## Lint and type-check the backend
	@echo "🔍 Running ruff linter..."
	cd backend && $(ACTIVATE) && ruff check app/ main.py
	@echo "🔍 Running mypy type-checker..."
	cd backend && $(ACTIVATE) && mypy app/ main.py --ignore-missing-imports || true

format: ## Auto-format the backend code
	@echo "✨ Formatting code with ruff..."
	cd backend && $(ACTIVATE) && ruff format app/ main.py tests/

ci: test lint ## Run full CI checks (tests + lint)
	@echo "✅ CI checks passed!"

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------

docker-build: ## Build Docker images
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-up: ## Start all services with Docker
	@echo "🐳 Starting AI Podcast Engine 2.0 via Docker..."
	docker-compose up -d
	@echo "✅ Stack running:"
	@echo "   Backend:  http://localhost:8000"
	@echo "   Frontend: http://localhost:3000"
	@echo "   API Docs: http://localhost:8000/docs"

docker-down: ## Stop all Docker services
	docker-compose down

docker-logs: ## Tail Docker logs
	docker-compose logs -f

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

clean: ## Remove generated data and caches
	@echo "🧹 Cleaning generated files..."
	rm -rf backend/data/raw/* backend/data/tts/* backend/data/viral/*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleaned."

clean-all: clean ## Remove everything including venv and node_modules
	rm -rf backend/venv frontend/node_modules frontend/.next

env: ## Create .env from .env.example (won't overwrite existing)
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env from .env.example — fill in your API keys!"; \
	else \
		echo "⚠️  .env already exists. Edit it manually."; \
	fi
