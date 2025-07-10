from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings


class Subject(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    exam_date = models.DateField()

    def __str__(self):
        return self.name

class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    difficulty = models.IntegerField()  # 1 (easy) to 5 (hard)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class UserAvailability(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    available_hours_per_day = models.IntegerField()


class StudySchedule(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    study_hours = models.PositiveIntegerField()
    is_completed = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.topic.title} on {self.date}"
    

class StudySession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    topic = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    hours = models.FloatField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)  # ✅ Add this field

    def __str__(self):
        return f"{self.topic} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"


