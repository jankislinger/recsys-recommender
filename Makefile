PROJECT ?= recsys-recommender
PORT ?= 8000
IMAGE ?= $(PROJECT):dev

.PHONY: dev run docker-build docker-run clean

dev:   ## Run auto-reload dev server (uvicorn)
	uv run --env-file .env uvicorn app.main:app --reload --host 0.0.0.0 --port $(PORT)

docker-build: ## Build docker image
	docker build -t $(IMAGE) .

docker-run:   ## Run docker container
	docker run --rm -p $(PORT):8000 --env-file .env $(IMAGE)

fmt:
	uv run ruff format && uv run ruff check --fix

clean:
	rm -rf .venv __pycache__ .pytest_cache
