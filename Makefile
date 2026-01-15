# Makefile for Blender MCP development
# Run `make help` to see available commands

.PHONY: help install dev-install test lint format type-check security clean build release docs

# Default target
help: ## Show this help message
	@echo "Blender MCP Development Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install Blender MCP for production use
	pip install -e .

dev-install: ## Install Blender MCP with development dependencies
	pip install -e ".[dev]"

# Development workflow
test: ## Run all tests
	pytest tests/ -v --cov=src/blender_mcp --cov-report=term-missing

test-unit: ## Run only unit tests
	pytest tests/unit/ -v

test-integration: ## Run only integration tests
	pytest tests/integration/ -v --tb=short

lint: ## Run linting checks
	ruff check src/ tests/
	ruff format --check src/ tests/

format: ## Format code with black and isort
	ruff format src/ tests/
	ruff check --fix src/ tests/

type-check: ## Run type checking with mypy
	mypy src/blender_mcp/

security: ## Run security scanning
	bandit -r src/ -c pyproject.toml
	safety check --full-report

quality: ## Run all quality checks (lint, type, security)
	@echo "Running quality checks..."
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) security
	@echo "✅ All quality checks passed!"

# MCPB Packaging
mcpb-validate: ## Validate MCPB package structure
	cd mcpb && mcpb validate

mcpb-build: ## Build MCPB package
	./scripts/build-mcpb.ps1 -Clean -Validate

mcpb-sign: ## Build and sign MCPB package
	./scripts/build-mcpb.ps1 -Clean -Validate -Sign

mcpb-release: ## Build release version of MCPB package
	./scripts/build-mcpb.ps1 -Clean -Validate -Sign -KeyFile "$(SIGNING_KEY)"

# Building and releasing
build: ## Build distribution packages
	python -m build

clean: ## Clean build artifacts
	rm -rf dist/ build/ *.egg-info/
	rm -rf src/blender_mcp.egg-info/
	rm -f .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.pyc" -delete

# Pre-commit hooks
pre-commit-install: ## Install pre-commit hooks
	pre-commit install

pre-commit-run: ## Run pre-commit on all files
	pre-commit run --all-files

# Development server
server-dev: ## Run development server
	python -m blender_mcp.server --debug --host 0.0.0.0 --port 8000

# Documentation
docs-build: ## Build documentation
	pip install -e ".[docs]"
	sphinx-build docs/ docs/_build/html

docs-serve: ## Serve documentation locally
	cd docs/_build/html && python -m http.server 8001

# CI/CD simulation
ci-local: ## Run local CI pipeline
	@echo "Running local CI pipeline..."
	$(MAKE) clean
	$(MAKE) quality
	$(MAKE) test
	$(MAKE) mcpb-validate
	@echo "✅ Local CI pipeline passed!"

# Publishing
publish-pypi: ## Publish to PyPI (requires API token)
	python -m build
	twine upload dist/*.whl dist/*.tar.gz

publish-test-pypi: ## Publish to Test PyPI
	python -m build
	twine upload --repository testpypi dist/*.whl dist/*.tar.gz

docker-build: ## Build Docker image
	docker build -t blender-mcp .

docker-run: ## Run Docker container
	docker run -p 8000:8000 blender-mcp

docker-compose-dev: ## Run with Docker Compose (dev)
	docker-compose --profile dev up

docker-compose-prod: ## Run with Docker Compose (prod)
	docker-compose --profile prod up

# Release workflow
release-patch: ## Create patch release (0.0.X)
	git tag -a "v$(shell python -c "import src/blender_mcp; print('.'.join(src.blender_mcp.__version__.split('.')[:2]) + '.' + str(int(src.blender_mcp.__version__.split('.')[-1]) + 1))")" -m "Patch release"
	git push --tags

release-minor: ## Create minor release (0.X.0)
	git tag -a "v$(shell python -c "import src/blender_mcp; print(str(int(src.blender_mcp.__version__.split('.')[0]) + 1) + '.0.0')")" -m "Minor release"
	git push --tags

release-major: ## Create major release (X.0.0)
	git tag -a "v$(shell python -c "import src/blender_mcp; print(str(int(src.blender_mcp.__version__.split('.')[0]) + 1) + '.0.0')")" -m "Major release"
	git push --tags

# Utility commands
deps-update: ## Update all dependencies
	pip install --upgrade pip-tools
	pip-compile --upgrade pyproject.toml
	pip-sync

deps-show: ## Show current dependency tree
	pipdeptree

version: ## Show current version
	@python -c "import src.blender_mcp; print(f'Blender MCP v{src.blender_mcp.__version__}')"

info: ## Show project information
	@echo "Blender MCP - AI-Powered 3D Creation"
	@echo "====================================="
	@$(MAKE) version
	@echo ""
	@echo "Python: $(shell python --version)"
	@echo "Platform: $(shell python -c 'import platform; print(platform.platform())')"
	@echo ""
	@echo "Installation: pip install -e ."
	@echo "Development: pip install -e \".[dev]\""
	@echo "Testing: make test"
	@echo "Quality: make quality"
