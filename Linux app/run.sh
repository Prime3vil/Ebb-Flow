#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN="$DIR/dist/Ebb&Flow-linux-x64/Ebb&Flow"
if [ ! -f "$BIN" ]; then
    echo "Binary not found at $BIN"
    exit 1
fi
exec "$BIN" "$@"
