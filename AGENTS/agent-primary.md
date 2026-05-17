## About the project

E2E test suite for the Semaphore UI web application. Tests run against a real Semaphore server (Go backend + Vue 2 frontend) built from source in `semaphore/`. Uses Playwright for browser automation and pytest as the test runner. Database: SQLite (file-based, no external server).

## Structure

```
tests/                  — test files, one per feature area (test_NN_name.py)
  conftest.py           — session fixtures, server lifecycle, markers
src/                    — Python utilities
  config.py             — env loading, paths, config generation
  server.py             — SemaphoreServer: start/stop/restart_clean
  database.py           — reset_database, migrate, create admin
  session.py            — login(), logout(), clear_session()
  pages/                — Playwright selectors, one file per page/interface
  seeds/                — DB seed functions for @seeded tests (via Semaphore API)
    api.py              — SemaphoreAPI client for seeds
tool_db.py              — DB inspector (uv run tool_db.py <command>)
scripts/                — user-facing shell scripts (build, test, serve + platform wrappers in mac/, linux/)
semaphore/              — Semaphore source code (Go + Vue 2), not our code
vendor/                 — Go toolchain, compiled binary (gitignored)
.testdata/              — runtime: SQLite DB, config, tmp (gitignored)
.env                    — port, credentials, worker count (gitignored, see .env.example)
AGENTS/                 — memory, tasks, research, docs, plans
```

## Configuration (`.env`)

Port, credentials, and test settings. See `.env.example` for all variables.

- `SEMAPHORE_TEST_PORT` — server port (default `3100`)
- `SEMAPHORE_TEST_ADMIN_USER` / `SEMAPHORE_TEST_ADMIN_PASS` — admin credentials (default `admin` / `admin123`)
- `SEMAPHORE_TEST_ADMIN_EMAIL` — admin email (default `admin@test.local`)
- `SEMAPHORE_TEST_WORKERS` — parallel test workers (default `4`, `0` = sequential)

## Running and building

- Build everything: `./scripts/build.sh` (add `--verify` to test server health)
- Run tests: `uv run pytest tests/`
- Run parallel tests only: `uv run pytest tests/ -m parallel -n $SEMAPHORE_TEST_WORKERS`
- Start server manually: `SemaphoreServer(port).start()` via `src/server.py`, or `./scripts/serve.sh`
- Stop server: `server.stop()` in Python, or `./scripts/kill.sh` to kill all Semaphore processes
- Entry point: `tests/conftest.py` (session fixtures start/stop server)

## Testing

- Run the full suite: `uv run pytest tests/`
- Run a single test / subset: `uv run pytest tests/test_foo.py -k test_name`
- Where tests live: `tests/`
- Where to add new tests: `tests/` — one file per feature area
- Fixtures / test data: `tests/conftest.py`, seed functions in `src/seeds/`
- External dependencies: real Semaphore server (started by fixtures), SQLite DB

### Server lifecycle

`tests/conftest.py` owns the full server lifecycle — no external process management:

1. **Session start**: `get_server()` creates config → resets DB → starts Semaphore → waits for `/api/ping`
2. **Between tests**: markers trigger `restart_clean()` (stop → delete DB → migrate → create admin → start)
3. **Session end**: `semaphore_server` fixture teardown calls `stop()`

Stopping and restarting the server is a normal, expected operation — not an error path. Tools in `src/` (server.py, database.py) are designed for this: kill the process, wipe the DB, bring it back up clean. This keeps test isolation simple and deterministic.

`scripts/test.sh` is a thin wrapper — it loads `.env`, passes `--headed` to pytest, and forwards arguments. It does not manage the server.

### Test groups (markers)

Tests are organized with pytest markers. Each marker defines isolation and parallelism rules:

| Marker | DB state | Parallelism | Use for |
|--------|----------|-------------|---------|
| `@pytest.mark.clean_db` | Fresh DB before each test | Sequential only | Destructive tests, admin operations, settings changes |
| `@pytest.mark.seeded(seed="name")` | Pre-populated via seed function | Sequential within seed group | CRUD tests that need existing data (projects, templates, etc.) |
| `@pytest.mark.parallel` | Shared read-only or isolated data | Up to `SEMAPHORE_TEST_WORKERS` threads | Read-only checks, UI navigation, non-mutating API tests |
| `@pytest.mark.clean_browser` | — (clears cookies) | Any | Tests that need a clean browser session without server restart |
| (no marker) | Inherited from session fixture | Sequential | Default, simple tests |

Rules:
- `clean_db` tests reset the database — never run them in parallel
- `seeded` tests share a pre-populated DB within their seed group — sequential within group, groups can be parallelized
- `parallel` tests must not mutate shared state — safe for concurrent execution
- Worker count is set in `.env` as `SEMAPHORE_TEST_WORKERS` (0 = all sequential)
- Seeds live in `src/seeds/` as Python functions that create entities via Semaphore API

### Writing tests

- **Tests must be deterministic.** Every test must produce the same result on every run, regardless of execution order, previous test state, or timing. No flaky tests — if a test fails intermittently, fix the root cause (missing wait, shared state leak, race condition), don't retry or increase timeouts blindly.
- Each test must fully own its preconditions: log in fresh, navigate explicitly, don't assume anything left over from a previous test. The browser context is shared across the session — always treat it as potentially dirty.
- **One test per scenario.** A scenario is a complete user action with a single expected outcome. Verify everything about that outcome in the same test — don't split element-level checks into separate tests.
- One file per feature area in `tests/`
- **Never match by visible text** — the UI is multilingual, labels and button names change with locale. Use `data-testid` attributes, element IDs, `name`/`type`/`role` attributes, or stable CSS classes (e.g. Vuetify `button.success`). If a needed element has no `data-testid`, add one in `semaphore/` source rather than matching by text
- **All selectors live in `src/pages/`** — one file per page/interface (e.g. `login.py`, `sidebar.py`, `dashboard.py`). Tests and helpers import selectors from there. When a `data-testid` changes, update one file
- For SPA navigation after actions, use `page.wait_for_url(lambda url: ..., timeout=N)` — glob patterns don't work reliably with Vue router
- Session helpers: `src/session.py` — `login()`, `logout()`, `clear_session()`
- Always pick the least-destructive marker: prefer `parallel` > `seeded` > `clean_db`
- After adding, removing, or renaming tests — update [`TESTS.md`](../TESTS.md)

### [Test index](../TESTS.md)

`TESTS.md` in the project root is the single source of truth for what every test checks. Format: one section per test file, one table per test class, columns `Test` and `Verifies`. The marker is shown next to the class name.

Rules:
- **Always keep in sync.** When you add, remove, or rename a test, update `TESTS.md` in the same step.
- One row per test function. `Verifies` column — short (under 15 words), describes the specific behavior being asserted.
- Group by file, then by class. Show the marker (`@clean_db`, `@seeded(seed="...")`, `@parallel`) next to the class name.
- Do not duplicate test code or fixtures — only names and what they verify.

## Seed tooling

Tools for creating seed data and inspecting the database.

### API client — `src/seeds/api.py`

`SemaphoreAPI(base_url)` — HTTP client that logs in as admin and exposes typed methods for every entity: `create_project`, `create_key_none`/`create_key_login`/`create_key_ssh`/`create_key_string`, `create_repository`, `create_inventory`, `create_environment`, `create_template`, `create_view`, `create_schedule`, `run_task`. Plus `list_*` methods for verification. Every seed module should use it instead of raw `requests`.

### DB inspector — `tool_db.py`

`uv run tool_db.py <command>` — inspect `.testdata/database.sqlite`. Pure Python (stdlib `sqlite3`), no platform dependencies.

| Command | What it does |
|---------|-------------|
| `tables` | List all tables |
| `schema [TABLE]` | Show DDL (all or one table) |
| `count [TABLE]` | Row counts (non-empty tables, or one) |
| `dump TABLE` | All rows in a table |
| `query "SQL"` | Arbitrary SQL |
| `users` / `projects` | Quick-view helpers |
| `keys` / `repos` / `templates` / `tasks PROJECT_ID` | Project-scoped helpers |

### API payloads reference

`AGENTS/research/semaphore-project/api-payloads.md` — exact JSON payloads for all CRUD endpoints and entity dependency graph.

## At the start of work

- Read [`AGENTS/memory/MEMORY.md`](AGENTS/memory/MEMORY.md)
- Read [`AGENTS/tasks/INDEX.md`](AGENTS/tasks/INDEX.md)
- Read [`AGENTS/docs/INDEX.md`](AGENTS/docs/INDEX.md)

## Working rules

### [Memory](AGENTS/memory/MEMORY.md)

Project facts that cannot be derived from code: decisions, constraints, non-obvious patterns.
- Claude's memory directory is a symlink to `AGENTS/memory/`.
- Short entries (1–3 lines) — inline in `MEMORY.md`: `- **Topic**: description`.
- Long entries (>3 lines) — separate file alongside, linked from `MEMORY.md`.
- Write after: architectural changes, finding non-obvious behavior, solving a non-obvious problem.
- Do not duplicate what can be read from the code.

### [Tasks](AGENTS/tasks/INDEX.md)

Log of work done on the project, one file per area of work. The index must be read at the start of every session.

### [Docs](AGENTS/docs/INDEX.md)

We follow the self-documenting code principle, but write docs when something cannot be expressed by the code alone: complex pipelines or workflows, architecture overviews, data schemas, protocols and integration contracts, configuration reference, deployment / infrastructure, operational runbooks. Docs may contain context important for the task — check the index at the start of a session.

### [Plans](AGENTS/plans/INDEX.md)

Stores implementation plans. The folder contains an index and a template. Use only when the user explicitly asks to create, update, or read a plan.

### [Research](AGENTS/research/INDEX.md)

Contains a log of research conducted within this project. When the user asks for research, reading `AGENTS/research/INDEX.md` is mandatory before anything else.
