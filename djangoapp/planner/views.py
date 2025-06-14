from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subject, Topic, UserAvailability
from .serializers import SubjectSerializer, TopicSerializer, UserAvailabilitySerializer
from .scheduler import generate_schedule
from django.http import HttpResponse
from django.shortcuts import render, redirect

#for login log out 
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

def calendar_page(request):
    return render(request, 'planner/calendar.html')



# for calendar
from django.http import JsonResponse
from .models import StudySchedule
from .serializers import StudyScheduleSerializer
from rest_framework.decorators import action
from rest_framework import status

def calendar_events_view(request):
    user = request.user  # Make sure user is authenticated or adapt for public view
    schedules = StudySchedule.objects.all()

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
    return HttpResponse("Welcome to the Study Planner Home Page!")


# Subject ViewSet
class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    def get_queryset(self):
        return Subject.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Topic ViewSet
class TopicViewSet(viewsets.ModelViewSet):
    serializer_class = TopicSerializer
    def get_queryset(self):
        return Topic.objects.filter(subject__user=self.request.user)

# User Availability ViewSet
class UserAvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = UserAvailabilitySerializer
    def get_queryset(self):
        return UserAvailability.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

#for calendar
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
        return StudySchedule.objects.all()
        

    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        schedule = self.get_object()
        schedule.completed = True
        schedule.save()
        return Response({'status': 'marked as completed'}, status=status.HTTP_200_OK)


# Schedule Generator View
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_schedule_view(request):
    generate_schedule(request.user)
    return Response({'message': 'Schedule generated!'})


#for dashboard frontend
def dashboard(request):
    return render(request, 'planner/dashboard.html')



# Signup View
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # log the user in after signup
            return redirect('dashboard')  # or wherever you want
    else:
        form = UserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')  # or your home page
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')  # back to login after logout


