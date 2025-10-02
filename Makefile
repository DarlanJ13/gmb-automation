.PHONY: help build up down logs clean install-backend install-frontend migrate

help:
	@echo "GMB Automation - Available commands:"
	@echo "  make build              - Build all Docker containers"
	@echo "  make up                 - Start all services"
	@echo "  make down               - Stop all services"
	@echo "  make logs               - View logs from all services"
	@echo "  make clean              - Remove all containers and volumes"
	@echo "  make install-backend    - Install backend dependencies"
	@echo "  make install-frontend   - Install frontend dependencies"
	@echo "  make migrate            - Run database migrations"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker system prune -f

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

migrate:
	docker-compose exec backend alembic upgrade head

dev-backend:
	cd backend && uvicorn app.main:app --reload

dev-frontend:
	cd frontend && npm run dev
