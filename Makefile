.PHONY: dev install deploy deploy-down healthcheck

dev:
	uv run asterism/api_server.py

install:
	uv sync

deploy:
	docker compose up --build -d

deploy-down:
	docker compose down

healthcheck:
	curl -f http://localhost:20820/v1/health
