# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

# Set workdir for all stages
WORKDIR /app

# Builder stage: install dependencies into a venv
FROM base AS builder

# System dependencies for Python packages (e.g. Pillow, psycopg2, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libjpeg-dev \
        zlib1g-dev \
        && rm -rf /var/lib/apt/lists/*

# Copy only requirements.txt if it exists, for better caching
COPY --link requirements.txt ./

# Use BuildKit mount for pip cache
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install -r requirements.txt

# Copy the rest of the application code
COPY --link . .

# Final stage: runtime image
FROM base AS final

# Create a non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy app code and venv from builder
COPY --from=builder /app /app

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Set permissions
RUN chown -R appuser:appgroup /app
USER appuser

# Expose the default Django port
EXPOSE 8000

# Entrypoint: run the Django app using manage.py
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
