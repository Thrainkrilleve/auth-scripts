# Indy Hub for Alliance Auth

A modern industry management module for [Alliance Auth](https://allianceauth.org/), focused on blueprint and job tracking for EVE Online alliances and corporations.

______________________________________________________________________

## ✨ Features

### Core Features

- **Blueprint Library**: View, filter, and search all your EVE Online blueprints by character, corporation, type, and efficiency.
- **Industry Job Tracking**: Monitor and filter your manufacturing, research, and invention jobs in real time.
- **Blueprint Copy Sharing**: Request, offer, and deliver blueprint copies (BPCs) with collapsible fulfillment cards, inline access list summaries, signed Discord quick-action links, and notifications for each step.
- **Flexible Sharing Scopes**: Expose blueprint libraries per character, per corporation, or to everyone at once.
- **Conditional Offer Chat**: Negotiate blueprint copy terms directly in Indy Hub with persistent history and status tracking.
- **Material Exchange**: Create buy/sell orders with order references, validate ESI contracts, and review transaction history.
- **ESI Integration**: Secure OAuth2-based sync for blueprints and jobs with director-level corporation scopes.
- **Notifications**: In-app alerts for job completions, copy offers, chat messages, and deliveries, with configurable immediate or digest cadences.
- **Discord Role-Based Notifications**: Restrict Discord notifications to specific roles (NEW!)
- **Modern UI**: Responsive Bootstrap 5 interface with theme compatibility and full i18n support.

______________________________________________________________________

## Requirements

- **Alliance Auth v4+**
- **Python 3.10+**
- **Django** (as required by AA)
- **django-eveuniverse** (populated with industry data)
- **Celery** (for background sync and notifications)
- *(Optional)* Director characters for corporate dashboards
- *(Optional)* aa-discordbot or aa-discordnotify for Discord notifications
- *(Optional)* Discord Guild (Server) ID for role-based notification filtering

______________________________________________________________________

## Installation & Setup

### 1. Install Dependencies

```bash
pip install django-eveuniverse indy_hub
```

### 2. Configure Alliance Auth Settings

Add to your `local.py`:

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    "eveuniverse",
    "indy_hub",
]

# EveUniverse configuration
EVEUNIVERSE_LOAD_TYPE_MATERIALS = True
EVEUNIVERSE_LOAD_MARKET_GROUPS = True
```

### 3. Run Migrations & Collect Static Files

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 4. Populate Industry Data

```bash
python manage.py eveuniverse_load_data types --types-enabled-sections industry_activities type_materials
```

### 5. Set Permissions

Assign permissions in Alliance Auth to control access levels:

#### Base Access (Required for all users)

- **`indy_hub.can_access_indy_hub`** → "Can access Indy Hub"
  - View and manage personal blueprints
  - Create and manage blueprint copy requests
  - Use Material Exchange (buy/sell orders)
  - View personal industry jobs
  - Configure personal settings and notifications

#### Corporation Management (Optional)

- **`indy_hub.can_manage_corp_bp_requests`** → "Can manage corporation indy"
  - View and manage corporation blueprints (director only)
  - Handle corporation blueprint copy requests
  - Access corporation industry jobs
  - Configure corporation sharing settings
  - Requires ESI director roles for the corporation

#### Material Exchange Administration (Optional)

- **`indy_hub.can_manage_material_hub`** → "Can manage Mat Exchange"
  - Configure Material Exchange settings
  - Manage stock availability
  - View all transactions
  - Admin panel access

**Note**: Permissions are independent and can be combined. Most users only need `can_access_indy_hub`.

### 6. Restart Services

```bash
# Restart Alliance Auth
systemctl restart allianceauth
```

______________________________________________________________________

## Configuration (Optional)

Customize Indy Hub behavior in `local.py`:

### Basic Settings

```python
# Manual refresh cooldown (seconds between user refreshes)
INDY_HUB_MANUAL_REFRESH_COOLDOWN_SECONDS = 3600  # Default: 1 hour

# Background sync windows (minutes)
INDY_HUB_BLUEPRINTS_BULK_WINDOW_MINUTES = 720  # Default: 12 hours
INDY_HUB_INDUSTRY_JOBS_BULK_WINDOW_MINUTES = 120  # Default: 2 hours
```

### Discord Notification Settings

```python
# Enable/disable Discord direct messages (default: True)
INDY_HUB_DISCORD_DM_ENABLED = True

# Footer text in Discord embeds (default: "Alliance Auth")
INDY_HUB_DISCORD_FOOTER_TEXT = "Your Alliance Name"

# How long Discord action links are valid in seconds (default: 72 hours)
INDY_HUB_DISCORD_ACTION_TOKEN_MAX_AGE = 72 * 60 * 60
```

### Discord Role-Based Notification Filtering (NEW!)

**Separate role configurations for Industry and Material Exchange notifications.**

```python
# Industry notifications (blueprints, jobs, copy requests)
# Only users with these roles get industry-related notifications
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1234567890123456789": {
        "name": "Industry Team",
        "enabled": True,
    },
}

# Material Exchange admin notifications (new orders to review)
# Only users with these roles get Material Exchange admin notifications
INDY_HUB_MATERIAL_EXCHANGE_NOTIFICATION_ROLES = {
    "9876543210987654321": {
        "name": "Material Exchange Managers",
        "enabled": True,
    },
}

# Multiple roles example (users with ANY role get notifications)
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1111111111111111111": {"name": "Industry Team", "enabled": True},
    "2222222222222222222": {"name": "Leadership", "enabled": True},
}

INDY_HUB_MATERIAL_EXCHANGE_NOTIFICATION_ROLES = {
    "3333333333333333333": {"name": "Mat Exchange Admins", "enabled": True},
    "4444444444444444444": {"name": "Finance Team", "enabled": True},
}

# Required for role checking to work
DISCORD_GUILD_ID = 123456789012345678  # Your Discord server ID

# Notes:
# - User-specific notifications (order status, approvals) are ALWAYS sent
# - Admin notifications (new orders to review) respect role filtering
# - If not configured or empty: ALL users receive that notification type
```

**How to get role IDs:**
1. Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
2. Right-click a role in your server → Copy ID
3. Right-click your server icon → Copy ID (for DISCORD_GUILD_ID)

**See also:** [Discord Role-Based Notifications](#discord-role-based-notifications-new) section below for management commands.

**Scheduled Tasks** (auto-created):

- `indy-hub-update-all-blueprints` → Daily at 03:00 UTC
- `indy-hub-update-all-industry-jobs` → Every 2 hours

______________________________________________________________________

## Updating

```bash
# Backup your database
python manage.py dumpdata >backup.json

# Update the package
pip install --upgrade indy_hub

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
systemctl restart allianceauth
systemctl restart allianceauth-celery
systemctl restart allianceauth-celery-beat
```

______________________________________________________________________

## Discord Role-Based Notifications (NEW!)

Restrict Discord notifications to specific roles following the [BlackhawkGT/auth-scripts](https://github.com/BlackhawkGT/auth-scripts) pattern.

### Overview

**Separate Discord notification roles for different notification types:**

- **Industry Notifications**: Blueprint jobs, copy requests, job completions → Use `INDY_HUB_DISCORD_NOTIFICATION_ROLES`
- **Material Exchange Admin Notifications**: New orders to review → Use `INDY_HUB_MATERIAL_EXCHANGE_NOTIFICATION_ROLES`
- **User-Specific Notifications**: Order status, approvals/denials → ALWAYS sent to the user (no filtering)

### How It Works

1. **Industry Managers** configure `INDY_HUB_DISCORD_NOTIFICATION_ROLES` with their Discord role
   - Only get notifications about blueprints, jobs, and copy requests
   
2. **Material Exchange Managers** configure `INDY_HUB_MATERIAL_EXCHANGE_NOTIFICATION_ROLES` with their Discord role
   - Only get notifications about new buy/sell orders to review
by notification type:
   - Industry: Jobs, blueprints, copy requests
   - Material Exchange: Admin notifications for new orders
2. When an admin notification is triggered:
   - ✅ **User has the role** → Notification is sent
   - ❌ **User lacks the role** → Notification is skipped (logged)
3. User-specific notifications (order status) are ALWAYS sent (no filtering)
4. Multiple roles use OR logic (user needs ANY configured role)
5. If not configured → ALL users with the permission
- `aa-discordbot` or `aa-discordnotify` installed
- Discord bot connected to your server
- Users have linked their Discord accounts in Alliance Auth
- `DISCORD_GUILD_ID` configured in `local.py`

### How It Works

1. You configure Discord roles in `local.py` (e.g., "Industry Team")
2. When a notification is triggered:
   - ✅ **User has the role** → Notification is sent
   - ❌ **User lacks the role** → Notification is skipped (logged)
3. Multiple roles use OR logic (user needs ANY configured role)
4. If not configured → ALL users receive notifications (default)

### Quick Setup (5 Minutes)

#### Step 1: Get Your Discord Role ID

In Discord:
1. Settings → Advanced → Turn on "Developer Mode"
2. Right-click your role (e.g., "Industry Team") → Copy ID
3. Right-click your server icon → Copy ID (for DISCORD_GUILD_ID)

#### Step 2: Add the Role (can also be done via local.py)

```bash
# Add a Discord role for notifications
python manage.py manage_discord_notification_roles add \
    --role-id 1234567890123456789 \
    --role-name "Industry Team"

# The command will generate settings for you to copy
```

#### Step 3: Update local.py

AdIndustry Notifications (blueprints, jobs, copy requests)
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1234567890123456789": {
        "name": "Industry Team",
        "enabled": True,
    },
}

# Material Exchange Admin Notifications (new orders to review)
# Separate role configuration!
INDY_HUB_MATERIAL_EXCHANGE_NOTIFICATION_ROLES = {
    "9876543210987654321": {
        "name": "Material Exchange Managersions
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1234567890123456789": {
        "name": "Industry Team",
        "enabled": True,
    },
}

# Required for role checking
DISCORD_GUILD_ID = 123456789012345678  # Your Discord server ID
```

#### Step 4: Update docker-compose.yml

**Important:** The Discord role checking utility (`discord_roles.py`) needs to be mounted into your container. 

Place the scripts in your auth-scripts directory (e.g., `./conf/auth-scripts/indyhubdiscordupdate/`).

Add these volume mounts to your `docker-compose.yml`:

```yaml
services:
  allianceauth:
    volumes:
      # ... your existing volumes ...
      
      # Indy Hub Discord Role-Based Notifications
      - ./conf/auth-scripts/indyhubdiscordupdate/discord_roles.py:/home/allianceauth/.local/lib/python3.11/site-packages/indy_hub/utils/discord_roles.py
```

**Optional:** If you want to use the management command for easier role configuration:
```yaml
      - ./conf/auth-scripts/indyhubdiscordupdate/manage_discord_notification_roles.py:/home/allianceauth/.local/lib/python3.11/site-packages/indy_hub/management/commands/manage_discord_notification_roles.py
```

**File locations:**
- Local: `./conf/auth-scripts/indyhubdiscordupdate/discord_roles.py`
- Local: `./conf/auth-scripts/indyhubdiscordupdate/manage_discord_notification_roles.py` (optional)
- Repository files: `indy_hub/utils/discord_roles.py` and `indy_hub/management/commands/manage_discord_notification_roles.py`

> **Note:** The volume mount injects the custom script into the Indy Hub package at runtime, extending the notification system with role-based filtering. This follows the same pattern as other auth-scripts (miningtaxes, discord_fix, etc.).

#### Step 5: Restart Services

```bash
# Docker
docker compose restart

# Systemd
systemctl restart allianceauth-worker allianceauth-beat allianceauth-gunicorn
```

### Management Commands

```bash
# List configured roles
python manage.py manage_discord_notification_roles list

# Add a new role
python manage.py manage_discord_notification_roles add \
    --role-id 1234567890123456789 \
    --role-name "Industry Team"

# Remove a role
python manage.py manage_discord_notification_roles remove \
    --role-id 1234567890123456789

# Clear all roles (notify everyone again)
python manage.py manage_discord_notification_roles clear
```

### Testing Your Setup

```bash
**For each notification type**, users with **ANY** of the configured roles will receive notifications:

```python
# Industry Team gets industry notifications
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1111111111111111111": {"name": "Industry Team", "enabled": True},
    "2222222222222222222": {"name": "Leadership", "enabled": True},
    "3333333333333333333": {"name": "Manufacturers", "enabled": True},
}

# Material Exchange Team gets Material Exchange admin notifications
INDY_HUB_MATERIAL_EXCHANGE_NOTIFICATION_ROLES = {
    "4444444444444444444": {"name": "Mat Exchange Admins", "enabled": True},
    "5555555555555555555": {"name": "Finance Team", "enabled": True},
}

# A user can have roles in both groups and receive both notification types!
```

### Notification Type Examples

| Notification | Type | Filtered By |
|--------------|------|-------------|
| Job completed | Industry | `INDY_HUB_DISCORD_NOTIFICATION_ROLES` |
| Blueprint copy request | Industry | `INDY_HUB_DISCORD_NOTIFICATION_ROLES` |
| New buy order to review | Material Exchange Admin | `INDY_HUB_MATERIAL_EXCHANGE_NOTIFICATION_ROLES` |
| Your order was approved | User-specific | **Never filtered** |
| Your order was rejected | User-specific | **Never filtered** |

### Multiple Roles (OR Logic)

Users with **ANY** of the configured roles will receive notifications:

```python
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1111111111111111111": {"name": "Industry Team", "enabled": True},
    "2222222222222222222": {"name": "Leadership", "enabled": True},
    "3333333333333333333": {"name": "Manufacturers", "enabled": True},
}
```

### Disabling Role Filtering

To notify **everyone** with the permission again:

```python
# Option 1: Remove or comment out the settings
# INDY_HUB_DISCORD_NOTIFICATION_ROLES = {}
# INDY_HUB_MATERIAL_EXCHANGE_NOTIFICATION_ROLES = {}

# Option 2: Empty dicts
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {}
INDY_HUB_MATERIAL_EXCHANGE_NOTIFICATION_ROLES = {}

# You can disable one and keep the other!
# This disables industry filtering but keeps Material Exchange filtering:
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {}  # All users with permission get industry notifications
INDY_HUB_MATERIAL_EXCHANGE_NOTIFICATION_ROLES = {
    "9876543210987654321": {"name": "Mat Exchange Managers", "enabled": True},
}  # Only this role gets Material Exchange admin notifications
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Users with role not getting notified | Check `DISCORD_GUILD_ID` is set correctly |
| All users still getting notified | Ensure roles are configured and services restarted |
| Role ID not working | Must be exact 18-19 digit number (no brackets, no quotes in Discord) |
| Discord bot errors | Ensure bot is running and connected to guild |
| User not receiving notifications | User must have Discord linked in Alliance Auth |

**Enable debug logging** in `local.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {
        'indy_hub.utils.discord_roles': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

### 📚 Complete Documentation

- **[Quick Start Guide](DISCORD_ROLES_QUICKSTART.md)** - 5-minute setup
- **[Full Documentation](DISCORD_ROLES_SETUP.md)** - Complete guide with advanced configuration
- **[Feature README](DISCORD_ROLES_README.md)** - Overview and FAQ
- **[Example Settings](discord_notification_roles_settings.py.example)** - Copy-paste configurations
- **[Implementation Details](IMPLEMENTATION_SUMMARY.md)** - Technical documentation

______________________________________________________________________

## Usage

1. **Navigate** to Indy Hub in the Alliance Auth dashboard
1. **Authorize ESI** for blueprints and jobs via the settings
1. **View Your Data**:

- Personal blueprints and industry jobs
- Corporation blueprints (if director)
- Pending blueprint copy requests
- Material Exchange buy/sell orders and transaction history

1. **Share Blueprints**: Set sharing scopes and send copy offers to alliance members
1. **Receive Notifications**: View job completions and copy request updates in the notification feed

______________________________________________________________________

## Support & Contributing

- Open an issue or pull request on GitHub for help or to contribute

______________________________________________________________________
