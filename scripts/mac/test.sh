#!/usr/bin/env bash
#
# Install macOS dependencies and run the test suite.
# Usage:  ./scripts/mac/test.sh [pytest args...]
#
# Installs uv, Python dependencies, and Playwright browsers if missing.
# All arguments are forwarded to scripts/test.sh (and then to pytest).

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

info()  { printf '\033[1;34m→ %s\033[0m\n' "$*"; }
ok()    { printf '\033[1;32m✓ %s\033[0m\n' "$*"; }
fail()  { printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

# ─── install uv ─────────────────────────────────────────────────────────────

if command -v uv &>/dev/null; then
    ok "uv already installed"
else
    info "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    ok "uv installed"
fi

# ─── install Python dependencies ────────────────────────────────────────────

info "Syncing Python dependencies..."
(cd "$ROOT_DIR" && uv sync --quiet)
ok "Dependencies synced"

# ─── install Playwright browsers ────────────────────────────────────────────

info "Ensuring Playwright browsers are installed..."
(cd "$ROOT_DIR" && uv run playwright install chromium 2>&1 | tail -1)
ok "Playwright browsers ready"

# ─── run tests ──────────────────────────────────────────────────────────────

exec "$ROOT_DIR/scripts/test.sh" "$@"
