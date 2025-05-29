from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Subject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    daily_hours = models.FloatField()

class StudySchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    date = models.DateField()
    # Calendar-friendly fields
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    
    # Optional fields
    hours = models.FloatField()
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.topic.title} on {self.start_time.strftime('%Y-%m-%d %H:%M')}"
