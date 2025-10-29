.PHONY: help install up down restart logs build test test-cov test-watch lint format clean check-all

help:
	@echo "Available commands:"
	@echo ""
	@echo "Setup & Dependencies:"
	@echo "  install    - Install project dependencies"
	@echo ""
	@echo "Docker Services:"
	@echo "  up         - Start all services in the background"
	@echo "  down       - Stop and remove all services"
	@echo "  restart    - Restart all services"
	@echo "  logs       - Follow the logs of all running services"
	@echo "  build      - Build or rebuild all service images"
	@echo ""
	@echo "Testing:"
	@echo "  test       - Run the entire pytest suite"
	@echo "  test-cov   - Run tests with coverage report"
	@echo "  test-watch - Run tests in watch mode (re-run on changes)"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint       - Run ruff linter and mypy type checker"
	@echo "  format     - Format all code using ruff"
	@echo "  check-all  - Run linters, type checks, and tests"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean      - Remove cache files, coverage reports, etc."

install:
	@echo "Installing dependencies..."
	python -m pip install --upgrade pip
	pip install -e .[dev]

up:
	@echo "Starting all services in detached mode..."
	docker-compose up --build -d

down:
	@echo "Stopping and removing all services..."
	docker-compose down

restart:
	@echo "Restarting all services..."
	docker-compose restart

logs:
	@echo "Following logs for all services..."
	docker-compose logs -f

build:
	@echo "Building all service images..."
	docker-compose build

test:
	@echo "Running pytest suite..."
	python -m pytest -v

test-cov:
	@echo "Running tests with coverage..."
	python -m pytest --cov --cov-report=html --cov-report=term-missing
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"

test-watch:
	@echo "Running tests in watch mode..."
	python -m pytest-watch

lint:
	@echo "Running linter and type checker..."
	ruff check .
	mypy .

format:
	@echo "Formatting code with ruff..."
	ruff format .

check-all: lint test
	@echo "All checks passed!"

clean:
	@echo "Cleaning up generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage coverage.xml
	@echo "Cleanup complete!"