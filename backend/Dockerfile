FROM python:3.14-slim

WORKDIR /app

# System deps for psycopg, ta-lib, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install PDM + uv
RUN pip install --no-cache-dir pdm && \
    curl -LsSf https://astral.sh/uv/install.sh | sh

COPY pyproject.toml pdm.lock* ./
RUN pdm install --no-self --group dev

COPY . .

EXPOSE 8000

CMD ["pdm", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
