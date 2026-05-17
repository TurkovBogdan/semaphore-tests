---
title: Browser testing frameworks for Python
date: 2026-05-17
description: "Comparison of Playwright, Selenium, Puppeteer for deterministic E2E web UI testing. MCP integration options for AI-assisted browser access."
tags: [testing, browser, playwright, mcp]
---

## Scope

Evaluated browser automation frameworks for Python-based deterministic E2E testing of the project's web frontend. Covered: Playwright, Selenium, Puppeteer. Also researched MCP servers that provide browser access to AI agents.

## Findings: Framework comparison

| Criteria | Playwright | Selenium | Puppeteer |
|---|---|---|---|
| Protocol | WebSocket / CDP direct | HTTP via WebDriver (extra layer) | CDP, Chromium only |
| Python API | Full sync + async | Full, less concise | No official Python API |
| Browsers | Chromium, Firefox, WebKit | All + legacy (IE) | Chromium only |
| Headless | Out of the box | Requires explicit config | Out of the box |
| Speed | 30-50% faster than Selenium | Baseline | Fast, single browser |
| Auto-waits | Built-in (visibility, stability, interactivity) | Manual waits/sleeps | Partial |
| Debugging | Trace Viewer, Inspector, video, screenshots | External tools | DevTools |
| Install | `pip install playwright && playwright install` | `pip install selenium` + drivers | Requires Node.js |

**Winner: Playwright** — faster, more reliable, simpler setup, best Python API.

## Findings: MCP browser access

### Microsoft Playwright MCP (official)

- GitHub: `microsoft/playwright-mcp`
- 25+ tools: navigation, clicks, form fills, screenshots, accessibility tree
- Headless and headed modes
- Direct Claude Code integration documented
- Install: `npx @playwright/mcp@latest`
- Config for Claude Code:
  ```json
  {
    "mcpServers": {
      "playwright": {
        "command": "npx",
        "args": ["@playwright/mcp@latest"]
      }
    }
  }
  ```

### Other MCP servers

- `executeautomation/mcp-playwright` — third-party, extended API/browser support
- `craigsdennis/playwright-mcp-example` — Cloudflare-optimized for Workers

### Recommended approach (two layers)

1. **MCP for exploration** — AI uses Playwright MCP to open frontend, discover elements and behavior
2. **Deterministic tests in Python** — classic `pytest` + `playwright` tests that run autonomously without AI

## Limits / quirks

- Playwright MCP uses accessibility tree instead of visual models — no CSS selectors needed but may miss visual-only elements
- For production-grade MCP test suites, auth handling and token costs are primary risks
- Puppeteer has no official Python wrapper — not viable for Python-first projects

## Current decision

Using native `claude-in-chrome` MCP for browser access during initial phase. Playwright MCP is a documented alternative for future migration.

## References

- https://playwright.dev/docs/getting-started-mcp
- https://github.com/microsoft/playwright-mcp
- https://github.com/executeautomation/mcp-playwright
- https://www.browserstack.com/guide/playwright-vs-selenium
- https://www.webfuse.com/blog/playwright-vs-selenium-which-automation-tool-is-right-for-you-in-2026
- https://testomat.io/blog/playwright-mcp-claude-code/
- https://bug0.com/blog/playwright-mcp-servers-ai-testing
