# Discord Service 404 Error Fix

## Problem

The Discord service throws ERROR logs when trying to sync nicknames for users who have:
- Left the Discord server
- Deleted their Discord account
- Have invalid Discord IDs

Error example:
```
ERROR [_api_request:678] [Discord Service] Discord API returned error code 404 for member ID 372383715483189250 
with this response: {"message": "Unknown Member", "code": 10007}
```

## Solution

This patch adds proper error handling to the Discord service's nickname sync tasks:

1. **Catches 404 errors gracefully** - When a member is not found, it logs a WARNING instead of ERROR
2. **Provides helpful context** - Logs explain why the error occurred and suggest cleanup
3. **Continues processing** - Doesn't stop the entire sync if one user fails
4. **Handles other errors** - Also catches 403 (permissions) and other HTTP errors

## What Changed

The patch modifies the Discord service's `tasks.py` file to:
- Wrap nickname update calls with try/except for HTTPError
- Check specifically for 404 status codes (Unknown Member)
- Log 404s as warnings with helpful context
- Log other errors appropriately
- Return success counts and error summaries

## Installation

### 1. Add volume mount to docker-compose.yml

Add this line to the `allianceauth-base` volumes section:

```yaml
- ./discord_fix/tasks.py:/home/allianceauth/.local/lib/python3.11/site-packages/allianceauth/services/modules/discord/tasks.py
```

### 2. Restart Alliance Auth containers

```bash
docker-compose restart allianceauth_worker allianceauth_beat allianceauth_gunicorn
```

## What You'll See After the Patch

**Before (ERROR):**
```
ERROR [_api_request:678] [Discord Service] Discord API returned error code 404 for member ID 372383715483189250
```

**After (WARNING with context):**
```
WARNING [Discord Service] Member not found in Discord server: User JohnDoe (Discord ID: 372383715483189250). 
Error: Unknown Member (Code: 10007). This user may have left the server or deleted their account. 
Consider removing their Discord service link from Alliance Auth.
```

## Cleaning Up Stale Discord Links

To find users with stale Discord links:

1. **Via Django shell:**
```bash
docker compose exec allianceauth_gunicorn python manage.py shell
```

```python
from allianceauth.services.modules.discord.models import DiscordUser
# Find the user by Discord ID
discord_user = DiscordUser.objects.filter(uid='372383715483189250').first()
if discord_user:
    print(f"User: {discord_user.user.username}")
    # Optionally delete the Discord link
    # discord_user.delete()
```

2. **Via Admin Panel:**
- Go to Alliance Auth admin panel
- Navigate to Services > Discord Users
- Search for the Discord ID
- Delete or update the entry

## Files Modified

- `discord_fix/tasks.py` - Patched version of Discord service tasks with error handling
- `docker-compose.yml` - Added volume mount (needs to be done manually)

## Benefits

- ✅ Reduces error log spam
- ✅ Provides actionable information about missing users
- ✅ Prevents sync task from failing completely
- ✅ Helps identify users who need Discord links removed
- ✅ Distinguishes between critical and non-critical errors

## Notes

- The patch doesn't automatically remove stale Discord links (intentional - requires manual review)
- Users who left and rejoin Discord will work normally once they re-link their account
- The bot still requires proper permissions to update nicknames
- This fix is specific to the `discord.update_all_usernames` task

## Reverting

To remove the patch:

1. Remove the volume mount from `docker-compose.yml`
2. Restart the containers
3. The original behavior will be restored
