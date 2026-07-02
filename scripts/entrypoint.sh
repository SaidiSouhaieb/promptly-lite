#!/bin/bash
set -e

/app/scripts/wait-for-it.sh db:5432 -t 30

alembic revision --autogenerate -m "auto migration on container start" || echo "No changes to migrate"

alembic upgrade head

exec uvicorn main:app --host 0.0.0.0 --port 8231 --reload
