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

from django.utils import timezone


from datetime import datetime, timedelta, date
from django.views.decorators.csrf import csrf_exempt
from .models import StudySession
import json


# Simple view to render calendar.html
def calendar_page(request):
    return render(request, 'planner/calendar.html')


# JSON API used by FullCalendar to fetch events
def calendar_events_view(request):
    user = request.user
    schedules = StudySchedule.objects.filter(topic__subject__user=user)

    events = []
    for schedule in schedules:
        start = schedule.start_time
        end = schedule.end_time

        if start:
            start = start.replace(second=0, microsecond=0)
        if end:
            end = end.replace(second=0, microsecond=0)

        events.append({
            "id": schedule.id,
            "title": f"{schedule.topic.subject.name}: {schedule.topic.title}",
            "start": start.isoformat() if start else str(schedule.date),
            "end": end.isoformat() if end else None,
            "color": "#28a745" if schedule.is_completed else "#007bff",
            "is_completed": schedule.is_completed 
        })
    return JsonResponse(events, safe=False)


# DRF API for calendar events
class CalendarEventsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        schedules = StudySchedule.objects.filter(topic__subject__user=request.user)
        data = []
        for schedule in schedules:
            start = schedule.start_time
            end = schedule.end_time

            if start:
                start = start.replace(second=0, microsecond=0)
            if end:
                end = end.replace(second=0, microsecond=0)

            data.append({
                "id": schedule.id,
                "title": schedule.topic.title,
                "start": start,
                "end": end,
                "hours": schedule.study_hours,
                "is_completed": schedule.is_completed
            })
        return Response(data)


# Landing and dashboard pages
def home(request):
    return render(request, 'landing.html')


def dashboard(request):
    return render(request, 'planner/dashboard.html')

@login_required
def landing_authenticated(request):
    return render(request, 'landing_authenticated.html')


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


# ✅ Generate schedule using Gemini AI (updated)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_schedule_view(request):
    if request.method == 'POST':
        print("✅ Gemini schedule generation started")

        user = request.user
        data = request.data

        subject_name = data.get("subject_name")
        exam_date = data.get("exam_date")
        available_hours_per_day = int(data.get("available_hours_per_day"))
        topics_data = data.get("topics", [])

        gemini_response = gemini_generate_schedule(
            subject_name, exam_date, available_hours_per_day, topics_data
        )

        if not gemini_response:
            return Response({"message": "Failed to generate schedule using Gemini."}, status=400)

        subject = Subject.objects.create(name=subject_name, exam_date=exam_date, user=user)

        UserAvailability.objects.create(
            user=user,
            available_hours_per_day=available_hours_per_day,
        )

        topic_map = {}
        for topic in topics_data:
            t = Topic.objects.create(
                subject=subject,
                title=topic["title"],
                difficulty=topic["difficulty"]
            )
            topic_map[t.title.strip().lower()] = t

        created_count = 0
        for item in gemini_response:
            topic_title = item.get('topic', '').strip().lower()
            topic_obj = topic_map.get(topic_title)
            if not topic_obj:
                print(f"⚠ Topic not matched: {topic_title}")
                continue

            try:
                # Parse date and time separately
                date_obj = datetime.strptime(item['date'], "%Y-%m-%d").date()
                start_time_obj = datetime.strptime(item['start_time'], "%H:%M").time()
                end_time_obj = datetime.strptime(item['end_time'], "%H:%M").time()

               # Combine date and time with timezone awareness
                start_datetime = timezone.make_aware(datetime.combine(date_obj, start_time_obj))
                end_datetime = timezone.make_aware(datetime.combine(date_obj, end_time_obj))


            except Exception as e:
                print(f"❌ Invalid time format: {e}")
                continue

            StudySchedule.objects.create(
                user=user,
                topic=topic_obj,
                date=date_obj,
                start_time=start_datetime,
                end_time=end_datetime,
                study_hours=item.get("hours", 1)
            )
            created_count += 1

        print(f"✅ Total schedules saved: {created_count}")
        return Response({"message": "Schedule generated and saved successfully!"})
    



@csrf_exempt
@login_required
def toggle_completion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            schedule_id = data.get('id')
            is_completed = data.get('is_completed')

            schedule = StudySchedule.objects.get(id=schedule_id, user=request.user)
            schedule.is_completed = is_completed
            schedule.save()

            return JsonResponse({'success': True})
        except StudySchedule.DoesNotExist:
            return JsonResponse({'error': 'Schedule not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

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
