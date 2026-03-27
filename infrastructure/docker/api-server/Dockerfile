# ---- base: shared dependency layer ----
FROM golang:1.26-alpine AS base

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

# ---- dev: hot-reload with air ----
FROM base AS dev

RUN go install github.com/air-verse/air@latest

COPY . .

CMD ["air", "-c", ".air.toml"]

# ---- build: compile static binary ----
FROM base AS build

COPY . .

RUN CGO_ENABLED=0 go build -o /server ./cmd/server

# ---- prod: minimal runtime image ----
FROM gcr.io/distroless/static-debian12 AS prod

COPY --from=build /server /server

EXPOSE 8080

ENTRYPOINT ["/server"]
