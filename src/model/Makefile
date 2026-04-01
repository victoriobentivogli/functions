.PHONY: help install sync test lint format clean

# Default target: show help
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install   Install uv and sync dependencies"
	@echo "  sync      Sync dependencies using uv"
	@echo "  test      Run tests using pytest"
	@echo "  lint      Run ruff check"
	@echo "  format    Run ruff format"
	@echo "  clean     Remove temporary files and virtualenv"

# Install/Sync
install:
	curl -LsSf https://astral.sh/uv/install.sh | sh
	uv sync --extra dev

sync:
	uv sync --extra dev

# Testing
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