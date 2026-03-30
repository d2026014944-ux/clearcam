#!/usr/bin/env bash
set -euo pipefail

# Basic secret scan (expand as needed)
if grep -RInE "(AKIA[0-9A-Z]{16}|BEGIN PRIVATE KEY|sk-[A-Za-z0-9]{20,})" . --exclude-dir=.git --exclude-dir=.venv --exclude=tasks/lessons.md >/dev/null 2>&1; then
  echo "[OMEGA] Potential secret detected"
  exit 1
fi

echo "[OMEGA] PostToolUse safety checks passed"
