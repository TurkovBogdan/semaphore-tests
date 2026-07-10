---
title: Inventory section modal tests
date: 2026-07-10
status: completed
description: "E2E tests for the project Inventory page and its modals (create/edit/delete). Added a seed and inventory page selectors; hardened DB reset and server startup against stale state."
tags: [inventory, tests, infra]
---

## Task

"Давай добавим тесты работы раздела инвенторя, его модалок" — add tests for the Inventory
section and its modals.

## Context

Only auth / new-project / settings tests existed. No inventory coverage, no inventory
selectors, no seed with inventory data. Inventory UI (InventoryForm.vue / EditDialog.vue)
has no data-testid on form fields, so fields are addressed positionally.

## What was done

- Seed `src/seeds/inventory_project.py`: project + login_password key + two inventories
  (static + file), both with `ssh_key_id` so the edit form loads valid.
- Selectors `src/pages/inventory.py`: toolbar "New Inventory" menu, table rows, row
  edit/delete icons, EditDialog (`editDialog-save`/`editDialog-close`), positional form
  fields, dropdown option menus, YesNoDialog confirm.
- Tests `tests/test_04_inventory.py` (all `@seeded(seed="inventory_project")`):
  - `test_new_inventory_modal_opens_and_closes` — menu opens dialog, close dismisses it
  - `test_create_file_inventory` — create File inventory via modal, verify table + API
  - `test_edit_inventory_name` — edit modal pre-fills, rename reflected in table + API
  - `test_delete_inventory_via_confirm_dialog` — YesNoDialog deletes, verify table + API
- Infra hardening (see Problems): `src/database.py` reset now wipes WAL/SHM sidecars;
  `src/server.py` start() fails loudly if its process dies (port held by an orphan).
- Updated `TESTS.md`.

## Problems

- **Orphan server served stale data.** A leftover `./vendor/semaphore server` on port
  3100 (from manual runs) kept answering `/api/ping`. `SemaphoreServer.start()` trusted
  that ping, so each "fresh" server actually talked to the orphan, whose open SQLite
  handle kept resurrecting deleted rows — tests saw 3, then 4 inventories. Fixed by
  killing the orphan and making `start()` raise if `self.process` exits during startup.
- **Stale WAL/SHM.** `reset_database` deleted only `database.sqlite`, leaving `-wal`/`-shm`
  behind; a later migrate replayed old committed transactions. Reset now removes all
  sidecar files.
- **Dropdown index cross-talk.** Selecting a v-select option while a previous autocomplete
  menu was still closing indexed across both menus. Option picking is now scoped to the
  newest visible `.v-menu__content`.

## Result

Created: `src/seeds/inventory_project.py`, `src/pages/inventory.py`,
`tests/test_04_inventory.py`.
Changed: `src/database.py`, `src/server.py`, `TESTS.md`.
Full suite: 17 passed, stable across repeated runs.
