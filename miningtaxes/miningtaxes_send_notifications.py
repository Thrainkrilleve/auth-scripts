from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from allianceauth.notifications import notify
from miningtaxes.app_settings import MININGTAXES_PING_CURRENT_MSG, MININGTAXES_PING_FIRST_MSG
from miningtaxes.models import Stats
from miningtaxes.tasks import (
    apply_interest,
    notify_current_taxes_threshold,
    notify_second_taxes_due,
    notify_taxes_due,
    send_discord_dm,
)

NOTIFICATION_CHOICES = ["first", "second", "current", "interest", "all"]


class Command(BaseCommand):
    help = "Manually sends tax notification(s) to users"

    def add_arguments(self, parser):
        parser.add_argument(
            "type",
            nargs="?",
            default="all",
            choices=NOTIFICATION_CHOICES,
            help=(
                "Which notification to send: "
                "'first' (taxes due soon), "
                "'second' (taxes due reminder), "
                "'current' (current balance threshold), "
                "'interest' (apply interest + notify), "
                "'all' (send all, default)"
            ),
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Bypass thresholds and notify ALL users with any positive balance",
        )

    def _force_notify(self, notification_type):
        s = Stats.load()
        arr = s.get_admin_main_json()
        count = 0
        for row in arr:
            if row["balance"] < 1:
                continue
            try:
                u = User.objects.get(id=row["user"])
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  Could not find user {row['user']}, skipping."))
                continue

            if notification_type in ("first", "all"):
                title = "Taxes are due soon!"
                message = MININGTAXES_PING_FIRST_MSG.format(row["balance"])
                notify(user=u, title=title, message=message, level="INFO")
                send_discord_dm(u, title, message, "yellow")

            if notification_type in ("second", "all"):
                title = "Taxes are due!"
                from miningtaxes.app_settings import MININGTAXES_PING_SECOND_MSG
                message = MININGTAXES_PING_SECOND_MSG.format(row["balance"])
                notify(user=u, title=title, message=message, level="INFO")
                send_discord_dm(u, title, message, "orange")

            if notification_type in ("current", "all"):
                title = "Taxes are due!"
                message = MININGTAXES_PING_CURRENT_MSG.format(row["balance"])
                notify(user=u, title=title, message=message, level="INFO")
                send_discord_dm(u, title, message, "yellow")

            self.stdout.write(f"  Notified user {u} (balance: {row['balance']:,.2f} ISK)")
            count += 1

        self.stdout.write(self.style.SUCCESS(f"  Sent to {count} user(s)."))

    def handle(self, *args, **options):
        notification_type = options["type"]
        force = options["force"]

        if force:
            self.stdout.write(self.style.WARNING("--force enabled: bypassing thresholds, notifying all users with positive balance."))
            self._force_notify(notification_type)
            return

        if notification_type in ("first", "all"):
            self.stdout.write("Sending first tax reminder (notify_taxes_due)...")
            notify_taxes_due()
            self.stdout.write(self.style.SUCCESS("  Done."))

        if notification_type in ("second", "all"):
            self.stdout.write("Sending second tax reminder (notify_second_taxes_due)...")
            notify_second_taxes_due()
            self.stdout.write(self.style.SUCCESS("  Done."))

        if notification_type in ("current", "all"):
            self.stdout.write("Sending current balance threshold notification (notify_current_taxes_threshold)...")
            notify_current_taxes_threshold()
            self.stdout.write(self.style.SUCCESS("  Done."))

        if notification_type in ("interest", "all"):
            self.stdout.write("Applying interest and notifying (apply_interest)...")
            apply_interest()
            self.stdout.write(self.style.SUCCESS("  Done."))
