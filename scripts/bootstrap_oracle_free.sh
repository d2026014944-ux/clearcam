#!/usr/bin/env bash
set -euo pipefail

# Bootstrap script for Oracle Cloud Always Free Ubuntu VM.
# Run as a sudo-capable user.

REPO_URL="${REPO_URL:-https://github.com/roryclear/clearcam.git}"
APP_DIR="${APP_DIR:-/opt/clearcam}"
SERVICE_USER="${SERVICE_USER:-clearcam}"

sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip ffmpeg git nginx

if ! id -u "${SERVICE_USER}" >/dev/null 2>&1; then
  sudo useradd --system --create-home --shell /usr/sbin/nologin "${SERVICE_USER}"
fi

if [[ ! -d "${APP_DIR}/.git" ]]; then
  sudo mkdir -p "${APP_DIR}"
  sudo chown -R "${SERVICE_USER}:${SERVICE_USER}" "${APP_DIR}"
  sudo -u "${SERVICE_USER}" git clone "${REPO_URL}" "${APP_DIR}"
else
  sudo -u "${SERVICE_USER}" git -C "${APP_DIR}" pull --ff-only
fi

sudo -u "${SERVICE_USER}" python3.11 -m venv "${APP_DIR}/.venv"
sudo -u "${SERVICE_USER}" "${APP_DIR}/.venv/bin/pip" install --upgrade pip
sudo -u "${SERVICE_USER}" "${APP_DIR}/.venv/bin/pip" install -r "${APP_DIR}/requirements.txt"

if [[ ! -f "${APP_DIR}/.env" ]]; then
  sudo -u "${SERVICE_USER}" cp "${APP_DIR}/.env.example" "${APP_DIR}/.env"
fi

sudo install -m 0755 "${APP_DIR}/scripts/run_clearcam.sh" /opt/clearcam/scripts/run_clearcam.sh
sudo install -m 0644 "${APP_DIR}/deploy/free/clearcam.service" /etc/systemd/system/clearcam.service
sudo systemctl daemon-reload
sudo systemctl enable clearcam
sudo systemctl restart clearcam

sudo install -m 0644 "${APP_DIR}/deploy/free/nginx-clearcam.conf" /etc/nginx/sites-available/clearcam
sudo ln -sf /etc/nginx/sites-available/clearcam /etc/nginx/sites-enabled/clearcam
sudo nginx -t
sudo systemctl reload nginx

echo "Bootstrap complete. Next steps:"
echo "1) Edit ${APP_DIR}/.env with credentials and tuning values."
echo "2) Set your domain in /etc/nginx/sites-available/clearcam and reload nginx."
echo "3) Optionally enable TLS with certbot."
