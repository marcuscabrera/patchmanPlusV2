# syntax=docker/dockerfile:1.5

# Base image with Python 3.11 satisfies the 3.9+ requirement.
FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered output.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=patchman.settings \
    PATH="/usr/local/bin:$PATH"

# Set working directory for the application code.
WORKDIR /app

# Install build dependencies required for certain Python packages and clean up afterwards.
RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirement definitions first to leverage Docker layer caching.
COPY requirements.txt ./

# Upgrade pip and install project dependencies before copying the remaining code.
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the full application source into the image.
COPY . .

# Ensure runtime directories exist ahead of time for volume mounts.
RUN mkdir -p /var/lib/patchman/db /var/lib/patchman/run /app/run/static

# Provide a deterministic secret key only for build time operations such as collectstatic.
ENV DJANGO_SECRET_KEY="build-only-secret-key"

# Collect Django static assets during the image build as requested.
RUN python manage.py collectstatic --noinput

# Preserve the built static assets so they can be restored into a mounted volume at runtime.
RUN mkdir -p /opt/patchman/static-build \
    && cp -a /var/lib/patchman/static/. /opt/patchman/static-build/

# Copy and set permissions for the entrypoint helper.
RUN chmod +x docker/entrypoint.sh

# Set the default entrypoint; the role (web/worker) will be selected via CMD or docker-compose.
ENTRYPOINT ["/bin/bash", "docker/entrypoint.sh"]

# Default command starts the Django development server bound to all interfaces on port 8000.
CMD ["web"]
