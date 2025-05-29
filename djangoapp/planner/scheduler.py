from datetime import timedelta, date, datetime, time
from django.utils import timezone
from .models import Subject, Topic, StudySchedule, UserAvailability

def generate_schedule(user):
    today = date.today()

    try:
        availability = UserAvailability.objects.get(user=user)
        daily_hours = availability.daily_hours
    except UserAvailability.DoesNotExist:
        print("User availability not set.")
        return

    # Clear previous schedule
    StudySchedule.objects.filter(user=user).delete()

    # Track hours scheduled per day
    schedule_plan = {}  # {date: hours_used}

    subjects = Subject.objects.filter(user=user).order_by('exam_date')

    for subject in subjects:
        topics = Topic.objects.filter(subject=subject, is_completed=False).order_by('-difficulty')

        for topic in topics:
            hours_needed = 1 + topic.difficulty  # Example: Difficulty 3 => 4 hours
            hours_left = hours_needed

            current_day = today
            while current_day <= subject.exam_date and hours_left > 0:
                hours_used_today = schedule_plan.get(current_day, 0)
                if hours_used_today >= daily_hours:
                    current_day += timedelta(days=1)
                    continue

                available_today = daily_hours - hours_used_today
                hours_to_assign = min(available_today, hours_left)

                # Time slots start at 9:00 AM and stack after previous sessions
                start_hour = 9 + int(hours_used_today)
                start_time = timezone.make_aware(datetime.combine(current_day, time(start_hour)))
                end_time = start_time + timedelta(hours=hours_to_assign)

                # Create schedule entry
                StudySchedule.objects.create(
                    user=user,
                    topic=topic,
                    date=current_day,
                    start_time=start_time,
                    end_time=end_time,
                    hours=hours_to_assign,
                    is_completed=False
                )

                # Update trackers
                schedule_plan[current_day] = hours_used_today + hours_to_assign
                hours_left -= hours_to_assign

                if hours_left > 0:
                    current_day += timedelta(days=1)
