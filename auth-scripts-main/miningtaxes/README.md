# Miningtaxes Enhanced - Type 90665 Fix + Character Tracking

## 🔴 The Problems

### Problem 1: Price Update Crashes
Miningtaxes price updates crash with:
```
HTTPNotFound: 404 Not Found - Type not found
```

**Why?** Type 90665 is a CCP test item that doesn't exist in ESI but may be in your database.

### Problem 2: Lost Tax Donations
Tax donations from unregistered alts or characters not in AllianceAuth are lost and never credited.

**Why?** The system only matches by ESI character ID. If the character isn't registered, donations are silently ignored.

---

## ✅ The Solutions

### Fix 1: Skip Invalid Type IDs
We patched `tasks.py` to skip invalid type IDs and handle 404 errors gracefully.

### Fix 2: Character Name Fallback Matching
When character ID matching fails, the system now:
- Parses character names from the donation reason field
- Attempts to match against registered characters
- Logs unmatched donations for admin review

**Player instructions updated:** Players must now include their character name in the donation reason:
- Format: `phrase CharacterName` (e.g., "TAX JohnDoe")
- Case insensitive
- Works with partial matches if name is truncated

---

## 📥 Installation (Volume Mount - Recommended)

### Step 1: Copy the patched file

/your-auth-folder/
├── docker-compose.yml
├── miningtaxes_fix/
│   └── tasks.py    (the enhanced patched file)

### Step 2: Edit docker-compose.yml
Add this line to the `volumes:` section (around line 11):
```yaml
### Step 3: Update FAQ template (important for character tracking)
Replace the FAQ template to update player instructions:
```yaml
volumes:
  - ./conf/local.py:/home/allianceauth/myauth/myauth/settings/local.py
  - ./miningtaxes_fix/tasks.py:/home/allianceauth/.local/lib/python3.11/site-packages/miningtaxes/tasks.py
  - ./templates/miningtaxes/faq.html:/home/allianceauth/.local/lib/python3.11/site-packages/miningtaxes/templates/miningtaxes/faq.html
```

Copy the updated FAQ template:
```bash
cp aa-miningtaxes-master/miningtaxes/templates/miningtaxes/faq.html templates/miningtaxes/
```

### Step 4: Configure Settings in conf/local.py
**IMPORTANT**: Keep the phrase short (3-5 characters) to leave room for character names:
```python
# Miningtaxes Settings
MININGTAXES_PHRASE = "TAX"  # Short phrase leaves room for character name
```

### Step 5: Restart
```bash
docker compose restart
```

✅ **Done!** The fixes persist across restarts and rebuilds.

---

## 🔍 Verify It Works

### Check Price Updates
```bash
docker logs allianceauth_worker_beat | grep miningtaxes
```

### Confirm Patch Loaded
```bash
docker exec allianceauth_gunicorn grep "INVALID_TYPE_IDS" /home/allianceauth/.local/lib/python3.11/site-packages/miningtaxes/tasks.py
docker exec allianceauth_gunicorn grep "_match_character_by_name" /home/allianceauth/.local/lib/python3.11/site-packages/miningtaxes/tasks.py
```

### Monitor Unmatched Donations
```bash
docker logs allianceauth_worker_beat | grep "Unmatched:"
```

---

## 👥 Player Instructions

Players should now format donations as: **`phrase CharacterName`**

**Examples:**
- `TAX JohnDoe`
- `JohnDoe TAX`
- `tax john doe` (case insensitive)

**Important Notes:**
- Total length limited to 32 characters (reason field limit)
- Use short phrases (TAX, MOON) to maximize space for character names
- Character name is required for proper tracking
- System will try partial matching if name is truncated

---

## 📊 What Happens When

### Successful Match (No Logs)
- Character ID found in AllianceAuth → **credited automatically**
- Character name parsed and matched → **credited with info log**

### Failed Match (Logged)
- Character not in system AND name not in reason → **logged as "Unmatched"**
- Name too short (< 3 chars) → **logged as "Unmatched"**
- Multiple characters with same name → **logged as "Unmatched"**

Admins should review unmatched donations periodically and manually credit if needed.

---

## ⚙️ Configuration Tips

### Recommended Phrase Settings
```python
# Good - Short and clear
MININGTAXES_PHRASE = "TAX"        # Leaves 28 chars for character name
MININGTAXES_PHRASE = "MOON"       # Leaves 27 chars for character name

# Avoid - Too long
MININGTAXES_PHRASE = "MININGTAX"  # Only 22 chars left for name
```

### Empty Phrase (Process All Donations)
```python
MININGTAXES_PHRASE = ""  # No filtering, all player_donations processed
```

With empty phrase, players just enter their character name in the reason field.

You should see: `INVALID_TYPE_IDS = {90665}`

---

## 📋 What Changed?
The patch adds error handling to skip invalid type IDs:

1. **Added import:** `from bravado.exception import HTTPNotFound`
2. **Created blacklist:** `INVALID_TYPE_IDS = {90665}`
3. **Added try-except blocks** to catch 404 errors and log warnings instead of crashing

---

## ℹ️ Notes
- This fix is for type **90665** ("QA Badly Authored Prismaticite")
- Other invalid IDs can be added to the blacklist if needed
- The fix is based on miningtaxes version **1.4.34**
2. Copy to: `/home/allianceauth/.local/lib/python3.11/site-packages/miningtaxes/tasks.py` in all containers
