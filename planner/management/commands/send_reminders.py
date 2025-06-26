from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.db import models
from planner.models import StudySchedule, UserAvailability, Topic
from datetime import timedelta

class Command(BaseCommand):
    help = "Send study reminders and reports to users"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        users = UserAvailability.objects.all()

        for user_avail in users:
            user = user_avail.user

            # 1. Upcoming Study Session Reminder (30 minutes before)
            upcoming_sessions = StudySchedule.objects.filter(
                topic__user=user,
                start_time__gt=now,
                start_time__lte=now + timedelta(minutes=30),
                completed=False
            )
            for session in upcoming_sessions:
                send_mail(
                    subject="Upcoming Study Session Reminder",
                    message=f"Hi {user.username}, your study session for '{session.topic.title}' starts at {session.start_time.strftime('%H:%M')}. Prepare yourself!",
                    from_email="noreply@yourapp.com",
                    recipient_list=[user.email],
                )

            # 2. Missed Session Reminder (session start time in past & not completed)
            missed_sessions = StudySchedule.objects.filter(
                topic__user=user,
                start_time__lt=now - timedelta(minutes=5),
                completed=False
            )
            for session in missed_sessions:
                send_mail(
                    subject="Missed Study Session",
                    message=f"Hi {user.username}, you missed your study session for '{session.topic.title}' scheduled at {session.start_time.strftime('%H:%M')}. Don't worry, you can reschedule it!",
                    from_email="noreply@yourapp.com",
                    recipient_list=[user.email],
                )

            # 3. Weekly Progress Report (send once a week)
            if now.weekday() == 6:  # Sunday
                total_hours = StudySchedule.objects.filter(
                    topic__user=user,
                    start_time__gte=now - timedelta(days=7),
                    completed=True
                ).aggregate(total=models.Sum('hours'))['total'] or 0

                send_mail(
                    subject="Your Weekly Study Progress",
                    message=f"Hi {user.username}, you've completed {total_hours} hours of study in the last week. Keep it up!",
                    from_email="noreply@yourapp.com",
                    recipient_list=[user.email],
                )
