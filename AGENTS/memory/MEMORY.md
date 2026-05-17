# Memory

Project facts that cannot be derived from code: decisions, constraints, non-obvious patterns.
Short entries (1–3 lines) go inline below. Long entries (>3 lines) — separate file alongside, linked from here.

## Entries

- **Testing stack**: Playwright + pytest + SQLite. Use `claude-in-chrome` MCP for browser exploration during test development.
- **Selectors**: always `data-testid`, never text/labels — labels are locale-dependent.
- **Commits**: only on explicit git terminology ("commit", "закоммить"). Russian words "зафиксируй", "запиши", "сохрани" mean write files, not git commit.
