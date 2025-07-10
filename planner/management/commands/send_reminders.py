from django.core.management.base import BaseCommand
from planner.reminders import (
    send_upcoming_session_reminders,
    send_break_reminders,
    send_exam_tomorrow_reminders,
)

class Command(BaseCommand):
    help = "Send all study reminders (upcoming, break, missed, weekly, and exam tomorrow)"

    def handle(self, *args, **kwargs):
        self.stdout.write("📢 Starting to send reminders...\n")

        try:
            send_upcoming_session_reminders()
            self.stdout.write(self.style.SUCCESS("✅ Sent upcoming session reminders."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Failed to send upcoming session reminders: {e}"))

        try:
            send_break_reminders()
            self.stdout.write(self.style.SUCCESS("✅ Sent break-over reminders."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Failed to send break-over reminders: {e}"))

        try:
            send_exam_tomorrow_reminders()
            self.stdout.write(self.style.SUCCESS("✅ Sent exam tomorrow reminders."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Failed to send exam tomorrow reminders: {e}"))

        self.stdout.write(self.style.SUCCESS("🏁 All reminders processed.\n"))
