FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . /app

EXPOSE 8000

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]