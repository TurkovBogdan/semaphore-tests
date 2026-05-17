---
name: Never edit semaphore source
description: Never modify files in semaphore/ directory — it's an external project we only build and run
type: feedback
originSessionId: 5a4696ec-d4e7-44df-bb5f-f2738e6ef7d0
---
Never edit files in `semaphore/` — it's an external project, we only build and run it.

**Why:** User explicitly forbids it. Semaphore is not our code, we should not modify it for test infrastructure needs.

**How to apply:** When an element lacks `data-testid`, use other stable selectors (CSS class, role, type, structural position) instead of adding testids to Semaphore source.
