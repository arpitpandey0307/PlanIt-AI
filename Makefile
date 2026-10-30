.PHONY: install dev test clean

install:
	@echo "Installing dependencies..."
	pip install -r backend/requirements.txt
	cd frontend && npm install

dev:
	@echo "Starting development servers..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	python backend/app/main.py

test:
	@echo "Running backend tests..."
	cd backend && pytest --cov=app tests/
	@echo "Running frontend tests..."
	cd frontend && npm test

lint:
	@echo "Linting code..."
	cd backend && ruff check app/
	cd backend && mypy app/
	cd frontend && npm run lint

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker build -t planit-ai .

docker-run:
	docker run -p 8000:8000 -e GOOGLE_API_KEY=$(GOOGLE_API_KEY) planit-ai
