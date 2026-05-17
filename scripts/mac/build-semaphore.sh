#!/usr/bin/env bash
#
# Install macOS dependencies and build Semaphore from source.
# Usage:  ./scripts/mac/build-semaphore.sh [--verify]
#
# Prerequisites: Homebrew (https://brew.sh)
# Installs: Node.js (for Vue frontend build)
# Go is downloaded automatically by build.sh.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

info()  { printf '\033[1;34m→ %s\033[0m\n' "$*"; }
ok()    { printf '\033[1;32m✓ %s\033[0m\n' "$*"; }
fail()  { printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

# ─── check Homebrew ─────────────────────────────────────────────────────────

command -v brew &>/dev/null || fail "Homebrew not found. Install from https://brew.sh"

# ─── check semaphore source ─────────────────────────────────────────────────

[[ -d "$ROOT_DIR/semaphore" ]] || fail "Semaphore source not found. Clone it first:
  git clone https://github.com/semaphoreui/semaphore.git $ROOT_DIR/semaphore"

# ─── install dependencies ───────────────────────────────────────────────────

install_if_missing() {
    local cmd="$1" pkg="${2:-$1}"
    if command -v "$cmd" &>/dev/null; then
        ok "$cmd already installed"
    else
        info "Installing $pkg..."
        brew install "$pkg"
        ok "$pkg installed"
    fi
}

install_if_missing node
install_if_missing curl

# ─── build ──────────────────────────────────────────────────────────────────

exec "$ROOT_DIR/scripts/build.sh" "$@"
