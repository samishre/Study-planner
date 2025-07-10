from django.contrib import admin
from .models import Subject, Topic, UserAvailability, StudySchedule

admin.site.register(Subject)
admin.site.register(Topic)
admin.site.register(UserAvailability)
admin.site.register(StudySchedule)


