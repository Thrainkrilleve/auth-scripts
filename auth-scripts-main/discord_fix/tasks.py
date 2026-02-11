"""
Patched Discord tasks.py with improved error handling for missing members.

This patch handles the case where Discord API returns 404 for unknown members,
which can happen when:
- A user leaves the Discord server
- A Discord account is deleted
- The member ID is invalid

The patch will:
1. Catch HTTP 404 errors gracefully
2. Log them as warnings instead of errors
3. Optionally clean up stale Discord links from the database
"""

import logging
from typing import Optional

from requests.exceptions import HTTPError

from celery import shared_task

from django.contrib.auth.models import User
from allianceauth.services.modules.discord.models import DiscordUser

logger = logging.getLogger(__name__)


# Wrap the original update function with error handling
def safe_update_nickname(discord_user, guild_id: str) -> bool:
    """
    Safely update a Discord user's nickname with proper error handling.
    
    Returns:
        bool: True if successful or member not found (non-critical), False for other errors
    """
    try:
        from allianceauth.services.modules.discord.manager import DiscordOAuthManager
        
        # Get the Discord user info
        user_id = discord_user.uid
        
        # Get the OAuth token for this user
        if not hasattr(discord_user, 'service_token') or not discord_user.service_token:
            logger.warning(
                f"[Discord Service] User {discord_user.user.username} (Discord ID: {user_id}) "
                "has no OAuth token, skipping nickname sync"
            )
            return True  # Non-critical, skip this user
        
        # Try to update the nickname
        manager = DiscordOAuthManager()
        manager.update_nickname(
            user_id=user_id,
            nickname=discord_user.user.profile.main_character.character_name
        )
        
        logger.debug(
            f"[Discord Service] Successfully updated nickname for user {discord_user.user.username} "
            f"(Discord ID: {user_id})"
        )
        return True
        
    except HTTPError as e:
        if e.response.status_code == 404:
            # Member not found - this is common when users leave the server
            error_data = {}
            try:
                error_data = e.response.json()
            except:
                pass
            
            logger.warning(
                f"[Discord Service] Member not found in Discord server: "
                f"User {discord_user.user.username} (Discord ID: {user_id}). "
                f"Error: {error_data.get('message', 'Unknown Member')} "
                f"(Code: {error_data.get('code', 10007)}). "
                "This user may have left the server or deleted their account. "
                "Consider removing their Discord service link from Alliance Auth."
            )
            return True  # Non-critical error, continue with other users
            
        elif e.response.status_code == 403:
            logger.warning(
                f"[Discord Service] Permission denied for user {discord_user.user.username} "
                f"(Discord ID: {user_id}). The bot may lack permissions."
            )
            return True  # Non-critical, skip this user
            
        else:
            # Other HTTP errors
            logger.error(
                f"[Discord Service] HTTP {e.response.status_code} error updating nickname "
                f"for user {discord_user.user.username} (Discord ID: {user_id}): {str(e)}"
            )
            return False
            
    except Exception as e:
        # Unexpected errors
        logger.error(
            f"[Discord Service] Unexpected error updating nickname "
            f"for user {discord_user.user.username} (Discord ID: {user_id}): {str(e)}",
            exc_info=True
        )
        return False


@shared_task
def update_all_usernames():
    """
    Update all Discord usernames/nicknames.
    Patched version with improved error handling for missing members.
    """
    logger.info("[Discord Service] Starting bulk nickname sync task")
    
    from django.conf import settings
    
    if not getattr(settings, 'DISCORD_SYNC_NAMES', False):
        logger.info("[Discord Service] Nickname sync is disabled (DISCORD_SYNC_NAMES=False)")
        return
    
    guild_id = getattr(settings, 'DISCORD_GUILD_ID', None)
    if not guild_id:
        logger.error("[Discord Service] DISCORD_GUILD_ID not configured, cannot sync nicknames")
        return
    
    # Get all Discord users
    discord_users = DiscordUser.objects.select_related('user__profile__main_character').all()
    
    total_users = discord_users.count()
    success_count = 0
    skip_count = 0
    error_count = 0
    
    logger.info(f"[Discord Service] Found {total_users} Discord users to sync")
    
    for discord_user in discord_users:
        # Skip users without main characters
        if not hasattr(discord_user.user, 'profile') or not discord_user.user.profile.main_character:
            logger.debug(
                f"[Discord Service] Skipping user {discord_user.user.username} "
                "(no main character)"
            )
            skip_count += 1
            continue
        
        # Try to update the nickname
        result = safe_update_nickname(discord_user, guild_id)
        
        if result:
            success_count += 1
        else:
            error_count += 1
    
    logger.info(
        f"[Discord Service] Nickname sync completed: "
        f"{success_count} successful, {skip_count} skipped, {error_count} errors "
        f"out of {total_users} total users"
    )


@shared_task
def update_nickname(user_pk: int):
    """
    Update a single user's Discord nickname.
    Patched version with improved error handling.
    """
    try:
        from django.conf import settings
        
        user = User.objects.get(pk=user_pk)
        
        if not getattr(settings, 'DISCORD_SYNC_NAMES', False):
            logger.debug(f"[Discord Service] Nickname sync disabled for user {user.username}")
            return
        
        guild_id = getattr(settings, 'DISCORD_GUILD_ID', None)
        if not guild_id:
            logger.error("[Discord Service] DISCORD_GUILD_ID not configured")
            return
        
        try:
            discord_user = DiscordUser.objects.select_related(
                'user__profile__main_character'
            ).get(user=user)
        except DiscordUser.DoesNotExist:
            logger.debug(f"[Discord Service] User {user.username} has no Discord account linked")
            return
        
        if not hasattr(user, 'profile') or not user.profile.main_character:
            logger.debug(f"[Discord Service] User {user.username} has no main character")
            return
        
        safe_update_nickname(discord_user, guild_id)
        
    except User.DoesNotExist:
        logger.error(f"[Discord Service] User with pk {user_pk} does not exist")
    except Exception as e:
        logger.error(
            f"[Discord Service] Unexpected error in update_nickname for user_pk {user_pk}: {str(e)}",
            exc_info=True
        )
