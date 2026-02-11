"""
Management command to manage Discord roles that receive notifications
Similar to auth-scripts pattern for managing Discord integrations
"""

# Django
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Add or remove Discord roles that receive Indy Hub notifications"

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            type=str,
            choices=["add", "remove", "list", "clear"],
            help="Action to perform: add, remove, list, or clear all roles",
        )
        parser.add_argument(
            "--role-id",
            type=str,
            help="Discord role ID to add or remove",
        )
        parser.add_argument(
            "--role-name",
            type=str,
            help="Human-readable name for the role (used with add)",
        )

    def handle(self, *args, **options):
        action = options["action"]
        role_id = options.get("role_id")
        role_name = options.get("role_name")

        # Get or initialize the notification roles setting
        notification_roles = self._get_notification_roles()

        if action == "list":
            self._list_roles(notification_roles)
        elif action == "add":
            self._add_role(notification_roles, role_id, role_name)
        elif action == "remove":
            self._remove_role(notification_roles, role_id)
        elif action == "clear":
            self._clear_roles()

    def _get_notification_roles(self):
        """Get current notification roles from settings"""
        return getattr(settings, "INDY_HUB_DISCORD_NOTIFICATION_ROLES", {})

    def _list_roles(self, notification_roles):
        """List all configured notification roles"""
        if not notification_roles:
            self.stdout.write(
                self.style.WARNING("No Discord notification roles configured.")
            )
            self.stdout.write(
                "\nTo add roles, use: python manage.py manage_discord_notification_roles add --role-id <ID> --role-name <NAME>"
            )
            return

        self.stdout.write(self.style.SUCCESS("\n📋 Configured Discord Notification Roles:\n"))
        self.stdout.write("=" * 70)
        
        for role_id, role_info in notification_roles.items():
            role_name = role_info.get("name", "Unknown")
            enabled = role_info.get("enabled", True)
            status = "✓ Enabled" if enabled else "✗ Disabled"
            
            self.stdout.write(f"\nRole ID: {role_id}")
            self.stdout.write(f"Name:    {role_name}")
            self.stdout.write(f"Status:  {status}")
            self.stdout.write("-" * 70)

        self.stdout.write(f"\n{self.style.SUCCESS('Total roles: ' + str(len(notification_roles)))}")
        self.stdout.write(
            "\n💡 Note: To apply changes, update your local.py settings file with:"
        )
        self.stdout.write(self.style.NOTICE(self._generate_settings_snippet(notification_roles)))

    def _add_role(self, notification_roles, role_id, role_name):
        """Add a new notification role"""
        if not role_id:
            raise CommandError("--role-id is required for add action")
        
        if not role_name:
            role_name = f"Role {role_id}"
            self.stdout.write(
                self.style.WARNING(
                    f"No --role-name provided, using default: '{role_name}'"
                )
            )

        if role_id in notification_roles:
            self.stdout.write(
                self.style.WARNING(
                    f"Role {role_id} ({notification_roles[role_id].get('name')}) already exists."
                )
            )
            return

        notification_roles[role_id] = {
            "name": role_name,
            "enabled": True,
        }

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Added role '{role_name}' (ID: {role_id})")
        )
        self.stdout.write(
            "\n💡 To apply this change, add the following to your local.py settings:"
        )
        self.stdout.write(self.style.NOTICE(self._generate_settings_snippet(notification_roles)))

    def _remove_role(self, notification_roles, role_id):
        """Remove a notification role"""
        if not role_id:
            raise CommandError("--role-id is required for remove action")

        if role_id not in notification_roles:
            self.stdout.write(
                self.style.WARNING(f"Role {role_id} not found in configuration.")
            )
            return

        role_info = notification_roles.pop(role_id)
        role_name = role_info.get("name", "Unknown")

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Removed role '{role_name}' (ID: {role_id})")
        )

        if notification_roles:
            self.stdout.write(
                "\n💡 To apply this change, update your local.py settings:"
            )
            self.stdout.write(self.style.NOTICE(self._generate_settings_snippet(notification_roles)))
        else:
            self.stdout.write(
                "\n💡 All roles removed. You can remove INDY_HUB_DISCORD_NOTIFICATION_ROLES from local.py"
            )

    def _clear_roles(self):
        """Clear all notification roles"""
        self.stdout.write(
            self.style.WARNING(
                "This will clear all notification roles. Are you sure? (yes/no): "
            ),
            ending="",
        )
        
        confirmation = input()
        if confirmation.lower() != "yes":
            self.stdout.write(self.style.ERROR("\nCancelled."))
            return

        self.stdout.write(
            self.style.SUCCESS("\n✓ All roles cleared.")
        )
        self.stdout.write(
            "\n💡 Remove INDY_HUB_DISCORD_NOTIFICATION_ROLES from your local.py settings"
        )

    def _generate_settings_snippet(self, notification_roles):
        """Generate the settings snippet for local.py"""
        if not notification_roles:
            return "\n# INDY_HUB_DISCORD_NOTIFICATION_ROLES can be removed\n"

        lines = ["\n# Discord Notification Roles Configuration"]
        lines.append("INDY_HUB_DISCORD_NOTIFICATION_ROLES = {")
        
        for role_id, role_info in notification_roles.items():
            role_name = role_info.get("name", "Unknown")
            enabled = role_info.get("enabled", True)
            lines.append(f'    "{role_id}": {{')
            lines.append(f'        "name": "{role_name}",')
            lines.append(f'        "enabled": {enabled},')
            lines.append('    },')
        
        lines.append("}\n")
        return "\n".join(lines)
