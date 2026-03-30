#!/usr/bin/env bash
set -euo pipefail

# Post-deploy smoke checks for ClearCAM host.
# Usage:
#   bash scripts/post_deploy_check.sh [URL]
# Example:
#   bash scripts/post_deploy_check.sh https://example.com

base_url="${1:-http://127.0.0.1}"

if [[ "${base_url}" == */health ]]; then
  health_url="${base_url}"
else
  health_url="${base_url%/}/health"
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "curl not found; install curl before running checks." >&2
  exit 1
fi

if command -v systemctl >/dev/null 2>&1 && [[ -d /run/systemd/system ]]; then
  echo "[check] clearcam service active"
  systemctl is-active --quiet clearcam

  echo "[check] nginx service active"
  systemctl is-active --quiet nginx
else
  echo "[warn] systemd not available/running; skipping service state checks"
fi

echo "[check] Health endpoint responds: ${health_url}"
http_code="$(curl -ksS -o /tmp/clearcam_smoke.out -w "%{http_code}" "${health_url}")"
if [[ "${http_code}" != "200" ]]; then
  echo "unexpected HTTP status: ${http_code}" >&2
  exit 1
fi

if ! grep -q '"status"[[:space:]]*:[[:space:]]*"ok"' /tmp/clearcam_smoke.out; then
  echo "health payload missing expected status=ok" >&2
  exit 1
fi

echo "[ok] smoke checks passed"
