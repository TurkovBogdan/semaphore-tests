#!/usr/bin/env bash
#
# Start the Semaphore server and open the browser. Stops on Ctrl+C.
#
# Usage:
#   ./scripts/serve.sh                  # start with existing DB (or create fresh)
#   ./scripts/serve.sh --seed empty_project  # clean DB + apply seed
#
# Examples:
#   ./scripts/serve.sh                       # just start
#   ./scripts/serve.sh --seed empty_project  # start with empty project seeded

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

info()  { printf '\033[1;34m→ %s\033[0m\n' "$*"; }
ok()    { printf '\033[1;32m✓ %s\033[0m\n' "$*"; }
fail()  { printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

# ─── parse args ───────────────────────────────────────────────────────────────

SEED=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --seed) SEED="$2"; shift 2 ;;
        *) fail "Unknown argument: $1" ;;
    esac
done

# ─── load env ─────────────────────────────────────────────────────────────────

if [[ -f "$ROOT_DIR/.env" ]]; then
    set -a; source "$ROOT_DIR/.env"; set +a
fi

PORT="${SEMAPHORE_TEST_PORT:-3100}"
BIN="$ROOT_DIR/vendor/semaphore"
CONFIG="$ROOT_DIR/.testdata/config.json"

[[ -x "$BIN" ]] || fail "Semaphore binary not found. Run ./scripts/build.sh first."

# ─── stop existing server ─────────────────────────────────────────────────────

EXISTING_PID=$(lsof -ti :"$PORT" 2>/dev/null || true)
if [[ -n "$EXISTING_PID" ]]; then
    info "Stopping existing server (PID $EXISTING_PID) on port $PORT..."
    kill "$EXISTING_PID" 2>/dev/null || true
    for i in {1..10}; do
        lsof -ti :"$PORT" >/dev/null 2>&1 || break
        sleep 0.5
    done
    if lsof -ti :"$PORT" >/dev/null 2>&1; then
        fail "Port $PORT is still in use (cannot kill PID $EXISTING_PID). Stop it manually."
    fi
    ok "Stopped"
fi

# ─── ensure config & DB ──────────────────────────────────────────────────────

if [[ -n "$SEED" ]]; then
    info "Resetting database and applying seed: $SEED"
    (cd "$ROOT_DIR" && uv run python -c "
from src.config import write_config
from src.database import reset_database
config = write_config()
reset_database(config)
")
    ok "Database reset"
elif [[ ! -f "$CONFIG" ]]; then
    info "Initializing database..."
    (cd "$ROOT_DIR" && uv run python -c "
from src.config import write_config
from src.database import reset_database
config = write_config()
reset_database(config)
")
    ok "Database ready"
fi

# ─── start server ────────────────────────────────────────────────────────────

URL="http://localhost:$PORT"
info "Starting Semaphore at $URL"

cleanup() { kill "$PID" 2>/dev/null; wait "$PID" 2>/dev/null || true; echo; ok "Server stopped"; }
trap cleanup EXIT INT TERM

"$BIN" server --config "$CONFIG" &
PID=$!

for i in {1..20}; do
    if ! kill -0 "$PID" 2>/dev/null; then
        fail "Server process exited unexpectedly"
    fi
    if curl -sf "$URL/api/ping" >/dev/null 2>&1; then
        break
    fi
    sleep 0.5
done

if ! curl -sf "$URL/api/ping" >/dev/null 2>&1; then
    fail "Server did not start within 10s"
fi

ok "Server is running at $URL"

# ─── apply seed ──────────────────────────────────────────────────────────────

if [[ -n "$SEED" ]]; then
    info "Applying seed: $SEED"
    (cd "$ROOT_DIR" && uv run python -c "
from src.seeds.$SEED import run
run('$URL')
")
    ok "Seed applied: $SEED"
fi

# ─── open browser ────────────────────────────────────────────────────────────

if command -v xdg-open &>/dev/null; then
    xdg-open "$URL" 2>/dev/null
elif command -v open &>/dev/null; then
    open "$URL"
fi

wait "$PID"
