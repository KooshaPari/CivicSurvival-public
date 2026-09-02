#!/bin/sh
# CivicSurvival-public on-device smoke test
set -e
PORT="${PORT:-20129}"
BIN="./dist/cli.js"
[ -f "$BIN" ] || { echo "[err] no $BIN — build first"; exit 1; }
node "$BIN" --version
node "$BIN" start --demo --port "$PORT" &
PID=$!
trap 'kill $PID 2>/dev/null || true' EXIT
sleep 1
curl -fsS "http://127.0.0.1:${PORT}/health"
echo ""
curl -fsS -X POST "http://127.0.0.1:${PORT}/audit" -H "Content-Type: application/json" -d '{"event":"test","actor":"on-device"}'
echo ""
echo "[pass] on-device demo OK"
