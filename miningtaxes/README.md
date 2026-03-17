# Miningtaxes Patch - Discord Notifications, Monthly Tax Cycle & Bug Fixes

This is a drop-in replacement for `tasks.py` from the [aa-miningtaxes](https://github.com/pvyParts/aa-miningtaxes) plugin. It adds Discord DM notifications, a complete monthly tax notification cycle, a manual notification management command, and fixes several bugs in the upstream code.

Based on aa-miningtaxes **1.4.37**.

> **Note on type 90665 fix:** The upstream dev already addressed this in v1.4.33. Our patch retains the same fix but it is not something new we are contributing.

---

## ✅ What This Patch Does

### Feature: Discord DM Notifications
All tax notification tasks now send a Discord DM to users in addition to the standard Alliance Auth notification. Requires [allianceauth-discordbot](https://github.com/pvyParts/allianceauth-discordbot) (`aadiscordbot`) to be installed. If it is not installed or not in `INSTALLED_APPS`, the patch falls back silently to Alliance Auth notifications only — nothing breaks.

### Feature: Monthly Tax Notification Cycle
Three new tasks replace the original `notify_taxes_due` / `apply_interest` scheduled tasks. These use the Stats balance (lifetime taxes minus credits) rather than the ESI-derived `calctaxes()` value, so **all users with any outstanding balance are notified**, not just those with ESI data present.

| Task | Schedule | Purpose | Discord Color |
|---|---|---|---|
| `notify_taxes_due_first` | 2nd of month | First notice — pay up or interest is coming | 🟡 Yellow |
| `notify_taxes_due_second` | 15th of month | Final warning — interest applied tomorrow | 🟠 Orange |
| `apply_interest_and_notify` | 16th of month | Applies interest, notifies with new total owed | 🔴 Red |

All three tasks call `calc_admin_main_json()` before reading balances so they always operate on fresh data.

### Feature: Manual Notification Management Command
A new Django management command `miningtaxes_send_notifications` lets you trigger notifications on demand without waiting for scheduled Celery beat tasks. See [Manual Notifications](#-manual-notifications) below.

### Feature: Standalone `run_precalcs` Task
A new `run_precalcs` task recalculates all character balances and Stats unconditionally. Schedule it ~2 hours after `update_daily` as a safety net — see [Scheduling](#-scheduling) below.

### Fix: Discord DM API Call
The original `send_discord_dm` called `aadiscordbot.tasks.send_message.delay()`, treating it as a Celery task. `send_message` is actually a plain function; calling `.delay()` on it raised an `AttributeError` that was silently swallowed. Fixed to call `send_message(user=user, embed=e)` directly.

### Fix: `chord` / `precalcs` Callback Silently Not Running
In `update_daily`, Celery's `chord` only fires the `precalcs` callback if every single `update_character` subtask completes without error. Any ESI token error, rate limit, or network issue on any one character would silently prevent `precalcs` from ever running — meaning balances and Stats were never recalculated after the daily update. The new `run_precalcs` task provides a guaranteed independent recalculation.

### Fix: Interest Task Leaves Stale Admin Panel
After charging interest in `apply_interest_and_notify`, `precalc_all()` is now called immediately on the affected character so the admin panel reflects the new balance right away rather than waiting for the next scheduled recalculation.

---

## 📋 Requirements

- [aa-miningtaxes](https://github.com/pvyParts/aa-miningtaxes) installed
- For Discord DMs: [allianceauth-discordbot](https://github.com/pvyParts/allianceauth-discordbot) installed and `aadiscordbot` added to `INSTALLED_APPS`
- Users must have their Discord account linked in Alliance Auth to receive DMs

---

## 📥 Installation (Docker Volume Mount)

### Step 1: Place the patched files

Put the files somewhere your Docker Compose can reach them, e.g.:

```
/your-auth-folder/
├── docker-compose.yml
└── conf/
    └── auth-scripts/
        └── miningtaxes/
            ├── tasks.py                          ← patched tasks
            └── miningtaxes_send_notifications.py ← manual command
```

### Step 2: Add volume mounts in docker-compose.yml

```yaml
volumes:
  - ./conf/local.py:/home/allianceauth/myauth/myauth/settings/local.py
  - ./conf/auth-scripts/miningtaxes/tasks.py:/home/allianceauth/.local/lib/python3.11/site-packages/miningtaxes/tasks.py
  - ./conf/auth-scripts/miningtaxes/miningtaxes_send_notifications.py:/home/allianceauth/.local/lib/python3.11/site-packages/miningtaxes/management/commands/miningtaxes_send_notifications.py
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

## 📅 Scheduling

Add the following to `local.py`. **Do not add `miningtaxes_update_daily`** — the daily ESI update is self-registered by the plugin via Django's periodic task admin and adding it to `local.py` will cause a conflict that breaks Alliance Auth on startup.

```python
# Safety net recalc — runs even if update_daily's chord callback failed
CELERYBEAT_SCHEDULE['miningtaxes_run_precalcs'] = {
    'task': 'miningtaxes.tasks.run_precalcs',
    'schedule': crontab(minute=0, hour='3'),  # 3:00 AM UTC
}

# 2nd of month: first tax notice to all users with outstanding balance
CELERYBEAT_SCHEDULE['miningtaxes_notifications'] = {
    'task': 'miningtaxes.tasks.notify_taxes_due_first',
    'schedule': crontab(0, 0, day_of_month='2'),
}

# 15th of month: final warning before interest is applied
CELERYBEAT_SCHEDULE['miningtaxes_apply_interest'] = {
    'task': 'miningtaxes.tasks.notify_taxes_due_second',
    'schedule': crontab(0, 0, day_of_month='15'),
}

# 16th of month: apply interest and notify with new total
CELERYBEAT_SCHEDULE['miningtaxes_apply_interest_notify'] = {
    'task': 'miningtaxes.tasks.apply_interest_and_notify',
    'schedule': crontab(0, 0, day_of_month='16'),
}
```

After updating `local.py`, restart the beat container:
```bash
docker restart allianceauth_worker_beat
```

---

## � Manual Notifications

The `miningtaxes_send_notifications` management command lets you trigger tax notifications on demand without waiting for the scheduled Celery beat tasks.

```bash
# Send all notifications
docker exec allianceauth_gunicorn python manage.py miningtaxes_send_notifications

# Send only the first reminder (taxes due soon)
docker exec allianceauth_gunicorn python manage.py miningtaxes_send_notifications first

# Send only the second reminder (taxes due)
docker exec allianceauth_gunicorn python manage.py miningtaxes_send_notifications second

# Send current balance threshold notification
docker exec allianceauth_gunicorn python manage.py miningtaxes_send_notifications current

# Apply interest and notify overdue users
docker exec allianceauth_gunicorn python manage.py miningtaxes_send_notifications interest
```

---

## �🔍 Verify It Works

### Confirm the patch is loaded
```bash
docker exec allianceauth_gunicorn grep "discord_bot_active" /home/allianceauth/.local/lib/python3.11/site-packages/miningtaxes/tasks.py
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

---

## ℹ️ Notes

- If a user has not linked their Discord account in Alliance Auth, the DM is skipped with a warning log — no error is raised.
- The type 90665 fix was already present in the upstream code (v1.4.33+) and is retained here. No configuration is needed.
- The new monthly cycle tasks (`notify_taxes_due_first`, `notify_taxes_due_second`, `apply_interest_and_notify`) use the Stats lifetime balance (total taxes minus all credits), not the ESI-derived `calctaxes()` value. This means users are notified based on their actual running balance in the system regardless of ESI availability.
- This patch is based on aa-miningtaxes **1.4.37**. If the upstream version changes significantly, review for conflicts before applying.

---

## 📝 Changelog

### 2026-03-16

**Bug Fixes**
- Fixed Discord DMs silently failing: `send_message` in `aadiscordbot` is a plain function, not a Celery task. Changed `send_message.delay(user_id=..., embed=e)` → `send_message(user=user, embed=e)`. The original `.delay()` call raised an `AttributeError` that was caught by the broad `except Exception` block, causing all Discord DMs to be silently dropped.
- Fixed `update_daily` / `precalcs` never recalculating balances: Celery `chord` only fires its callback if every subtask succeeds. A single ESI token error on any character would silently prevent `precalcs` from running, leaving all Stats and admin panel balances permanently stale. Added a standalone `run_precalcs` task to be scheduled independently as a guaranteed safety net.
- Fixed `apply_interest_and_notify` leaving stale admin panel data: added `precalc_all()` call on the affected character immediately after charging interest so the balance is updated right away.

**New Features**
- Added three new Stats-based monthly notification tasks that notify **all users with any outstanding balance**, not just those with ESI `calctaxes()` data:
  - `notify_taxes_due_first` — 2nd of month, yellow
  - `notify_taxes_due_second` — 15th of month, orange (final warning)
  - `apply_interest_and_notify` — 16th of month, red (applies interest, sends new total)
- Added `run_precalcs` standalone task as a reliable daily recalculation fallback.
- Added `miningtaxes_send_notifications` management command for triggering notifications manually (with `--force` flag to notify all users regardless of threshold).
