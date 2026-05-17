# TASKS INDEX

Log of tasks for the project. Each task in a new area — a separate file. Filename format: `YYYY-MM-DD-slug.md`.

## Rules

- Create `AGENTS/tasks/YYYY-MM-DD-slug.md` from `AGENTS/tasks/TEMPLATE.md` at the start of a task.
- The slug describes the area, not the action: `auth-flow`, `build-pipeline`, `payment-api`.
- Add an entry to the "In work" table below.
- Fill in "What was done", "Problems", "Result" and set status to `completed` on completion; then move the row to "Completed".

## In work

Tasks currently being worked on.

| File | Date | Description |
|------|------|-------------|

## Completed

Tasks the user has confirmed as complete.

| File | Date | Description |
|------|------|-------------|
| [2026-05-17-project-setup.md](2026-05-17-project-setup.md) | 2026-05-17 | uv init, Python 3.14, pytest + playwright |
| [2026-05-18-test-infrastructure.md](2026-05-18-test-infrastructure.md) | 2026-05-18 | Build/test scripts, tools, fixtures, markers, first auth tests, SQLite, headed browser |
| [2026-05-18-project-settings.md](2026-05-18-project-settings.md) | 2026-05-18 | empty_project seed, settings page test, serve.sh --seed option |

## Deferred

Tasks paused at the user's request. Move the row here from "In work" and set status to `deferred` in the task's frontmatter.

| File | Date | Description |
|------|------|-------------|

## Archive

Archiving is performed only at the user's request: move the task file into `AGENTS/tasks/archive/`, remove its row from this index, and add a row to [`AGENTS/tasks/archive/INDEX.md`](AGENTS/tasks/archive/INDEX.md).
