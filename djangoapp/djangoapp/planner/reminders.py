from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.models import User
from datetime import timedelta
from .models import StudySchedule

def send_upcoming_session_reminders():
    now = timezone.now()
    upcoming = now + timedelta(minutes=30)
    schedules = StudySchedule.objects.filter(start_time__range=(now, upcoming), is_completed=False)

    for schedule in schedules:
        user = schedule.user
        subject = "Upcoming Study Session Reminder"
        message = f"Hi {user.username}, your study session for '{schedule.topic.title}' starts in 30 minutes. Get ready!"
        send_mail(subject, message, 'noreply@studyplanner.com', [user.email])

def send_missed_session_reminders():
    now = timezone.now()
    past = now - timedelta(hours=1)
    schedules = StudySchedule.objects.filter(start_time__lt=past, is_completed=False)

    for schedule in schedules:
        user = schedule.user
        subject = "Missed Study Session"
        message = f"Hi {user.username}, you missed your study session for '{schedule.topic.title}'. Want to reschedule?"
        send_mail(subject, message, 'noreply@studyplanner.com', [user.email])

def send_weekly_progress_reports():
    last_week = timezone.now() - timedelta(days=7)
    users = User.objects.all()

    for user in users:
        schedules = StudySchedule.objects.filter(user=user, start_time__gte=last_week)
        hours = sum([s.hours for s in schedules if s.is_completed])
        subject = "Weekly Progress Report"
        message = f"Hi {user.username},\n\nYou studied {hours} hours this week. Keep it up!\nNext week, focus on harder topics."
        send_mail(subject, message, 'noreply@studyplanner.com', [user.email])
