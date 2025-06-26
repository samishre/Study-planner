

# planner/scheduler.py

from datetime import datetime, timedelta
from collections import defaultdict
from .models import StudySchedule, Topic

def generate_schedule(user, available_hours_per_day=3):
    def calculate_score(topic):
        today = datetime.today().date()
        days_left = (topic.subject.exam_date - today).days or 1
        difficulty_map = {'easy': 1, 'medium': 2, 'hard': 3}
        difficulty = difficulty_map.get(topic.difficulty.lower(), 1)
        difficulty_weight = 2
        urgency_weight = 10
        return (difficulty_weight * difficulty) + (urgency_weight / days_left)

    topics = Topic.objects.filter(subject__user=user)
    topics = sorted(topics, key=calculate_score, reverse=True)

    StudySchedule.objects.filter(topic__user=user).delete()

    schedule = defaultdict(list)
    current_date = datetime.today().date()
    topic_index = 0

    while topic_index < len(topics):
        hours_remaining = available_hours_per_day
        while hours_remaining > 0 and topic_index < len(topics):
            topic = topics[topic_index]
            hours_for_topic = min(1, hours_remaining)
            schedule[current_date].append((topic, hours_for_topic))
            hours_remaining -= hours_for_topic
            topic_index += 1
        current_date += timedelta(days=1)

    for date, sessions in schedule.items():
        for topic, hours in sessions:
            StudySchedule.objects.create(
                user=user,
                topic=topic,
                date=date,
                start_time=datetime.combine(date, datetime.min.time()),
                end_time=datetime.combine(date, datetime.min.time()) + timedelta(hours=hours),
                hours=hours
            )