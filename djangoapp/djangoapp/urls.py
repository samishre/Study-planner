from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from planner.views import generate_schedule_view
from django.shortcuts import render

from planner.views import SubjectViewSet, TopicViewSet, UserAvailabilityViewSet, StudyScheduleViewSet  # <- Import them!
from planner.views import home  # or from users.views if home() is there
from users.views import signup_view, login_view, dashboard_view  # import your views
from users import views as user_views


#for calendar
from planner.views import StudyScheduleViewSet
from planner.views import calendar_events_view

from planner.views import calendar_page


# for landing page view
def landing_page(request):
    return render(request, 'landing.html')

router = DefaultRouter()

router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'topics', TopicViewSet, basename='topic')
router.register(r'useravailability', UserAvailabilityViewSet, basename='useravailability')
router.register(r'studyschedule', StudyScheduleViewSet, basename='studyschedule')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/generate-schedule/', generate_schedule_view, name='generate-schedule'),
    path('', home, name='home'), # root URL will render landing page
    path('api/calendar-events/', calendar_events_view, name='calendar-events'),
    path('calendar/', calendar_page, name='calendar-page'),
    path('', include('planner.urls')),
    #path('api/users/', include('users.urls')),
    
    path('', landing_page, name='landing'),
   
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('', user_views.landing, name='guest_landing'),
    path('home/', user_views.landing_authenticated, name='auth_landing'),
    path('dashboard/', dashboard_view , name='dashboard'),
    path('users/', include('users.urls')),  # 👈 include the users app routes
]

   







