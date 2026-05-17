#!/usr/bin/env bash
#
# Install macOS dependencies and start Semaphore server.
# Usage:  ./scripts/mac/serve.sh

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

# ─── start server ───────────────────────────────────────────────────────────

exec "$ROOT_DIR/scripts/serve.sh" "$@"
