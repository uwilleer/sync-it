FROM golang:1.22-alpine AS builder

ARG APP_PATH=/app
ARG SERVICE_NAME=vacancy-matcher
ARG SERVICE_PATH=services/${SERVICE_NAME}

WORKDIR ${APP_PATH}/${SERVICE_PATH}

RUN apk add --no-cache git ca-certificates && update-ca-certificates

COPY ${SERVICE_PATH}/go.mod ./
RUN go mod download

COPY ${SERVICE_PATH} .

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o /bin/${SERVICE_NAME}


FROM alpine:3.19 AS runtime

ARG APP_PATH=/app
ARG SERVICE_NAME=vacancy-matcher

RUN apk add --no-cache ca-certificates && update-ca-certificates

COPY --from=builder /bin/${SERVICE_NAME} /usr/local/bin/${SERVICE_NAME}

ENV ENV_SERVICE_INTERNAL_HOST=0.0.0.0
ENV ENV_SERVICE_INTERNAL_PORT=8080

EXPOSE 8080

CMD ["vacancy-matcher"]

