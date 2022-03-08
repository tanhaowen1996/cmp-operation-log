#!/bin/bash
# entrypoint.sh file of Dockerfile

# Section1: Bash options
set -o errexit
set -o pipefail
set -o nounset

# Section2: Health of dependent services
postgres_ready() {
  python << END
import sys

from psycopg2 import connect
from psycopg2.errors import OperationalError

try:
    connect(
        dbname="${DB_NAME}",
        user="${DB_USER}",
        password="${DB_PASSWORD}",
        host="${DB_HOST}",
        port="${DB_PORT}",
    )
except OperationalError:
    sys.exit(-1)
END
}

until postgres_ready; do
  >&2 echo "Waiting for PostgreSQL to become available..."
  sleep 5
done
>&2 echo "PostgreSQL is available"

# until redis_ready; do
#  >&2 echo "Waiting for Redis to become available..."
#  sleep 5
# done
# >&2 echo "Redis is available"


# Section3: Idempotent Django commands
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

exec "$@"
