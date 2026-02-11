# How to Setup Custom /recruit_me Message

## 📋 What This Does
This guide helps you change the message that appears when someone uses the `/recruit_me` command in Discord.

---

## 📁 Files You Need

You need 3 files on your production server:

1. ✅ `recruit_me.py` (this folder - copy to production)
2. ✅ `conf/local.py` (edit this file)
3. ✅ `docker-compose.yml` (edit this file)

---

## 🔧 Step 1: Copy recruit_me.py File

**What to do:**
- Copy the file `recruit_me.py` from this folder
- Put it in the `conf/` folder on your production server
- The file should be at: `conf/recruit_me.py`

---

## 🔧 Step 2: Edit docker-compose.yml

**Where to find it:**
- File location: `docker-compose.yml` (in main folder)

**What to add:**
- Find the section that says `volumes:` (around line 11)
- Add this new line in the list:

```yaml
- ./conf/recruit_me.py:/home/allianceauth/.local/lib/python3.11/site-packages/aadiscordbot/cogs/recruit_me.py
```

**Full example of how it should look:**
```yaml
volumes:
  - ./conf/local.py:/home/allianceauth/myauth/myauth/settings/local.py
  - ./conf/celery.py:/home/allianceauth/myauth/myauth/celery.py
  - ./conf/urls.py:/home/allianceauth/myauth/myauth/urls.py
  - ./conf/recruit_me.py:/home/allianceauth/.local/lib/python3.11/site-packages/aadiscordbot/cogs/recruit_me.py
  - ./conf/memory_check.sh:/memory_check.sh
  - ./templates:/home/allianceauth/myauth/myauth/templates/
  - static-volume:/var/www/myauth/static
```

⚠️ **Important:** Make sure the spacing (indentation) is exactly the same!

---

## 🔧 Step 3: Edit conf/local.py

**Where to find it:**
- File location: `conf/local.py`

**What to add:**
- Find this line: `PRICE_CHECK_HOSTNAME = "evepraisal.com"`
- Add these lines **AFTER** that line:

**Option A: Single Recruiter Role (Default Message)**
```python
# Recruit Me Cog Configuration
RECRUIT_CHANNEL_ID = YOUR_CHANNEL_ID_HERE  # Your recruitment channel ID
RECRUITER_GROUP_ID = YOUR_ROLE_ID_HERE  # Your recruiter Discord role ID
```

**Option B: Multiple Recruiter Roles (Default Message)**
```python
# Recruit Me Cog Configuration
RECRUIT_CHANNEL_ID = YOUR_CHANNEL_ID_HERE  # Your recruitment channel ID
RECRUITER_GROUP_ID = [YOUR_ROLE_ID_1, YOUR_ROLE_ID_2]  # Multiple role IDs in brackets
```

**Option C: Custom Welcome Message (Single or Multiple Roles)**
```python
# Recruit Me Cog Configuration
RECRUIT_CHANNEL_ID = YOUR_CHANNEL_ID_HERE  # Your recruitment channel ID
RECRUITER_GROUP_ID = YOUR_ROLE_ID_HERE  # Single role OR [ROLE_1, ROLE_2] for multiple
RECRUIT_WELCOME_MESSAGE = "Welcome! A recruiter will be with you shortly."
```

⚠️ **Note:** If you don't set `RECRUIT_WELCOME_MESSAGE`, the bot will use the default message: "is hunting for a recruiter! Someone from @Role will get in touch soon!"

**How to get the correct IDs:**

1. **RECRUIT_CHANNEL_ID:** 
   - Right-click your Discord recruitment channel
   - Click "Copy Channel ID"
   - Replace `YOUR_CHANNEL_ID_HERE` with your channel ID

2. **RECRUITER_GROUP_ID:**
   - Go to Discord Server Settings → Roles
   - Right-click your recruiter role
   - Click "Copy Role ID"
   - Replace `YOUR_ROLE_ID_HERE` with your role ID
   - **For multiple roles:** Use brackets with comma-separated IDs:
     - Example: `[12345678901234567, 98765432109876543, 55555555555555555]`
   - **For single role:** Just the number (no brackets):
     - Example: `12345678901234567`

---

## 🔧 Step 4: Check DISCORD_BOT_COGS List

**Where to find it:**
- Same file: `conf/local.py`
- Look for `DISCORD_BOT_COGS = [`

**What to check:**
- Make sure this line is in the list:
```python
"aadiscordbot.cogs.recruit_me",
```

✅ If you see it, good! Do nothing.
❌ If you don't see it, add it to the list.

---

## 🚀 Step 5: Restart Discord Bot

**Commands to run:**

```bash
docker restart allianceauth_discordbot
```

**Wait 30 seconds**, then check if it worked:

```bash
docker logs allianceauth_discordbot | grep "recruit_me"
```

You should see: `[Cogs Loaded] aadiscordbot.cogs.recruit_me`

---

## ✏️ How to Change the Message Later

**Easy steps:**

1. Open file: `conf/local.py`
2. Find the line: `RECRUIT_WELCOME_MESSAGE = "..."`
3. Change the text between the quotes `"..."`
4. Save the file
5. Run: `docker restart allianceauth_discordbot`

**Example custom message:**
```python
RECRUIT_WELCOME_MESSAGE = """Welcome to My Corporation! 🎮

Thank you for your interest!
A recruiter will contact you soon.

Please tell us:
• What timezone are you in?
• How long have you played EVE?
• What do you want to do in our corp?"""
```

---

## ❓ Common Problems

### Problem: "/recruit_me command not showing"
**Solution:**
1. Wait 30 seconds after restart
2. Close Discord completely and reopen it
3. Check the logs (Step 5 above)

### Problem: "Something went wrong" error in Discord
**Solution:**
1. Check the channel ID is correct (no brackets [ ])
2. Check the role ID is correct (no brackets [ ] for single role)
3. Make sure both are just numbers, like: `1234567890`

### Problem: Custom message not showing
**Solution:**
1. Make sure you saved the file `conf/local.py`
2. Make sure you restarted the Discord bot
3. Make sure the text is between quotes `"..."`

---

## 📝 Summary Checklist

Before you finish, check all these boxes:

- [ ] File `recruit_me.py` is copied to `conf/` folder
- [ ] File `docker-compose.yml` has the new volume line
- [ ] File `conf/local.py` has RECRUIT_CHANNEL_ID setting
- [ ] File `conf/local.py` has RECRUITER_GROUP_ID setting
- [ ] Channel ID is correct (no brackets)
- [ ] Role ID is correct (single: no brackets, multiple: use brackets)
- [ ] Discord bot was restarted
- [ ] Command `/recruit_me` appears in Discord
- [ ] Command works when you test it

---

## 🎉 Done!

If all checkboxes are ✅, you are finished!

Your custom message will now show when users run `/recruit_me`.

**Need help?** Ask in your support channel with:
- The error message you see
- Which step you are on
- A screenshot if possible
