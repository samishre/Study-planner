from django.urls import path, include
from rest_framework.routers import DefaultRouter



from .views import (
    calendar_page,
    calendar_events_view,
    CalendarEventsView,
    SubjectViewSet,
    TopicViewSet,
    UserAvailabilityViewSet,
    StudyScheduleViewSet,
    generate_schedule_view,
    dashboard,
    landing,
    signup_view,
    login_view,
    logout_view,
    views,
)

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'topics', TopicViewSet, basename='topic')
router.register(r'availability', UserAvailabilityViewSet, basename='availability')
router.register(r'study-schedules', StudyScheduleViewSet, basename='schedule')

urlpatterns = [
    # Main calendar page (GET renders calendar)
    path('calendar/', calendar_page, name='calendar'),
    path('', calendar_page, name='calendar'),  # root also goes to calendar

    # API endpoint to fetch events for FullCalendar (function-based)
    path('calendar/events/', calendar_events_view, name='calendar_events'),


    # API endpoint to fetch events for FullCalendar (class-based DRF)
    path('api/calendar-events/', CalendarEventsView.as_view(), name='calendar-events-api'),

    # API endpoint to generate study schedule (POST)
    path('api/generate-schedule/', generate_schedule_view, name='generate-schedule'),

    # Dashboard page
    path('dashboard/', dashboard, name='dashboard'),
  

    # Auth routes
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # REST Framework router for CRUD APIs
    path('api/', include(router.urls)),
]
