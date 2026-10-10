#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

command -v python >/dev/null 2>&1 || { echo "python is required" >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "npm is required" >&2; exit 1; }

if ! python -m pip_audit --version >/dev/null 2>&1; then
  echo "pip-audit is required for the dependency security gate." >&2
  echo "Install with: python -m pip install pip-audit" >&2
  exit 1
fi

cd "$ROOT/backend"
python -m pip_audit -r requirements.txt

cd "$ROOT/frontend"
npm audit --omit=dev
