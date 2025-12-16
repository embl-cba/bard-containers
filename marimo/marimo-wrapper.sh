#!/usr/bin/env bash
set -euo pipefail

# Always start in the user's home
cd "$HOME"

case "${1:-}" in
  edit|new)
    sub="$1"; shift || true
    if [[ $# -eq 0 || "${1:-}" == -* ]]; then
      set -- "$HOME" "$@"
    fi
    exec /usr/local/bin/marimo-real "$sub" "$@"
    ;;
  *)
    exec /usr/local/bin/marimo-real "$@"
    ;;
esac

