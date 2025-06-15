from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from datetime import datetime
from .models import Subject, Topic, UserAvailability, StudySchedule
from .serializers import SubjectSerializer, TopicSerializer, UserAvailabilitySerializer, StudyScheduleSerializer

# ✅ Import scheduler function
from .scheduler import generate_schedule


def calendar_page(request):
    return render(request, 'planner/calendar.html')


def calendar_events_view(request):
    user = request.user
    schedules = StudySchedule.objects.filter(topic__user=user)

    events = []
    for schedule in schedules:
        events.append({
            "id": schedule.id,
            "title": f"{schedule.topic.subject.name}: {schedule.topic.title}",
            "start": schedule.start_time.isoformat(),
            "end": schedule.end_time.isoformat() if schedule.end_time else None,
            "color": "#28a745" if schedule.is_completed else "#007bff",
        })
    return JsonResponse(events, safe=False)


def home(request):
    return render(request, 'landing.html')


class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer

    def get_queryset(self):
        return Subject.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TopicViewSet(viewsets.ModelViewSet):
    serializer_class = TopicSerializer

    def get_queryset(self):
        return Topic.objects.filter(subject__user=self.request.user)


class UserAvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = UserAvailabilitySerializer

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
        qs = StudySchedule.objects.filter(topic__user=user)
        if start and end:
            qs = qs.filter(start_time__range=[start, end])
        return qs

    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        schedule = self.get_object()
        schedule.completed = True
        schedule.save()
        return Response({'status': 'marked as completed'}, status=200)


# ✅ Refactored to call scheduler.py logic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_schedule_view(request):
    available_hours = request.data.get('available_hours_per_day', None)
    if available_hours:
        generate_schedule(request.user, available_hours_per_day=int(available_hours))
    else:
        generate_schedule(request.user)
    return Response({'message': 'Schedule generated using intelligent heuristic!'})


def dashboard(request):
    return render(request, 'planner/dashboard.html')


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
