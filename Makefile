.PHONY: help setup build up down logs restart clean test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Run setup script
	@./setup.sh

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## View logs from all services
	docker-compose logs -f

logs-backend: ## View backend logs
	docker-compose logs -f backend

logs-frontend: ## View frontend logs
	docker-compose logs -f frontend

restart: ## Restart all services
	docker-compose restart

restart-backend: ## Restart backend service
	docker-compose restart backend

restart-frontend: ## Restart frontend service
	docker-compose restart frontend

clean: ## Remove containers and volumes
	docker-compose down -v

test: ## Run health check
	@echo "Testing backend health..."
	@curl -f http://localhost:8000/api/v1/health || echo "Backend is not healthy"
	@echo "\nTesting frontend..."
	@curl -f http://localhost:3003 || curl -f http://localhost:3001 || curl -f http://localhost:3000 || echo "Frontend is not accessible"

dev-backend: ## Run backend in development mode
	cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload

dev-frontend: ## Run frontend in development mode
	cd frontend && npm install && npm run dev

