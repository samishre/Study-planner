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

#class UserAvailability(models.Model):
    #user = models.OneToOneField(User, on_delete=models.CASCADE)
    #daily_hours = models.FloatField()

class UserAvailability(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    available_hours_per_day = models.IntegerField()
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.available_hours_per_day} hrs"

class StudySchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    study_date = models.DateField()
    study_hours = models.PositiveIntegerField()
    is_completed = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.topic.title} on {self.study_date}"



