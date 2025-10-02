#!/usr/bin/env bash
# Entry point responsible for bootstrapping the Patchman Django stack inside a container.

set -euo pipefail

ROLE=${1:-web}
shift || true

# Ensure the runtime directories exist even when mounted volumes are empty.
mkdir -p /var/lib/patchman/db /var/lib/patchman/run /app/run/static

# Restore pre-built static files into the mounted volume when required.
if [ -d /opt/patchman/static-build ] && [ -z "$(ls -A /app/run/static 2>/dev/null)" ]; then
  cp -a /opt/patchman/static-build/. /app/run/static/
fi

# Apply database migrations on every start to keep the schema up to date.
python manage.py migrate --noinput

# Optionally bootstrap a Django superuser based on environment variables.
if [[ -n "${DJANGO_SUPERUSER_USERNAME:-}" ]] && [[ -n "${DJANGO_SUPERUSER_EMAIL:-}" ]]; then
  python manage.py shell <<'PYTHON'
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ["DJANGO_SUPERUSER_USERNAME"]
email = os.environ["DJANGO_SUPERUSER_EMAIL"]
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "patchman")

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
PYTHON
fi

# Select the appropriate long-running process for the container.
case "${ROLE}" in
  web)
    if [[ "${PATCHMAN_RUN_GUNICORN:-false}" =~ ^([Tt]rue|1|yes|on)$ ]]; then
      exec gunicorn patchman.wsgi:application --bind 0.0.0.0:8000 --workers "${GUNICORN_WORKERS:-4}" "$@"
    else
      exec python manage.py runserver 0.0.0.0:8000 "$@"
    fi
    ;;
  worker)
    exec celery -A patchman.celery worker -l info "$@"
    ;;
  *)
    exec "$ROLE" "$@"
    ;;
 esac
