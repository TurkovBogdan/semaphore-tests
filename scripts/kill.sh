#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BIN="$PROJECT_ROOT/vendor/semaphore"

pids=$(pgrep -f "$BIN" 2>/dev/null || true)

if [ -z "$pids" ]; then
    echo "No Semaphore processes found."
    exit 0
fi

echo "Found Semaphore processes:"
ps -p $pids -o pid,ppid,etime,args 2>/dev/null || true
echo ""

kill $pids 2>/dev/null || true
sleep 1

still_alive=$(pgrep -f "$BIN" 2>/dev/null || true)
if [ -n "$still_alive" ]; then
    echo "Processes did not stop, sending SIGKILL..."
    kill -9 $still_alive 2>/dev/null || true
fi

echo "Done."
