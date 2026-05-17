---
title: Test infrastructure — build, run, first tests
date: 2026-05-18
status: completed
description: "Full test infrastructure: build/test scripts, .env config, tools package, pytest fixtures, test markers, first auth test suite. SQLite DB, headed/headless browser."
tags: [testing, infrastructure, semaphore, build, playwright]
---

## Task

1. Create test directory structure with pytest fixtures
2. Build Semaphore from source (Go backend + Vue.js frontend)
3. Create utilities to start/stop Semaphore server
4. Create utilities to clean/reinitialize SQLite database
5. Create reusable scripts: `scripts/build.sh` (rebuild) and `scripts/test.sh` (run tests)
6. Centralize config in `.env` (ports, credentials, workers, browser visibility, slowmo)
7. Define test group markers (clean_db, seeded, parallel)
8. Write first test suite: auth required checks

## Context

Need a deterministic test environment that can spin up a real Semaphore server with a fresh database for each test session. Must be reproducible: when a new Semaphore release is pulled into `semaphore/`, one script rebuilds everything. Browser tests must support headed (visible) and headless modes with configurable speed.

## What was done

- Installed Go 1.24.13 into `vendor/go/`
- Built Vue.js frontend (`npm install && npm run build` in `semaphore/web/`)
- Built Semaphore binary (57MB) into `vendor/semaphore`
- Created `tools/` package:
  - `config.py` — generates SQLite config.json, reads `.env`, manages paths and defaults
  - `server.py` — `SemaphoreServer` class with start/stop/restart_clean, health check polling, context manager
  - `database.py` — `reset_database()` (delete DB → migrate → create admin), `clean_data()`
- Created `tests/` directory with `conftest.py` — owns full server lifecycle:
  - `get_server()` — singleton: write config → reset DB → start server
  - `semaphore_server` (session) — yields server, stops on teardown
  - `_handle_clean_db` (autouse) — `restart_clean()` when `@clean_db` marker present
  - `_handle_seeded` (autouse) — `restart_clean()` + run seed module when `@seeded` marker present
  - `browser_type_launch_args` — headless/headed from `.env` or `--headed` CLI flag, `slow_mo` support
  - `_pause_after_tests` — configurable pause before browser closes (`SEMAPHORE_TEST_PAUSE`)
- Created `scripts/build.sh` — full rebuild: Go toolchain → frontend → binary → DB reset → optional verify
- Created `scripts/test.sh` — thin pytest wrapper; supports `--headed`/`--headless` overrides
- Created `.env` / `.env.example` with all settings
- Registered pytest markers in `pyproject.toml`: `clean_db`, `seeded`, `parallel`
- Created `tools/session.py` — `login()`, `logout()`, `clear_session()` helpers using `data-testid` selectors
- Created `tools/seeds/__init__.py` — seed function directory for `@seeded` marker
- Wrote first test: `tests/test_01_auth.py` (8 tests, all pass):
  - `TestAuthRequired`: root redirects, login form visible, API requires auth, ping is public
  - `TestLogin`: wrong credentials rejected, valid login redirects, session persists, cleared session requires reauth
- Migrated from BoltDB to SQLite (BoltDB deprecated, removed in 2.19)
- Updated `AGENTS.md` with full project docs and test marker rules
- Unified `.claude/memory` → symlink to `AGENTS/memory/`

## Result

Files created/modified:
- `scripts/build.sh` — one-command rebuild
- `scripts/test.sh` — one-command test runner with server lifecycle
- `.env` / `.env.example` — all configurable settings
- `tools/__init__.py`, `tools/config.py`, `tools/server.py`, `tools/database.py`, `tools/session.py`, `tools/seeds/__init__.py`
- `tests/__init__.py`, `tests/conftest.py`, `tests/test_01_auth.py`
- `pyproject.toml` — pytest markers registered
- `.gitignore` — `.testdata/`, `vendor/`, `.env`
- `AGENTS/agent-primary.md` — filled with real project data

`.env` settings:
- `SEMAPHORE_TEST_PORT=3100`
- `SEMAPHORE_TEST_HEADED=true/false` — show/hide browser
- `SEMAPHORE_TEST_SLOWMO=0..N` — ms delay per Playwright action
- `SEMAPHORE_TEST_PAUSE=0..N` — seconds to keep browser open after tests
- `SEMAPHORE_TEST_WORKERS=4` — parallel worker count
- `GO_VERSION=1.24`

Runtime artifacts (gitignored):
- `vendor/go/`, `vendor/gopath/`, `vendor/semaphore`
- `.testdata/config.json`, `.testdata/database.sqlite`, `.testdata/tmp/`

Key discovery: Semaphore frontend uses `data-testid` attributes (`auth-username`, `auth-password`, `auth-signin`) — more reliable than labels which change with locale.

## Updates

### 2026-05-18 — serve script, new project tests

- Added `scripts/serve.sh` — starts Semaphore server and opens URL in browser (Ctrl+C to stop)
- Added `tests/test_02_new_project.py` (3 tests):
  - `TestNewProjectPage`: empty DB shows new project form
  - `TestCreateEmptyProject`: creates empty project, verifies all sections empty
  - `TestCreateDemoProject`: creates demo project with dashboard, sidebar, templates, inventory, keys, repos
- Added page selectors in `src/pages/` for new project and dashboard pages
