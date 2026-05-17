#!/usr/bin/env bash
#
# Run the test suite.
# Usage:  ./scripts/test.sh [pytest args...]
#
# Loads .env, enables headed mode, forwards all arguments to pytest.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [[ -f "$ROOT_DIR/.env" ]]; then
    set -a; source "$ROOT_DIR/.env"; set +a
fi

cd "$ROOT_DIR"
exec uv run pytest tests/ --headed "$@"
