FROM golang:1.25-alpine AS base

ARG APP_PATH=/app
ARG SERVICE_NAME=vacancy-matcher
ARG SERVICE_PATH=services/$SERVICE_NAME

ENV CGO_ENABLED=0 \
    GOOS=linux

WORKDIR ${APP_PATH}/${SERVICE_PATH}

# ============================ #
#            BUILDER           #
# ============================ #
FROM base AS builder

RUN apk update

COPY ${SERVICE_PATH}/go.mod ${SERVICE_PATH}/go.sum ./
RUN go mod download

COPY ${SERVICE_PATH} ./

RUN go build -o /app/matcher ./cmd/matcher/main.go


# ============================ #
#         DEVELOPMENT          #
# ============================ #
FROM base AS development

RUN go install github.com/air-verse/air@latest

CMD ["air"]


# ============================ #
#          PRODUCTION          #
# ============================ #
FROM alpine:3.22 AS production

COPY --from=builder /app/matcher /app/matcher

CMD ["/app/matcher"]
