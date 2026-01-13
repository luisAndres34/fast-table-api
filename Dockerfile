FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen 

ENV PATH="/app/.venv/bin:$PATH"

COPY ./app ./app

EXPOSE 8000

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
