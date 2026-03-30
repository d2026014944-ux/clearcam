#!/usr/bin/env bash
set -euo pipefail

echo "[OMEGA] Running quality gates..."

if command -v ruff >/dev/null 2>&1; then
  ruff check .
else
  echo "[OMEGA] ruff not found. Install with: pip install ruff"
  exit 1
fi

if command -v pytest >/dev/null 2>&1; then
  if [[ -d test ]]; then
    pytest -q test
  elif [[ -d tests ]]; then
    pytest -q tests
  else
    echo "[OMEGA] No test directory found"
    exit 1
  fi
else
  echo "[OMEGA] pytest not found. Install with: pip install pytest"
  exit 1
fi

bash .claude/hooks/posttool-safety.sh

echo "[OMEGA] All gates passed"
