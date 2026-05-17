#!/usr/bin/env bash
#
# One-time setup: install uv, Python deps, Playwright browsers (+ system deps on Linux).
# Usage:  ./scripts/setup.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OS="$(uname -s)"

info()  { printf '\033[1;34m→ %s\033[0m\n' "$*"; }
ok()    { printf '\033[1;32m✓ %s\033[0m\n' "$*"; }

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

info "Installing Playwright browsers..."
if [[ "$OS" == "Linux" ]]; then
    (cd "$ROOT_DIR" && uv run playwright install --with-deps chromium)
else
    (cd "$ROOT_DIR" && uv run playwright install chromium)
fi
ok "Playwright ready"

echo ""
ok "Setup complete. Run tests with: ./scripts/test.sh"
