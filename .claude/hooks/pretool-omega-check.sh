#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f "CLAUDE.md" || ! -f ".mcp.json" ]]; then
  echo "[OMEGA] Missing CLAUDE.md or .mcp.json"
  exit 1
fi

if [[ ! -f "tasks/todo.md" ]]; then
  echo "[OMEGA] Missing tasks/todo.md"
  exit 1
fi

if ! grep -qi "Problema:" tasks/todo.md || ! grep -qi "Solucao:" tasks/todo.md; then
  echo "[OMEGA] Feynman gate failed: add Problema/Solucao in tasks/todo.md"
  exit 1
fi

echo "[OMEGA] PreToolUse checks passed"
