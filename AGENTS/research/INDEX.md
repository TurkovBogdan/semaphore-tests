# research — index

Research artifacts for external services and technologies: API documentation, behavior, limits.

## Rules

- Log results of researching an external service or technology into `AGENTS/research/<topic>/`.
- Create `INDEX.md` inside the subfolder from `AGENTS/research/TEMPLATE.md` and add an entry below.
- Do not duplicate into memory — research stores raw data and details, memory stores final decisions made for the project.

## Inventory

### [`browser-testing/`](browser-testing/INDEX.md) — Browser testing frameworks & MCP

Playwright vs Selenium vs Puppeteer for Python E2E testing. MCP servers for AI browser access.

- Playwright is the winner: fastest, best Python API, built-in auto-waits
- Microsoft Playwright MCP exists as official solution for AI-agent browser control
- Current decision: using claude-in-chrome for now, Playwright MCP as future option

### [`semaphore-project/`](semaphore-project/INDEX.md) — Semaphore UI architecture and structure

Full analysis of semaphoreui/semaphore: Go backend, Vue 2 frontend, REST API map, DB models, build system.

- Go backend: gorilla/mux router, gorp ORM, BoltDB/MySQL/PostgreSQL
- Vue 2 + Vuetify 2 SPA, embedded into Go binary via go:embed
- REST API at /api with session/token auth, OIDC, LDAP, 2FA
- Key entities: Project, Template, Task, Inventory, Environment, Repository, AccessKey, Runner
- Build via Taskfile.yml; Docker images for server and runner
