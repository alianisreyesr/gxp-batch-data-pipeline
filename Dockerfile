FROM python:3.11-slim

WORKDIR /app

# Runtime-only dependencies (no pytest/dbt in the image)
COPY requirements-runtime.txt .
RUN pip install --no-cache-dir -r requirements-runtime.txt

COPY . .

RUN useradd --system --uid 10001 --no-create-home appuser \
    && mkdir -p data warehouse artifacts \
    && chown -R appuser:appuser /app
USER appuser

CMD ["python", "-m", "src.pipeline", "--seed", "42"]
