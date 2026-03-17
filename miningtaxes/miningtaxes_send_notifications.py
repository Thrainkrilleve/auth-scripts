from django.core.management.base import BaseCommand

from ...tasks import (
    apply_interest,
    notify_current_taxes_threshold,
    notify_second_taxes_due,
    notify_taxes_due,
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

    def handle(self, *args, **options):
        notification_type = options["type"]

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
