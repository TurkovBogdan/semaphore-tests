---
title: Semaphore UI project structure
date: 2026-05-17
description: "Architecture, directory layout, tech stack, API routes, and database layer of semaphoreui/semaphore."
tags: [semaphore, go, vue, architecture]
---

## Scope

Full analysis of the semaphoreui/semaphore repository (local clone at `../semaphore/`). Covers backend (Go), frontend (Vue 2), API surface, database layer, build system. Version ~2.16.14 (from api-docs.yml).

## High-level architecture

Semaphore UI is a web interface + API for running Ansible, Terraform/OpenTofu, PowerShell and other DevOps tools. Single Go binary serves both the REST API and the embedded Vue.js SPA.

## Directory layout

```
semaphore/
  cli/            -- Entry point (cobra CLI: server, setup, migrate, etc.)
  api/            -- HTTP handlers, router (gorilla/mux), middleware
    router.go     -- All route definitions
    projects/     -- Handlers for project-scoped resources (CRUD)
    runners/      -- Runner registration and management
    tasks/        -- Task-related handlers
    sockets/      -- WebSocket handler
    helpers/      -- Request helpers (store, context extractors)
    public/       -- Embedded frontend build (go:embed)
  db/             -- Domain models + Store interface
    bolt/         -- BoltDB (bbolt) store implementation
    sql/          -- SQL store implementation (MySQL, PostgreSQL)
    factory/      -- Store factory (selects bolt vs sql)
    migration/    -- Database migration files
  db_lib/         -- Shared DB utilities
  services/       -- Business logic layer
    tasks/        -- Task pool, task runner
    server/       -- Project service, integration service, etc.
    runners/      -- Runner service
    schedules/    -- Cron schedule service
    export/       -- Project export
    session_svc.go
  pkg/            -- Shared packages (tz, etc.)
  util/           -- Config, helpers, rand
  web/            -- Vue.js frontend (source)
    src/
      views/      -- Page-level Vue components
      components/ -- Reusable UI components
      router/     -- Vue Router config
      lib/        -- API client, helpers
      lang/       -- i18n translations
      plugins/    -- Vuetify plugin setup
  pro/            -- Pro/commercial features (Terraform state, subscriptions, roles)
  pro_interfaces/ -- Interfaces for pro features (allows open-source build without pro)
  deployment/     -- Docker files (server, runner, debug)
  test/           -- Integration/E2E test configs
  .dredd/         -- Dredd API testing setup
  hook_helpers/   -- Git hook helpers
  examples/       -- Example configs
```

## Tech stack

### Backend (Go)
- **Router**: gorilla/mux
- **ORM/SQL builder**: go-gorp/gorp v3 + Masterminds/squirrel
- **Databases**: BoltDB (bbolt) for embedded, MySQL (go-sql-driver), PostgreSQL (lib/pq)
- **Auth**: Session-based (gorilla/securecookie), OIDC (coreos/go-oidc), LDAP (go-ldap), TOTP (pquerna/otp)
- **WebSocket**: gorilla/websocket
- **CLI**: spf13/cobra
- **Logging**: sirupsen/logrus
- **Git**: go-git/go-git v5
- **Cron**: robfig/cron v3
- **Testing**: stretchr/testify

### Frontend (Vue 2)
- **Framework**: Vue 2.6
- **UI library**: Vuetify 2.6
- **Router**: vue-router 3
- **HTTP client**: axios
- **i18n**: vue-i18n 8
- **Code editor**: vue-codemirror
- **Charts**: chart.js + vue-chartjs
- **Build**: @vue/cli-service 5

## API structure

Base path: `/api`

### Public (no auth)
- `GET /api/ping` -- health check (returns "pong")
- `POST /api/auth/login` -- login (username + password)
- `POST /api/auth/logout` -- logout
- `POST /api/auth/verify` -- verify session (2FA)
- `POST /api/auth/recovery` -- recovery session
- `GET /api/auth/oidc/{provider}/login` -- OIDC login
- `GET /api/auth/oidc/{provider}/redirect` -- OIDC redirect
- `POST /api/internal/runners` -- register runner

### Internal (runner auth)
- `GET/PUT/DELETE /api/internal/runners` -- runner self-management

### Webhooks (no auth, alias-based)
- `POST/GET /api/integrations/{integration_alias}` -- receive integration webhook
- `GET/POST/LOCK/UNLOCK /api/terraform/{alias}` -- Terraform state backend

### Authenticated
- `GET /api/info` -- system info
- `GET /api/projects` -- list projects
- `POST /api/projects` -- create project
- `GET /api/events` -- global events
- `GET /api/users` -- list users
- `GET /api/user` -- current user
- `GET /api/user/tokens` -- API tokens
- `GET /api/ws` -- WebSocket

### Admin
- `GET /api/options` -- system options
- `GET /api/runners` -- all runners
- `GET /api/roles` -- global roles
- `DELETE /api/cache` -- clear cache
- `GET /api/admin/info` -- admin info
- `GET /api/tasks` -- all tasks

### Project-scoped (`/api/project/{project_id}/...`)
Resources: keys, repositories, inventory, environment, templates, schedules, views, integrations, tasks, runners, roles, users, secret_storages, backup.
Each resource supports standard CRUD + refs endpoints.
Special: `/tasks/{task_id}/output`, `/tasks/{task_id}/stop`, `/tasks/{task_id}/confirm`, `/tasks/{task_id}/reject`.

## Database models (db/ package)

Key entities:
- **User** -- accounts, admin flag, LDAP/external
- **Project** -- top-level container
- **ProjectUser** -- many-to-many with role
- **AccessKey** -- SSH keys, login/password, none (types: ssh, login_password, none)
- **Repository** -- Git repo reference (URL + access key)
- **Inventory** -- static, static-yaml, file (types)
- **Environment** -- key-value + JSON env vars + secrets
- **Template** -- task template (ansible, terraform, etc.), links to repo, inventory, environment, keys
- **Task** -- running/completed job instance
- **Schedule** -- cron-based task scheduling
- **View** -- UI grouping of templates
- **Integration** -- webhook triggers
- **Runner** -- external task runners
- **Session** -- user sessions
- **APIToken** -- API auth tokens
- **Event** -- audit log entries
- **SecretStorage** -- external secret backends (Vault, AWS SM, etc.)

Store interface (`db.Store`) abstracts all persistence. Implementations: `db/bolt/` (BoltDB), `db/sql/` (MySQL/PostgreSQL).

## Auth flow

1. `POST /api/auth/login` with `{auth, password}` -- returns session cookie
2. If 2FA enabled: `POST /api/auth/verify` with TOTP code
3. API tokens: `Authorization: Bearer <token>` header
4. OIDC: redirect-based flow via `/api/auth/oidc/{provider}/login`

## Build system

Uses [Task](https://taskfile.dev/) (`Taskfile.yml`):
- `task deps` -- install Go + npm dependencies
- `task build:fe` -- build Vue app (output to `api/public/`)
- `task build:be` -- build Go binary (output to `bin/semaphore`)
- `task build` -- both
- `task test:be` -- `go test ./...`
- `task test:fe` -- `npm run test:unit`
- `task dredd:test` -- API integration tests via Dredd

Docker images: `deployment/docker/server/Dockerfile`, `deployment/docker/runner/Dockerfile`.

## Web UI pages (Vue Router)

- `/auth/login` -- login page
- `/project/new` -- create project
- `/project/:projectId/history` -- task history (default)
- `/project/:projectId/templates` -- task templates
- `/project/:projectId/templates/:templateId/tasks|details|perms|state` -- template detail
- `/project/:projectId/environment` -- environment vars
- `/project/:projectId/inventory` -- inventories
- `/project/:projectId/repositories` -- git repos
- `/project/:projectId/keys` -- access keys
- `/project/:projectId/team` -- project members
- `/project/:projectId/schedule` -- schedules
- `/project/:projectId/settings` -- project settings
- `/project/:projectId/integrations` -- webhooks
- `/project/:projectId/runners` -- runners
- `/project/:projectId/stats` -- statistics
- `/project/:projectId/secret_storages` -- secret storages
- `/users` -- user management (admin)
- `/runners` -- global runners (admin)
- `/roles` -- roles (admin)
- `/tasks` -- global tasks (admin)
- `/apps` -- apps (admin)
- `/tokens` -- API tokens

## Additional files

- [api-payloads.md](api-payloads.md) — exact JSON payloads for all CRUD endpoints, entity dependency graph

## References

- GitHub: https://github.com/semaphoreui/semaphore
- Docs: https://semaphoreui.com/docs/
- API docs (Swagger): https://semaphoreui.com/api-docs
- Local clone: `../semaphore/` relative to project root
