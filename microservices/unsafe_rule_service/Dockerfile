# ─── Unsafe Rule Service ──────────────────────────────────────────────────────
# Runs as a one-shot job that finds 'failed' submissions and marks them unsafe.
#
# Build:  docker build -t unsafe-rule-service .
# Run:    docker run --rm \
#           -v /absolute/path/to/db.sqlite3:/app/db.sqlite3 \
#           -v /absolute/path/to/photos:/app/photos \
#           unsafe-rule-service
# ──────────────────────────────────────────────────────────────────────────────

FROM python:3.12-slim

WORKDIR /app

# Install only what the ORM layer needs
RUN pip install --no-cache-dir \
    Django==6.0.7 \
    asgiref==3.11.1 \
    sqlparse==0.5.5 \
    tzdata==2026.2

# Copy the service script
COPY microservices/unsafe_rule_service/service.py .

# Copy the Django app package so its models are importable
COPY photos ./photos

# The SQLite database is injected at runtime via the DB_PATH env-var + a volume.
ENV DB_PATH=/app/db.sqlite3

CMD ["python", "service.py"]
