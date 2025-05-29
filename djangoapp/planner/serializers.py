from rest_framework import serializers
from .models import Subject, Topic, UserAvailability

#calendar
from .models import StudySchedule
from rest_framework import serializers

class StudyScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySchedule
        fields = ['id', 'topic', 'start_time', 'completed']
        depth = 1  # to include topic title


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'

class UserAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAvailability
        fields = '__all__'


