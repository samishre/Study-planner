from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.models import User
from datetime import timedelta
from .models import StudySchedule, Subject
from pytz import timezone as pytz_timezone

FROM_EMAIL = 'aistudyplanner2025@gmail.com'
NPT = pytz_timezone('Asia/Kathmandu')  # ✅ Nepal Timezone


def send_upcoming_session_reminders():
    now = timezone.now()
    upcoming = now + timedelta(minutes=30)
    schedules = StudySchedule.objects.filter(
        start_time__range=(now, upcoming),
        is_completed=False
    )

    print(f"⏰ Found {schedules.count()} upcoming sessions")

    for schedule in schedules:
        user = schedule.user
        if not user.email:
            print(f"⚠️ Skipping user {user.username} (no email)")
            continue

        # Convert time to NPT
        start_time_npt = schedule.start_time.astimezone(NPT)
        formatted_time = start_time_npt.strftime('%I:%M %p')

        subject = "Upcoming Study Session Reminder"
        message = (
            f"Hi {user.username},\n\n"
            f"Your study session for '{schedule.topic.title}' starts in 30 minutes "
            f"at {formatted_time} (Nepal Time). Get ready!"
        )

        try:
            send_mail(subject, message, FROM_EMAIL, [user.email])
            print(f"✅ Sent 30-min reminder to {user.email}")
        except Exception as e:
            print(f"❌ Failed to send to {user.email}: {e}")


def send_break_reminders():
    now = timezone.now()
    soon = now + timedelta(minutes=5)
    schedules = StudySchedule.objects.filter(
        start_time__range=(now, soon),
        is_completed=False
    )

    print(f"☕ Found {schedules.count()} sessions starting in 5 mins")

    for schedule in schedules:
        user = schedule.user
        if not user.email:
            print(f"⚠️ Skipping user {user.username} (no email)")
            continue

        # Convert time to NPT
        start_time_npt = schedule.start_time.astimezone(NPT)
        formatted_time = start_time_npt.strftime('%I:%M %p')

        subject = "Break Over: Session Starts in 5 Minutes"
        message = (
            f"Hi {user.username},\n\n"
            f"Your study session '{schedule.topic.title}' starts in 5 minutes "
            f"at {formatted_time} (Nepal Time). Time to refocus!"
        )

        try:
            send_mail(subject, message, FROM_EMAIL, [user.email])
            print(f"✅ Sent 5-min reminder to {user.email}")
        except Exception as e:
            print(f"❌ Failed to send to {user.email}: {e}")


def send_exam_tomorrow_reminders():
    tomorrow = timezone.now().date() + timedelta(days=1)
    users = User.objects.all()

    print(f"📆 Sending exam tomorrow reminders for {tomorrow}")

    for user in users:
        if not user.email:
            print(f"⚠️ Skipping user {user.username} (no email)")
            continue

        exam_subjects = Subject.objects.filter(user=user, exam_date=tomorrow)

        if exam_subjects.exists():
            for subject in exam_subjects:
                subject_line = "📘 Exam Tomorrow Reminder"
                message = (
                    f"Hi {user.username},\n\n"
                    f"Your exam for '{subject.name}' is tomorrow ({tomorrow}).\n"
                    f"Use today to revise and stay confident. Good luck!"
                )

                try:
                    send_mail(subject_line, message, FROM_EMAIL, [user.email])
                    print(f"✅ Sent exam reminder to {user.email} for {subject.name}")
                except Exception as e:
                    print(f"❌ Failed to send to {user.email}: {e}")
