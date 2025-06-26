from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

from .gemini_utils import gemini_generate_schedule
from .models import Subject, Topic, UserAvailability, StudySchedule
from .serializers import SubjectSerializer, TopicSerializer, UserAvailabilitySerializer, StudyScheduleSerializer

from datetime import datetime, timedelta


# Simple view to render calendar.html
def calendar_page(request):
    return render(request, 'planner/calendar.html')


# JSON API used by FullCalendar to fetch events
def calendar_events_view(request):
    user = request.user
    schedules = StudySchedule.objects.filter(topic__subject__user=user)

    events = []
    for schedule in schedules:
        events.append({
            "id": schedule.id,
            "title": f"{schedule.topic.subject.name}: {schedule.topic.title}",
            "start": schedule.start_time.isoformat() if schedule.start_time else str(schedule.study_date),
            "end": schedule.end_time.isoformat() if schedule.end_time else None,
            "color": "#28a745" if schedule.is_completed else "#007bff",
        })
    return JsonResponse(events, safe=False)


# DRF API for calendar events
class CalendarEventsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        schedules = StudySchedule.objects.filter(topic__subject__user=request.user)
        data = [
            {
                "title": schedule.topic.title,
                "start": schedule.study_date,
                "end": schedule.study_date,
                "hours": schedule.study_hours
            }
            for schedule in schedules
        ]
        return Response(data)


# Landing and dashboard pages
def home(request):
    return render(request, 'landing.html')


def dashboard(request):
    return render(request, 'planner/dashboard.html')


# ViewSets for API functionality
class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subject.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TopicViewSet(viewsets.ModelViewSet):
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Topic.objects.filter(subject__user=self.request.user)


class UserAvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = UserAvailabilitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserAvailability.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudyScheduleViewSet(viewsets.ModelViewSet):
    queryset = StudySchedule.objects.all()
    serializer_class = StudyScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        qs = StudySchedule.objects.filter(topic__subject__user=user)
        if start and end:
            qs = qs.filter(start_time__range=[start, end])
        return qs

    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        schedule = self.get_object()
        schedule.is_completed = True
        schedule.save()
        return Response({'status': 'marked as completed'}, status=200)


# Generate schedule using Gemini AI
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_schedule_view(request):
    if request.method == 'POST':
        print("✅ Gemini schedule generation started")

        user = request.user
        data = request.data

        # Debug logs
        print("📥 Received data:", data)
        print("📘 Topics data:", data.get("topics"))

        subject_name = data.get("subject_name")
        exam_date = data.get("exam_date")
        available_hours_per_day = int(data.get("available_hours_per_day", 1))
        topics_data = data.get("topics", [])

        print("DEBUG - subject_name:", subject_name)
        print("DEBUG - exam_date:", exam_date)
        print("DEBUG - daily_hours:", available_hours_per_day)
        print("DEBUG - topics_data:", topics_data)

        # Call Gemini AI with full topics data (list of dicts)
        gemini_response = gemini_generate_schedule(
            subject_name, exam_date, available_hours_per_day, topics_data
        )

        if not gemini_response:
            print("❌ Gemini returned no schedule.")
            return Response({"message": "Failed to generate schedule using Gemini."}, status=400)

        # Create Subject
        subject = Subject.objects.create(name=subject_name, exam_date=exam_date, user=user)

        # Create topics and build lowercase title mapping
        topic_map = {}
        for topic in topics_data:
            t = Topic.objects.create(
                subject=subject,
                title=topic["title"],
                difficulty=topic["difficulty"]
            )
            topic_map[t.title.strip().lower()] = t

        # Save study schedule entries
        created_count = 0
        for item in gemini_response:
            try:
                topic_title = item.get('topic', '').strip().lower()
                study_date_str = item.get('date')
                study_hours = int(item.get('hours', 1))

                topic_obj = topic_map.get(topic_title)
                if not topic_obj:
                    print(f"⚠ Topic not found in topic_map: {topic_title}")
                    continue

                study_date = datetime.strptime(study_date_str, "%Y-%m-%d").date()

                print(f"Attempting to save: {topic_title}, Date: {study_date_str}, Hours: {study_hours}")

                schedule = StudySchedule.objects.create(
                    user=user,
                    topic=topic_obj,
                    study_date=study_date,
                    start_time=datetime.combine(study_date, datetime.min.time()),
                    end_time=datetime.combine(study_date, datetime.min.time()) + timedelta(hours=study_hours),
                    study_hours=study_hours
                )
                created_count += 1

            except Exception as e:
                print("❌ Error creating schedule entry:", e)

        print(f"✅ Total schedules saved: {created_count}")
        return Response({"message": "Schedule generated and saved successfully!"})


# Auth views
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'users/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
