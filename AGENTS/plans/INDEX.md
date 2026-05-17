# PLANS INDEX

Implementation plans for the project. Each plan in a separate file. Filename format: `YYYY-MM-DD-slug.md`.

## Rules

- Create `AGENTS/plans/YYYY-MM-DD-slug.md` from `AGENTS/plans/TEMPLATE.md` when the user asks for a plan.
- The slug describes the area, not the action.
- Add an entry to the "In work" table below.
- Set status to `completed` on completion; then move the row to "Completed".

## In work

Plans currently being executed.

| File | Date | Description |
|------|------|-------------|

## Completed

Plans the user has confirmed as complete.

| File | Date | Description |
|------|------|-------------|

## Deferred

Plans paused at the user's request. Move the row here from "In work" and set status to `deferred` in the plan's frontmatter.

| File | Date | Description |
|------|------|-------------|

## Archive

Archiving is performed only at the user's request: move the plan file into `AGENTS/plans/archive/`, remove its row from this index, and add a row to [`AGENTS/plans/archive/INDEX.md`](AGENTS/plans/archive/INDEX.md).
