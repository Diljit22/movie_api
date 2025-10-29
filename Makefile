.PHONY: help up down logs build test lint format

help:
	@echo "Available commands:"
	@echo "  up      - Start all services in the background"
	@echo "  down    - Stop and remove all services"
	@echo "  logs    - Follow the logs of all running services"
	@echo "  build   - Build or rebuild all service images"
	@echo "  test    - Run the entire pytest suite"
	@echo "  lint    - Run ruff linter and mypy type checker"
	@echo "  format  - Format all code using ruff"

up:
	@echo "Starting all services in detached mode..."
	docker-compose up --build -d

down:
	@echo "Stopping and removing all services..."
	docker-compose down

logs:
	@echo "Following logs for all services..."
	docker-compose logs -f

build:
	@echo "Building all service images..."
	docker-compose build

test:
	@echo "Running pytest suite..."
	python -m pytest -v

lint:
	@echo "Running linter and type checker..."
	ruff check .
	mypy .

format:
	@echo "Formatting code with ruff..."
	ruff format .