.PHONY: help build build-gpu up down logs up-gpu down-gpu logs-gpu clean

# Configuration
MODEL_VARIANT ?= server

# Default target
help:
	@echo "Available targets:"
	@echo "  Docker (CPU):"
	@echo "    build       - Build CPU Docker image"
	@echo "    up          - Start CPU containers"
	@echo "    down        - Stop CPU containers"
	@echo "    logs        - Follow CPU container logs"
	@echo ""
	@echo "  Docker (GPU):"
	@echo "    build-gpu   - Build GPU Docker image"
	@echo "    up-gpu      - Start GPU containers"
	@echo "    down-gpu    - Stop GPU containers"
	@echo "    logs-gpu    - Follow GPU container logs"
	@echo ""
	@echo "  Cleanup:"
	@echo "    clean       - Remove build artifacts and caches"
	@echo ""
	@echo "  Variables:"
	@echo "    MODEL_VARIANT - Model variant: server (default) or mobile"
	@echo "                    Example: make build MODEL_VARIANT=mobile"

# Docker CPU targets
build:
	MODEL_VARIANT=$(MODEL_VARIANT) docker-compose build

up: build
	MODEL_VARIANT=$(MODEL_VARIANT) docker-compose up

down:
	MODEL_VARIANT=$(MODEL_VARIANT) docker-compose down

logs:
	MODEL_VARIANT=$(MODEL_VARIANT) docker-compose logs -f

# Docker GPU targets
build-gpu:
	MODEL_VARIANT=$(MODEL_VARIANT) docker-compose -f docker-compose.gpu.yml build

up-gpu: build-gpu
	MODEL_VARIANT=$(MODEL_VARIANT) docker-compose -f docker-compose.gpu.yml up

down-gpu:
	MODEL_VARIANT=$(MODEL_VARIANT) docker-compose -f docker-compose.gpu.yml down

logs-gpu:
	MODEL_VARIANT=$(MODEL_VARIANT) docker-compose -f docker-compose.gpu.yml logs -f

# Cleanup
clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
