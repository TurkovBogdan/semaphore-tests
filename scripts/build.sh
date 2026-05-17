#!/usr/bin/env bash
#
# Build Semaphore from source: install platform deps, compile Go binary + Vue frontend, reset DB.
# Usage:  ./scripts/build.sh [--verify]

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SEMAPHORE_DIR="$ROOT_DIR/semaphore"
VENDOR_DIR="$ROOT_DIR/vendor"
TESTDATA_DIR="$ROOT_DIR/.testdata"
OS="$(uname -s)"

info()  { printf '\033[1;34m→ %s\033[0m\n' "$*"; }
ok()    { printf '\033[1;32m✓ %s\033[0m\n' "$*"; }
fail()  { printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

# ─── check source ──────────────────────────────────────────────────────────

[[ -d "$SEMAPHORE_DIR" ]] || fail "Semaphore source not found at $SEMAPHORE_DIR
  Clone it:  git clone https://github.com/semaphoreui/semaphore.git $SEMAPHORE_DIR"

# ─── load env ──────────────────────────────────────────────────────────────

if [[ -f "$ROOT_DIR/.env" ]]; then
    set -a; source "$ROOT_DIR/.env"; set +a
fi

GO_VERSION="${GO_VERSION:-1.24}"

# ─── install platform dependencies ─────────────────────────────────────────

install_deps() {
    if [[ "$OS" == "Darwin" ]]; then
        command -v brew &>/dev/null || fail "Homebrew not found. Install from https://brew.sh"
        command -v node &>/dev/null || { info "Installing node..."; brew install node; }
        command -v curl &>/dev/null || { info "Installing curl..."; brew install curl; }
    else
        if command -v apt-get &>/dev/null; then
            PKG_MGR="apt"
        elif command -v dnf &>/dev/null; then
            PKG_MGR="dnf"
        elif command -v pacman &>/dev/null; then
            PKG_MGR="pacman"
        else
            fail "No supported package manager found (apt, dnf, pacman)"
        fi

        for cmd in node curl; do
            if ! command -v "$cmd" &>/dev/null; then
                info "Installing $cmd..."
                case "$PKG_MGR" in
                    apt)    sudo apt-get update -qq && sudo apt-get install -y -qq nodejs npm curl ;;
                    dnf)    sudo dnf install -y -q nodejs npm curl ;;
                    pacman) sudo pacman -S --noconfirm --needed nodejs npm curl ;;
                esac
                break
            fi
        done
    fi
    ok "Platform dependencies ready"
}

install_deps

# ─── install Go ────────────────────────────────────────────────────────────

GO_DIR="$VENDOR_DIR/go"
GO_BIN="$GO_DIR/bin/go"

if [[ -x "$GO_BIN" ]] && "$GO_BIN" version 2>/dev/null | grep -q "go${GO_VERSION}"; then
    ok "Go $GO_VERSION already installed"
else
    info "Downloading Go $GO_VERSION..."
    OS_LOWER=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    case "$ARCH" in
        x86_64)  ARCH="amd64" ;;
        aarch64|arm64) ARCH="arm64" ;;
    esac
    GO_URL="https://go.dev/dl/go${GO_VERSION}.0.${OS_LOWER}-${ARCH}.tar.gz"
    mkdir -p "$VENDOR_DIR"
    curl -sSL "$GO_URL" | tar -xz -C "$VENDOR_DIR"
    ok "Go $GO_VERSION installed"
fi

export PATH="$GO_DIR/bin:$PATH"
export GOPATH="$VENDOR_DIR/gopath"

# ─── build frontend ────────────────────────────────────────────────────────

info "Building Vue frontend..."
(cd "$SEMAPHORE_DIR/web" && npm ci --silent && npm run build --silent)
ok "Frontend built"

# ─── build backend ─────────────────────────────────────────────────────────

info "Building Go binary..."
(cd "$SEMAPHORE_DIR" && go build -o "$VENDOR_DIR/semaphore" .)
ok "Binary at $VENDOR_DIR/semaphore"

# ─── reset database ────────────────────────────────────────────────────────

info "Resetting test database..."
mkdir -p "$TESTDATA_DIR/tmp"
rm -f "$TESTDATA_DIR/database.sqlite"

if command -v uv &>/dev/null; then
    (cd "$ROOT_DIR" && uv run python -c "
from src.config import write_config
from src.database import reset_database
config = write_config()
reset_database(config)
")
    ok "Database ready"
else
    info "uv not found, skipping DB reset (run tests to initialize)"
fi

# ─── verify ────────────────────────────────────────────────────────────────

if [[ "${1:-}" == "--verify" ]]; then
    info "Verifying server starts..."
    "$VENDOR_DIR/semaphore" server --config "$TESTDATA_DIR/config.json" &
    PID=$!
    sleep 3
    if curl -sf "http://localhost:${SEMAPHORE_TEST_PORT:-3100}/api/ping" >/dev/null; then
        ok "Server responds to /api/ping"
    else
        fail "Server did not respond"
    fi
    kill "$PID" 2>/dev/null; wait "$PID" 2>/dev/null || true
fi

ok "Build complete"
