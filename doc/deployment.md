# sprpsr Backend Deployment Guide

This document describes the deployment process for the sprpsr backend API, which is hosted at [https://api.superposr.com](https://api.superposr.com).

---

## Overview
- **Backend Framework:** Flask (served via Gunicorn)
- **Process Manager:** systemd
- **Server:** Ubuntu (root@88.222.215.41)
- **MongoDB:** Managed server instance (not local)
- **Domain:** https://api.superposr.com

---

## Deployment Steps

### 1. Prepare Your Local Build
- Ensure all code is committed and tested locally.
- Activate your virtual environment and install dependencies if needed:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

### 2. Copy Files to the Server
- Use `scp` to copy all backend files to the server:
  ```bash
  scp -r ./* root@88.222.215.41:/root/Desktop/sp_back/
  ```
- This will overwrite the existing backend code on the server.

### 3. Restart the Backend Service
- SSH into the server if needed:
  ```bash
  ssh root@88.222.215.41
  cd /root/Desktop/sp_back/
  ```
- Restart the backend service using systemd:
  ```bash
  sudo systemctl restart sp_back
  ```
- Check the status to ensure it is running:
  ```bash
  sudo systemctl status sp_back
  ```

### 4. Logs
- Logs are configured and can be viewed on the server for debugging and monitoring.
- Typical log locations:
  - Systemd journal: `journalctl -u sp_back -f`
  - Application logs: Check the log configuration in `app.py` or the systemd service file for log file paths.

---

## Gunicorn & systemd
- The backend is served using Gunicorn behind systemd for process management and automatic restarts.
- Example systemd service file (`/etc/systemd/system/sp_back.service`):
  ```ini
  [Unit]
  Description=Sprpsr Backend
  After=network.target

  [Service]
  User=root
  WorkingDirectory=/root/Desktop/sp_back
  ExecStart=/root/Desktop/sp_back/.venv/bin/gunicorn -w 4 -b 0.0.0.0:8890 app:app
  Restart=always
  StandardOutput=journal
  StandardError=journal

  [Install]
  WantedBy=multi-user.target
  ```
- After editing the service file, reload systemd:
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl restart sp_back
  ```

---

## MongoDB
- The backend connects to a managed MongoDB server (not localhost).
- The connection string is set in the `.env` file as `MONGO_URI`.
- Example:
  ```
  MONGO_URI=mongodb+srv://<username>:<password>@<cluster-url>/sprpsr_db
  ```

---

## SSL/HTTPS
- The API is served over HTTPS at `https://api.superposr.com`.
- SSL termination is handled at the server or proxy level (e.g., Nginx, Caddy, or direct Gunicorn SSL config).

---

## Notes
- Always backup the server and database before major updates.
- Ensure environment variables and credentials (e.g., `firebase-credentials.json`, `.env`) are present on the server but **never** committed to version control.
- For troubleshooting, check both systemd and application logs.

---

For further details or issues, contact the backend team or server administrator. 