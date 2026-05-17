#!/usr/bin/env bash
#
# Install Linux dependencies and build Semaphore from source.
# Usage:  ./scripts/linux/build-semaphore.sh [--verify]
#
# Supports: Debian/Ubuntu (apt), Fedora/RHEL (dnf), Arch (pacman).
# Installs: Node.js, npm, curl (for Vue frontend build)
# Go is downloaded automatically by build.sh.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

info()  { printf '\033[1;34m→ %s\033[0m\n' "$*"; }
ok()    { printf '\033[1;32m✓ %s\033[0m\n' "$*"; }
fail()  { printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

# ─── check semaphore source ─────────────────────────────────────────────────

[[ -d "$ROOT_DIR/semaphore" ]] || fail "Semaphore source not found. Clone it first:
  git clone https://github.com/semaphoreui/semaphore.git $ROOT_DIR/semaphore"

# ─── detect package manager ─────────────────────────────────────────────────

if command -v apt-get &>/dev/null; then
    PKG_MGR="apt"
elif command -v dnf &>/dev/null; then
    PKG_MGR="dnf"
elif command -v pacman &>/dev/null; then
    PKG_MGR="pacman"
else
    fail "No supported package manager found (apt, dnf, pacman)"
fi

ok "Package manager: $PKG_MGR"

# ─── install dependencies ───────────────────────────────────────────────────

install_pkg() {
    local cmd="$1"; shift
    if command -v "$cmd" &>/dev/null; then
        ok "$cmd already installed"
        return
    fi
    info "Installing $cmd..."
    case "$PKG_MGR" in
        apt)    sudo apt-get update -qq && sudo apt-get install -y -qq "$@" ;;
        dnf)    sudo dnf install -y -q "$@" ;;
        pacman) sudo pacman -S --noconfirm --needed "$@" ;;
    esac
    ok "$cmd installed"
}

install_pkg node nodejs npm
install_pkg curl curl

# ─── build ──────────────────────────────────────────────────────────────────

exec "$ROOT_DIR/scripts/build.sh" "$@"
