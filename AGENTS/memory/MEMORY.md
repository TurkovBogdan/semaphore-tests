# Memory

Project facts that cannot be derived from code: decisions, constraints, non-obvious patterns.
Short entries (1–3 lines) go inline below. Long entries (>3 lines) — separate file alongside, linked from here.

## Entries

- **Testing stack**: Playwright + pytest + SQLite. Use `claude-in-chrome` MCP for browser exploration during test development.
- **Selectors**: prefer `data-testid`, never text/labels — labels are locale-dependent. If no testid, use stable CSS class/role/type.
- [Never edit semaphore source](feedback_no_edit_semaphore.md) — use alternative selectors instead of adding testids there.
- **Commits**: only on explicit git terminology ("commit", "закоммить"). Russian words "зафиксируй", "запиши", "сохрани" mean write files, not git commit.
