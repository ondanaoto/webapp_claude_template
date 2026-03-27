# Project

<!-- プロジェクトの概要を書いておく -->

## Tech Stack

- **API**: Go + Connect RPC (gRPC)
- **Frontend**: TypeScript + React + Vite + Tailwind CSS
- **DB**: PostgreSQL + ent (ORM)
- **Schema**: Protobuf (buf)
- **Monorepo**: Task (Taskfile) runner

## Build & Dev Commands

```bash
# Code generation
task proto:gen        # Generate all code from protobuf (Go + TypeScript)
task ent:gen          # Generate ent ORM code from schemas
task ent:new -- MyEntity # Create a new ent schema file

# Migrations (Atlas)
task ent:migrate:diff -- migration_name  # Generate migration from schema diff
task ent:migrate:apply                   # Apply pending migrations

# Quality
task lint             # Run all linters (go + proto + ts)
task go:test          # Run all Go tests
task web:test         # Run frontend tests (Vitest)

# Local development
task docker:up        # Start PostgreSQL + MinIO + API server + Web (hot-reload)
```

Single test: `cd apps/api-server && go test ./internal/handler -run TestRegisterUser`

## Project Structure (target)

```
apps/
  api-server/         # Go API (cmd/server/, ent/schema/, internal/handler/)
  web/                # React frontend (src/)
packages/proto/       # Protobuf definitions (api/v1/*.proto)
infrastructure/       # Terraform + Docker
docs/                 # Product specs (Japanese)
  generated/          # Auto-generated docs (proto, godoc, ERD)
```

## Architecture

### Taskfile Structure

Root `Taskfile.yaml` includes domain-specific taskfiles from `taskfiles/` with `dir` set at include level:
- `taskfiles/docker.yaml` → dir: `infrastructure/docker`
- `taskfiles/go.yaml` → dir: `apps/api-server`
- `taskfiles/proto.yaml` → dir: `packages/proto`
- `taskfiles/ent.yaml` → dir: `apps/api-server`
- `taskfiles/web.yaml` → dir: `apps/web`

### API Server (`apps/api-server/`)

Connect RPC handlers in `internal/handler/` implement generated service interfaces from `gen/`. Each handler receives dependencies (ent client, content store, JWT verifier) via constructor injection.

**Transaction + event pattern**: resource mutations wrap DB operations in `ent.Tx`. The resource update and its corresponding event entity are saved atomically in the same transaction.

**Error handling**: uses `connectrpc.com/connect` error codes with Google `errdetails.BadRequest` field violations. Helper functions in `internal/handler/errors.go`.

**Content storage**: `internal/storage/ContentStore` interface with `S3Store` implementation. Local development uses MinIO (S3-compatible) via `S3_ENDPOINT_URL`; production uses AWS S3 directly.

### Frontend (`apps/web/`)

React 19 + Vite + Tailwind CSS 4. Path alias `@/*` maps to `src/*`.

**Provider hierarchy**: `QueryClientProvider` → `AuthProvider` → `RouterProvider`. Data fetching via TanStack Query; forms via React Hook Form; UI components via shadcn (Radix UI).

### Testing

Tests use PostgreSQL via testcontainers (`testutil.SetupPostgres` in `TestMain` starts a shared postgres:17-alpine container). Each test gets an isolated database via `testutil.NewTestClient(t)`. Test helpers (`ctxWithAuth`, `createUser`) live alongside test files. Tests run with `t.Parallel()` and table-driven subtests.

## Entity Conventions

- Resource entities should NOT have `created_at` / `updated_at` fields.
- For each update use case, create a dedicated event entity and record the event alongside the resource update.
- Timestamps belong on event entities. Name them after the verb the event represents (e.g., `registered_at`, `published_at`).

## Development Flow

This project follows spec-driven development. Before writing any implementation code, create or update the relevant spec documents in `docs/` first. Keep specs and implementation in sync by making incremental progress — update the docs, implement to match, then move on to the next piece.

## Documentation Rules

- **Single responsibility**: Each document covers one clear concern. Do not mix multiple topics in a single file.
- **Granularity**: Keep each document small enough to describe its responsibility in one sentence.
- **New documents**: When the concern differs, create a new file rather than appending to an existing one.
- **H1 heading**: Every document must start with `# Heading` on line 1 (used by the index generator).

## Specs

Specifications live in `docs/`. 

- **`docs/product/`** — Product planning (vision, scope)
- **`docs/auth/`** — Authentication, authorization, and user management
- **`docs/api/`** — API specs (Connect RPC service/method definitions)
- **`docs/entity/`** — Resource entities (data model definitions)
- **`docs/event/`** — Event entities (state change records with timestamps)
