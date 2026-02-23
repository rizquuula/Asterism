FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
COPY asterism/ asterism/
COPY workspace/ workspace/

RUN uv sync --frozen --no-dev

RUN mkdir -p logs sessions

ENV PYTHONPATH=/app
ENV WORKSPACE_DIR=/app/workspace

EXPOSE 8080

CMD ["uv", "run", "python", "asterism/api_server.py"]
