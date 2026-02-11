# AllianceAuth Docker Customizations

Custom fixes and enhancements for AllianceAuth Docker deployments.

## 📦 What's Included

### 1. Discord Recruit Me Cog
Enables the `/recruit_me` command with:
- ✅ Multiple recruiter role support
- ✅ Custom welcome messages
- ✅ Private thread recruitment system

[📖 Documentation](recruit_me/README.md)

### 2. Miningtaxes Type 90665 Fix
Fixes price update crashes caused by invalid ESI type IDs:
- ✅ Handles 404 errors gracefully
- ✅ Blacklists problematic type IDs
- ✅ Prevents complete update failures

[📖 Documentation](miningtaxes/README.md)

### 3. Discord Service 404 Error Fix
Handles "Unknown Member" errors during nickname sync:
- ✅ Catches 404 errors gracefully
- ✅ Logs as warnings instead of errors
- ✅ Provides actionable user information
- ✅ Prevents sync task failures

[📖 Documentation](discord_fix/README.md)

### 4. Celeryanalytics Asset Manifest Fix
Fixes missing React app manifest in PyPI package:
- ✅ Provides correct asset-manifest.json
aa-customizations/
│
├── recruit_me/
│   ├── recruit_me.py               # Custom Discord cog
│   └── README.md                   # Setup documentation

### 5. Indyhub Discord DM Fix
Added in settings to set DMs for selected roles:
- ✅ Provides injected script and local.py settings
aa-customizations/
│
├── indyhubdiscordupdate/
│   ├── manage_discord_notification_roles.py      # Custom Discord role notification settings
│   └── README.md                   # Setup documentation

## 📁 Repository Structure

```
aa-customizations/
│
├── recruit_me/
│   ├── recruit_me.py               # Custom Discord cog
│   └── README.md                   # Setup documentation
│
├── miningtaxes/
│   ├── tasks.py                    # Patched tasks file
│   └── README.md                   # Fix documentation
│
├── discord_fix/
│   ├── tasks.py                    # Patched Discord service
│   └── README.md                   # Fix documentation
│
├── celeryanalytics_fix/
│   ├── asset-manifest.json         # React app manifest
│   └── README.md                   # Fix documentation
│
├── indyhubdiscordupdate/
│   ├── manage_discord_notification_roles.py         # React app manifest
│   └── README.md                   # Fix documentation
│
├── docker-compose.snippet.yml      # Example volume mounts
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

---

## 🚀 Quick Start

### Prerequisites
- AllianceAuth running in Docker
- Docker Compose (v2 syntax)

### Installation

**1. Clone or download this repository**

**2. Copy customization files to your AllianceAuth directory:**
```bash
# From this repository root
cp -r recruit_me /path/to/allianceauth/recruit_me_custom
cp -r miningtaxes /path/to/allianceauth/miningtaxes_fix
cp -r discord_fix /path/to/allianceauth/discord_fix
cp -r celeryanalytics_fix /path/to/allianceauth/celeryanalytics_fix
```

**3. Add volume mounts to docker-compose.yml:**

Find the `volumes:` section in your `x-allianceauth-base` and add:
```yaml
volumes:
  - ./recruit_me_custom/recruit_me.py:/home/allianceauth/.local/lib/python3.11/site-packages/aadiscordbot/cogs/recruit_me.py
  - ./miningtaxes_fix/tasks.py:/home/allianceauth/.local/lib/python3.11/site-packages/miningtaxes/tasks.py
  - ./discord_fix/tasks.py:/home/allianceauth/.local/lib/python3.11/site-packages/allianceauth/services/modules/discord/tasks.py
  - ./celeryanalytics_fix/asset-manifest.json:/var/www/myauth/static/celeryanalytics/asset-manifest.json
```

**4. Configure settings in conf/local.py:**

For Recruit Me:
```python
RECRUIT_CHANNEL_ID = YOUR_CHANNEL_ID_HERE
RECRUITER_GROUP_ID = YOUR_ROLE_ID_HERE  # or [ROLE1, ROLE2] for multiple
RECRUIT_WELCOME_MESSAGE = "Your custom message here"  # Optional
```

**5. Restart containers:**
```bash
docker compose up -d
```
---
```

---

## 🔧 Configuration Examples

### Single Recruiter Role (Default Message)
```python
RECRUIT_CHANNEL_ID = 1234567890
RECRUITER_GROUP_ID = 9876543210
```

### Multiple Recruiter Roles (Custom Message)
```python
RECRUIT_CHANNEL_ID = 1234567890
RECRUITER_GROUP_ID = [9876543210, 1111111111, 2222222222]
RECRUIT_WELCOME_MESSAGE = """Welcome to our corporation!

A recruiter will be with you shortly. Please provide:
• Your timezone
• EVE experience
• What interests you about our corp"""
```

---

## 🛠️ Troubleshooting

### Mount Error: "not a directory: Are you trying to mount a directory onto a file"
This happens when Docker created a directory instead of expecting a file. **Fix:**

```bash
# 1. Stop containers
docker compose down

# 2. Remove the problematic directory inside the container
docker compose run --rm allianceauth_gunicorn rm -rf /home/allianceauth/.local/lib/python3.11/site-packages/aadiscordbot/cogs/recruit_me.py
docker compose run --rm allianceauth_gunicorn rm -rf /home/allianceauth/.local/lib/python3.11/site-packages/miningtaxes/tasks.py

# 3. Verify source files exist on host
ls -l recruit_me_custom/recruit_me.py
ls -l miningtaxes_fix/tasks.py

# 4. Start containers
docker compose up -d
```

### Recruit Me Not Showing
1. Verify volume mount in docker-compose.yml
2. Check `RECRUIT_CHANNEL_ID` is an integer (not list)
3. Restart Discord bot: `docker compose restart allianceauth_discordbot`
4. Wait 30 seconds and refresh Discord

### Miningtaxes Updates Failing
1. Verify volume mount in docker-compose.yml
2. Check logs: `docker logs allianceauth_worker_beat | grep miningtaxes`
3. Verify patch loaded: `docker exec allianceauth_gunicorn grep "INVALID_TYPE_IDS" /home/allianceauth/.local/lib/python3.11/site-packages/miningtaxes/tasks.py`

### Discord 404 Errors Still Showing as ERROR
1. Verify volume mount in docker-compose.yml
2. Restart containers: `docker compose restart allianceauth_worker allianceauth_beat allianceauth_gunicorn`
3. Verify patch loaded: `docker exec allianceauth_gunicorn grep "safe_update_nickname" /home/allianceauth/.local/lib/python3.11/site-packages/allianceauth/services/modules/discord/tasks.py`
4. Check for stale Discord links in admin panel: Services → Discord Users

### Celeryanalytics Dashboard Not Loading
1. Verify volume mount in docker-compose.yml
2. Check manifest exists: `docker exec allianceauth_gunicorn cat /var/www/myauth/static/celeryanalytics/asset-manifest.json`
3. Restart containers: `docker compose restart allianceauth_gunicorn nginx`
4. Clear browser cache (Ctrl+Shift+R)

---

## 📝 Notes

- **Persistence:** Volume mounts persist across container restarts and rebuilds
- **Updates:** To update, edit the files and restart containers
- **Python Version:** Paths assume Python 3.11 - adjust if using different version
- **Compatibility:** Tested with AllianceAuth 4.11.2

---


# MiningTaxes Discord Integration

**What it does:** Makes MiningTaxes send Discord messages to your players!

## 📁 What You Get

One file called `discord_integration.py` that can:
- 💬 Send private messages to players
- 📢 Post announcements in channels  
- 📊 Show who owes taxes in a nice table

## ⚙️ What You Need First

**Step 1:** Install aa-discordbot
```bash
pip install aa-discordbot
```

**Step 2:** Make sure your Alliance Auth has Discord turned on

That's it! 

## 🚀 How to Use It

### Super Simple Way

1. **Download the file**
   - Grab `discord_integration.py` from this folder

2. **Put it in your MiningTaxes folder**
   - Drop it where your other MiningTaxes files are

3. **Tell MiningTaxes to use it**
   - Add this to the top of your tasks.py file:
   ```python
   from .discord_integration import send_discord_dm, get_user_discord_id
   ```

4. **Done!** Now you can send Discord messages!

## 🎯 Functions

### 1. `send_discord_notification(webhook_url, title, message, color, username)`
Sends public notifications to Discord channels via webhook.
What Each Thing Does

### 1. Send Channel Messages
`send_discord_notification()` - Posts to a Discord channel everyone can see

**Example:** "Taxes are due on the 15th!"

### 2. Send Private Messages  
`send_discord_dm()` - Sends a secret message to one person

**Example:** "Hey John, you owe 500,000 ISK"

### 3. Find Someone's Discord
`get_user_discord_id()` - Looks up a player's Discord username

**Example:** Finds that "john_doe" is Discord user #12345

### 4. Make a Tax Report
`send_corp_tax_summary()` - Creates a pretty table showing who owes what

**Example:** Shows top 25 people who owe taxes with a leaderboard
```python
from discord_integration import send_discord_dm, get_user_discord_id
from django.contrib.auth.models import User

user = User.objects.get(username='john_doe')
discord_id = get_user_discord_id(user)
Copy & Paste Examples

### Example 1: Send Someone a Private Message
```python
# Get their Discord ID
discord_id = get_user_discord_id(user)

# Send them a message
send_discord_dm(
    discord_id,
    "Taxes Due!",
    "Please pay 1,234,567 ISK",
    color=0xf39c12  # Makes it orange
)
```

### Example 2: Post a Tax Report  
```python
# Make a list of who owes what
tax_data = [
    {
        'username': 'john_doe',
        'main_character': 'John Doe',
        'balance': 125.5  # in millions
    }
]

# Send it to Discord
send_corp_tax_summary(None, tax_data, channel_id=YOUR_CHANNEL_ID)
```

### Example 3: Full Setup in MiningTaxes
```python
# In your tasks.py file, add this:

@shared_task
def notify_taxes_due():
    # Load the Discord tools
    from .discord_integration import send_discord_dm, get_user_discord_id
    
    # For each person who owes taxes...
    for user in users_who_owe_money:
        discord_id = get_user_discord_id(user)
        
        if discord_id:
            send_discord_dm(
                discord_id,
                "Taxes Due!",
                f"You owe {amount} ISK",
                color=0xf39c12
            
# In models/settings.py
class Settings(models.Model):
    discord_webhook_url = models.CharField(
        max_length=500,
        default="",
        blank=True,
        help_text="Discord webhook URL for notifications"
    )
    
    discord_send_individual_dms = models.BooleanField(
        default=False,
        help_text="Send private DMs to users"
    )
    
    discord_corp_webhook_url = models.CharField(
        max_length=500,
        default="",
        blank=True,
        help_text="Webhook for corp summaries"
    )
    
    discord_corp_channel_id = models.BigIntegerField(
        default=0,
        null=True,
        blank=True,
   🔧 Settings You Need to Add

If you want buttons in your admin panel, add these to your Settings model:

```python
discord_send_individual_dms = True/False  # Turn DMs on or off
discord_corp_channel_id = 123456789       # Your Discord channel number
discord_send_corp_summary = True/False    # Turn reports on or off
```

## ✅ How to Test If It's Working

### Test 1: Is aa-discordbot installed?
```python
try:
    from aadiscordbot.tasks import send_message
    print("✅ Yes it's installed!")
except:
    print("❌ Nope, you need to install it")
```

### Test 2: Can you find Discord users?
```python
from discord_integration import get_user_discord_id

discord_id = get_user_discord_id(some_user)

if discord_id:
    print(f"✅ Found them! Their ID is {discord_id}")
else:
    print("❌ They haven't linked their Discord yet")
```

## ❓ Common Questions

**Q: Do players need to do anything?**  
A: Yes! They need to link their Discord account in Alliance Auth first.

**Q: What if someone doesn't have Discord linked?**  
A: The code skips them automatically - no error!

**Q: Can I change the message colors?**  
A: Yes! Use these color codes:
- `0xe74c3c` = Red
- `0xf39c12` = Orange  
- `0x2ecc71` = Green
- `0x3498db` = Blue

**Q: Where do I get a channel ID?**  
A: In Discord, right-click a channel → Copy ID (you need Developer Mode on)

## 📝 That's It!

Copy the file, drop it in, use the examples above. Done! 🎉

---
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



---

## 🤝 Contributing

Found a bug or have an improvement? Feel free to:
- Open an issue
- Submit a pull request
- Share your experience

---

## 📄 License

These customizations are provided as-is for the AllianceAuth community.

---

## 🔗 Related Links

- [AllianceAuth Documentation](https://allianceauth.readthedocs.io/)
- [AllianceAuth Discord](https://discord.gg/fjnHAmk)
- [aadiscordbot GitHub](https://github.com/pvyParts/allianceauth-discordbot)
- [miningtaxes GitHub](https://gitlab.com/arctiru/aa-miningtaxes)














