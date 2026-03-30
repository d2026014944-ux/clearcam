#!/usr/bin/env bash
set -euo pipefail

cd /opt/clearcam

use_clip="${CLEARCAM_USE_CLIP:-false}"
yolo_size="${CLEARCAM_YOLO_SIZE:-t}"
yolo_res="${CLEARCAM_YOLO_RES:-640}"
userid="${CLEARCAM_USERID:-}"
key="${CLEARCAM_KEY:-}"

args=(
  "--use_clip=${use_clip}"
  "--yolo_size=${yolo_size}"
  "--yolo_res=${yolo_res}"
)

if [[ -n "${userid}" ]]; then
  args+=("--userid=${userid}")
fi
if [[ -n "${key}" ]]; then
  args+=("--key=${key}")
fi

exec /opt/clearcam/.venv/bin/python /opt/clearcam/clearcam.py "${args[@]}"
