#!/bin/bash
set -euo pipefail

PROJECT_DIR="/srv/syncit"
COMPOSE_FILE="${PROJECT_DIR}/infra/docker/docker-compose.yml"
ENV_FILE="${PROJECT_DIR}/infra/.env"
COMPOSE="docker compose -f ${COMPOSE_FILE} --env-file ${ENV_FILE}"

MIGRATOR_SERVICES=(telegram-bot vacancy-parser vacancy-processor)

cd "$PROJECT_DIR"

echo "[deploy] pulling images..."
$COMPOSE pull

echo "[deploy] running migrations..."
for svc in "${MIGRATOR_SERVICES[@]}"; do
    if $COMPOSE --profile migrator config --services | grep -q "^${svc}-migrator$"; then
        echo "[deploy] migrate ${svc}..."
        $COMPOSE --profile migrator run --rm --no-TTY \
            --workdir "/app/services/${svc}" "${svc}-migrator" \
            alembic upgrade head
    else
        echo "[deploy] skip ${svc} (no migrator service)"
    fi
done

echo "[deploy] rolling up..."
$COMPOSE up -d --wait --wait-timeout 120

echo "[deploy] pruning dangling images..."
docker image prune -f

echo "[deploy] done"
