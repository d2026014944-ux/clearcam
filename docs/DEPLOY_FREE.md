# Deploy Free (Oracle Cloud Always Free)

This guide deploys ClearCAM on a zero-cost VM for autonomous development.
The default profile is tuned for small free-tier resources.

## 1) Scope and limits

- Recommended start: 1 camera at 720p.
- Default model profile: `--yolo_size=t` and `--yolo_res=640`.
- CLIP disabled by default to reduce CPU and RAM pressure.

## 2) Provision VM

- Create an Ubuntu VM in Oracle Cloud Always Free.
- Open inbound ports:
  - `22` for SSH
  - `80` for HTTP
  - `443` for HTTPS

## 3) Run bootstrap

```bash
cd /opt
git clone https://github.com/roryclear/clearcam.git
cd clearcam
bash scripts/bootstrap_oracle_free.sh
```

The script installs dependencies, creates a service user, creates a virtualenv,
installs Python dependencies, installs systemd and nginx templates, and starts services.

## 4) Configure runtime

1. Edit `/opt/clearcam/.env`.
2. Set optional premium credentials:
   - `CLEARCAM_USERID`
   - `CLEARCAM_KEY`
3. Keep conservative defaults for free tier:
   - `CLEARCAM_USE_CLIP=false`
   - `CLEARCAM_YOLO_SIZE=t`
   - `CLEARCAM_YOLO_RES=640`

## 5) Configure nginx domain

1. Edit `/etc/nginx/sites-available/clearcam` and replace `example.com`.
2. Test and reload:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 6) Optional TLS (free)

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.example
```

## 7) Operations

### Check status

```bash
sudo systemctl status clearcam --no-pager
sudo journalctl -u clearcam -n 100 --no-pager
sudo systemctl status nginx --no-pager
```

### Update and restart

```bash
cd /opt/clearcam
git pull --ff-only
.venv/bin/pip install -r requirements.txt
sudo systemctl restart clearcam
```

### Rollback

```bash
cd /opt/clearcam
git reflog
# checkout previous commit hash after inspection
git checkout <commit>
.venv/bin/pip install -r requirements.txt
sudo systemctl restart clearcam
```

## 8) Validation checklist

- Service starts after reboot.
- Web UI responds through nginx.
- Camera stream loads and events are generated.
- Disk usage remains under control on free-tier volume.

## 9) Local quality gates before release

Run from repository root:

```bash
bash .claude/hooks/precommit-gate.sh
```

This runs ruff, pytest, and secret scanning.

## 10) Validate deploy artifacts locally

Validate shell scripts:

```bash
bash -n scripts/run_clearcam.sh scripts/bootstrap_oracle_free.sh
```

Validate systemd unit syntax:

```bash
systemd-analyze verify deploy/free/clearcam.service
```

Note: `systemd-analyze verify` checks the first binary in `ExecStart` on the local machine.
The target script path is resolved on the deployed host at `/opt/clearcam/scripts/run_clearcam.sh`.

## 11) Post-deploy smoke test on VM

Run this on the target VM after bootstrap, nginx setup, and optional TLS:

```bash
bash scripts/post_deploy_check.sh https://your-domain.example
```

The script checks `https://your-domain.example/health`.

For local-only checks on the VM:

```bash
bash scripts/post_deploy_check.sh http://127.0.0.1
```
