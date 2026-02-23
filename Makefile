.PHONY: dev install

dev:
	uv run asterism/api_server.py

install:
	uv sync
