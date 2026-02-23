.PHONY: dev install deploy deploy-down

dev:
	uv run asterism/api_server.py

install:
	uv sync

deploy:
	docker compose up --build -d

deploy-down:
	docker compose down
