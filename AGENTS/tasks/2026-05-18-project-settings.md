---
title: Project settings test & serve.sh seed support
date: 2026-05-18
status: completed
description: "Created empty_project seed, settings page selectors, rename test, and added --seed option to serve.sh."
tags: [tests, seeds, scripts]
---

## Task

1. Start server with clean DB, create admin user, create seed `empty_project`
2. Write test: go to settings, rename project to TestProject2, save, verify, rename back
3. Add `--seed` option to `serve.sh` (stop existing server, reset DB, apply seed)

## Context

First seeded test in the project. Settings page had no page-object file yet. `serve.sh` had no way to start with pre-populated data.

## What was done

- Created `src/seeds/empty_project.py` — seed that creates a single project via API
- Created `src/pages/settings.py` — selectors for project settings page (name input, save button)
- Created `tests/test_03_project_settings.py` — `TestProjectRename::test_rename_project_and_rename_back` (`@seeded(seed="empty_project")`)
- Updated `scripts/serve.sh` — added `--seed <name>` option, stop existing server logic, proper startup health check
- Updated `CLAUDE.md` — added "never edit semaphore/" rule, fixed selector guidance (use CSS class/role instead of adding testids)
- Updated `README.md` — added serve.sh seed examples

## Problems

- `button.primary` selector resolved to 2 elements (save + export). Fixed with sibling selector: `[data-testid='settings-testAlerts'] ~ button.primary`
- System Semaphore process on port 3100 couldn't be killed (different user). Added proper port-free check with timeout and failure message to serve.sh.
- Background pytest processes became zombies. Resolved by killing stale processes before re-running.

## Result

Files created:
- `src/seeds/empty_project.py`
- `src/pages/settings.py`
- `tests/test_03_project_settings.py`

Files modified:
- `scripts/serve.sh` — seed support, stop existing, health check
- `AGENTS/agent-primary.md` (CLAUDE.md) — never edit semaphore/, selector guidance
- `README.md` — serve.sh examples
- `AGENTS/memory/MEMORY.md` — added feedback entry
- `AGENTS/memory/feedback_no_edit_semaphore.md` — new memory file
