.PHONY: help backend-install backend-run docker-up docker-down db-init db-shell test lint format clean

help:
	@echo "BI System Development Commands"
	@echo ""
	@echo "Backend:"
	@echo "  make backend-install    Install Python dependencies"
	@echo "  make backend-run        Run development server"
	@echo "  make backend-test       Run tests"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up          Start PostgreSQL and Redis"
	@echo "  make docker-down        Stop PostgreSQL and Redis"
	@echo "  make docker-logs        View Docker logs"
	@echo ""
	@echo "Database:"
	@echo "  make db-init            Initialize database"
	@echo "  make db-shell           Connect to PostgreSQL"
	@echo "  make db-reset           Reset database (drop all tables)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint               Run linters (ruff, black)"
	@echo "  make format             Format code with black"
	@echo "  make clean              Clean cache files"
	@echo ""

# Backend
backend-install:
	cd backend && pip install -r requirements.txt

backend-run:
	cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

backend-test:
	cd backend && pytest tests/ -v

# Docker
docker-up:
	docker-compose -f docker-compose.dev.yml up -d
	@echo "PostgreSQL and Redis started"
	@echo "PostgreSQL: localhost:5432 (postgres/postgres)"
	@echo "Redis: localhost:6379"

docker-down:
	docker-compose -f docker-compose.dev.yml down

docker-logs:
	docker-compose -f docker-compose.dev.yml logs -f

# Database
db-init:
	cd backend && python -c "from app.db.database import init_db; init_db(); print('Database initialized')"

db-shell:
	psql -h localhost -U postgres -d bi_system

db-reset:
	cd backend && python -c "from app.db.database import Base, engine; Base.metadata.drop_all(bind=engine); print('Database reset')"

# Code Quality
lint:
	cd backend && ruff check . && black --check .

format:
	cd backend && black . && ruff check . --fix

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	rm -rf backend/.venv 2>/dev/null || true

# All-in-one setup
setup: backend-install docker-up db-init
	@echo "✓ Setup complete!"
	@echo "Next steps:"
	@echo "  1. Copy backend/.env.example to backend/.env"
	@echo "  2. Add Zoho and Claude API credentials to backend/.env"
	@echo "  3. Run: make backend-run"
