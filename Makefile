# Makefile — Shortcuts for Structured LLM Notebooks
.PHONY: help install sync ollama-setup notebooks nb fmt lint typecheck test clean cost-report

help: ## Show this help message
	@echo "Structured LLM Notebooks — Available Commands"
	@echo "=============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## First-time project setup (dependencies + kernel)
	bash setup.sh

sync: ## Sync uv dependencies
	uv sync --all-extras

ollama-setup: ## Pull local Ollama models for zero-cost mode
	bash scripts/ollama_setup.sh

notebooks: ## Start Jupyter Lab
	uv run jupyter lab --notebook-dir=notebooks --ip=0.0.0.0 --no-browser --port=8888

nb: ## Alias for notebooks
	$(MAKE) notebooks

fmt: ## Format code with ruff
	uv run ruff format src/ notebooks/

lint: ## Lint code with ruff
	uv run ruff check src/ notebooks/

typecheck: ## Type check with mypy
	uv run mypy src/

clean: ## Clean cache files and outputs
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	find notebooks -type f -name "*.ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned cache files"

cost-report: ## Show estimated costs for all notebooks
	uv run python -c "from src.cost_tracker import full_report; full_report()"
