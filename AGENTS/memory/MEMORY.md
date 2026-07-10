# Memory

Project facts that cannot be derived from code: decisions, constraints, non-obvious patterns.
Short entries (1–3 lines) go inline below. Long entries (>3 lines) — separate file alongside, linked from here.

## Entries

- **Testing stack**: Playwright + pytest + SQLite. Use `claude-in-chrome` MCP for browser exploration during test development.
- **Selectors**: prefer `data-testid`, never text/labels — labels are locale-dependent. If no testid, use stable CSS class/role/type.
- [Never edit semaphore source](feedback_no_edit_semaphore.md) — use alternative selectors instead of adding testids there.
- **Commits**: only on explicit git terminology ("commit", "закоммить"). Russian words "зафиксируй", "запиши", "сохрани" mean write files, not git commit.
- **Go version**: keep `GO_VERSION` in `.env`/`.env.example` synced with `go 1.x.y` in `semaphore/go.mod` (currently `1.26.4`). `build.sh` accepts a full patch version (`1.26.4`) or `major.minor` (auto-appends `.0`).
- **Orphan server = stale data**: a leftover `./vendor/semaphore server` on the test port answers `/api/ping`, so `SemaphoreServer.start()` thinks it started and tests silently hit stale data (deleted rows reappear). Before manual server work run `./scripts/kill.sh`; check with `ss -ltnp | grep :3100`. `start()` now raises if its own process dies (port busy).
- **SQLite WAL sidecars**: reset must delete `database.sqlite` **and** `-wal`/`-shm`/`-journal` — a stale WAL replays old committed rows on the next migrate. `reset_database` handles this via `_remove_db_files()`. Never `rm` only `database.sqlite`; use `database.sqlite*`.
- **Inventory form has no testids**: `InventoryForm.vue` fields are addressed positionally in `src/pages/inventory.py` (0 name, 1 user-cred, 2 sudo-cred, 3 type, 4 file-path). Vuetify dropdown options: scope to the newest `.v-menu__content:visible` to avoid index cross-talk between a closing menu and a new one.
