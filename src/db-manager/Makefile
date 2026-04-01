.PHONY: help install sync test lint format clean db-up db-down db-reset db-logs db-psql

# Default target: show help
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Development:"
	@echo "  install   Install uv and sync dependencies"
	@echo "  sync      Sync dependencies using uv"
	@echo "  test      Run tests (requires db-up)"
	@echo "  lint      Run ruff check"
	@echo "  format    Run ruff format"
	@echo "  clean     Remove temporary files and virtualenv"
	@echo ""
	@echo "Infrastructure:"
	@echo "  db-up     Start PostgreSQL + pgAdmin containers"
	@echo "  db-down   Stop containers"
	@echo "  db-reset  Destroy data volume and recreate containers"
	@echo "  db-logs   Follow container logs"
	@echo "  db-psql   Open psql shell in the PostgreSQL container"

# Install/Sync
install:
	curl -LsSf https://astral.sh/uv/install.sh | sh
	uv sync --extra dev

sync:
	uv sync --extra dev

# Testing (requires running database: make db-up)
test:
	uv run pytest

# Linting and Formatting (using Ruff, which is standard with uv)
lint:
	uv run ruff check .

format:
	uv run ruff format .

# Cleanup
clean:
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

# --- Infrastructure ---
db-up:
	docker compose up -d
	@echo "PostgreSQL: localhost:5433  (user: ere / password: ere)"
	@echo "pgAdmin:    http://localhost:5051  (admin@ere.local / admin)"

db-down:
	docker compose down

db-reset:
	docker compose down -v
	docker compose up -d
	@echo "Database volume destroyed and containers recreated."

db-logs:
	docker compose logs -f

db-psql:
	docker compose exec postgres psql -U ere -d ere
