FROM python:3.13.4-alpine AS base

ARG APP_PATH=/app
ARG SERVICE_NAME=gpt-api
ARG SERVICE_PATH=services/$SERVICE_NAME

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    PYTHONPATH=${APP_PATH}/libs:$APP_PATH/$SERVICE_PATH/src \
    PATH="${APP_PATH}/.venv/bin:$PATH"

WORKDIR ${APP_PATH}


# ============================ #
#            BUILDER           #
# ============================ #
FROM base AS builder

RUN apk update && \
    apk add --no-cache \
    uv

COPY ./pyproject.toml ./uv.lock ./
COPY ./${SERVICE_PATH}/pyproject.toml ${SERVICE_PATH}/pyproject.toml
COPY ./libs/common ./libs/common


# ============================ #
#         DEPS INSTALLING      #
# ============================ #
FROM builder AS deps-dev

RUN uv sync --frozen --dev --package $SERVICE_NAME

FROM builder AS deps-prod

RUN uv sync --frozen --no-dev --package $SERVICE_NAME


# ============================ #
#         SOURCE CODE          #
# ============================ #
FROM builder AS source

COPY ${SERVICE_PATH}/src ${SERVICE_PATH}/src
COPY ./libs/common ./libs/common


# ============================ #
#         DEVELOPMENT          #
# ============================ #
FROM base AS development

COPY --from=deps-dev ${APP_PATH}/.venv ./.venv
COPY --from=source ${APP_PATH} .

WORKDIR ${APP_PATH}/${SERVICE_PATH}/src

CMD ["hupper", "-q", "-m", "main"]


# ============================ #
#          PRODUCTION          #
# ============================ #
FROM base AS production

COPY --from=deps-prod ${APP_PATH}/.venv ./.venv
COPY --from=source ${APP_PATH} .

WORKDIR ${APP_PATH}/${SERVICE_PATH}/src

CMD ["python", "main.py"]
