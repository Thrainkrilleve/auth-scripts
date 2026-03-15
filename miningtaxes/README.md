# Miningtaxes Patch - Discord Notifications + Type 90665 Fix

This is a drop-in replacement for `tasks.py` from the [aa-miningtaxes](https://github.com/pvyParts/aa-miningtaxes) plugin. It adds Discord DM notifications for tax reminders and fixes a price update crash caused by a bad CCP item type.

## ✅ What This Patch Does

### Feature: Discord DM Notifications
Tax reminder tasks now send a Discord DM to users in addition to the standard Alliance Auth notification. Requires [allianceauth-discordbot](https://github.com/pvyParts/allianceauth-discordbot) (`aadiscordbot`) to be installed. If it is not installed or not in `INSTALLED_APPS`, the patch falls back silently to Alliance Auth notifications only — nothing breaks.

| Task | Trigger | Discord Color |
|---|---|---|
| `notify_taxes_due` | Balance exceeds `MININGTAXES_PING_THRESHOLD` | 🟡 Yellow |
| `notify_second_taxes_due` | Balance exceeds `MININGTAXES_PING_THRESHOLD` (second reminder) | 🟠 Orange |
| `notify_current_taxes_threshold` | Balance exceeds `MININGTAXES_PING_CURRENT_THRESHOLD` | 🟡 Yellow |
| `apply_interest` | Interest charged on overdue balance | 🔴 Red |

### Fix: Type 90665 Price Crash
Price update tasks no longer crash when type ID `90665` ("QA Badly Authored Prismaticite") is in the database. This CCP test item has no valid ESI entry and previously caused the entire price update to fail with a 404 error. It is now silently skipped inline.

---

## 📋 Requirements

- [aa-miningtaxes](https://github.com/pvyParts/aa-miningtaxes) installed
- For Discord DMs: [allianceauth-discordbot](https://github.com/pvyParts/allianceauth-discordbot) installed and `aadiscordbot` added to `INSTALLED_APPS`
- Users must have their Discord account linked in Alliance Auth to receive DMs

---

## 📥 Installation (Docker Volume Mount)

### Step 1: Place the patched file

Put this `tasks.py` somewhere your Docker Compose can reach it, e.g.:

```
/your-auth-folder/
├── docker-compose.yml
├── miningtaxes/
│   └── tasks.py    ← this file
```

### Step 2: Add a volume mount in docker-compose.yml

```yaml
volumes:
  - ./conf/local.py:/home/allianceauth/myauth/myauth/settings/local.py
  - ./miningtaxes/tasks.py:/home/allianceauth/.local/lib/python3.11/site-packages/miningtaxes/tasks.py
```

> **Note:** Adjust the Python version path (`python3.11`) to match what's in your container. You can check with:
> ```bash
> docker exec allianceauth_gunicorn python --version
> ```

### Step 3: Restart

```bash
docker compose restart
```

The patch will persist across restarts and container rebuilds as long as the volume mount is in place.

---

## 🔍 Verify It Works

### Confirm the patch is loaded
```bash
docker exec allianceauth_gunicorn grep "discord_bot_active" /home/allianceauth/.local/lib/python3.11/site-packages/miningtaxes/tasks.py
docker exec allianceauth_gunicorn grep "90665" /home/allianceauth/.local/lib/python3.11/site-packages/miningtaxes/tasks.py
```

### Check Discord DM logs
```bash
docker logs allianceauth_worker_beat | grep "sent discord ping"
docker logs allianceauth_worker_beat | grep "Unable to ping"
```

### Check price update logs
```bash
docker logs allianceauth_worker_beat | grep miningtaxes
```

---

## ℹ️ Notes

- If a user has not linked their Discord account in Alliance Auth, the DM is skipped with a warning log — no error is raised.
- The type 90665 skip is handled inline in `update_all_prices`. No configuration is needed.
- This patch is based on aa-miningtaxes **1.4.34**. If the upstream version changes significantly, review for conflicts before applying.
