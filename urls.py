from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from djangoapp.planner import views

from djangoapp.planner.views import (
    generate_schedule_view,
    SubjectViewSet,
    TopicViewSet,
    UserAvailabilityViewSet,
    StudyScheduleViewSet,
    home,
    calendar_events_view,
    calendar_page,
    toggle_completion,
    landing_authenticated
)

from djangoapp.users.views import signup_view, login_view, dashboard_view, logout_view  # Import logout_view here explicitly
from djangoapp.users import views as user_views

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'topics', TopicViewSet, basename='topic')
router.register(r'useravailability', UserAvailabilityViewSet, basename='useravailability')
router.register(r'studyschedule', StudyScheduleViewSet, basename='studyschedule')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')), 
    
    # API routes (planner app)
    path('api/', include(router.urls)),
    path('api/generate-schedule/', generate_schedule_view, name='generate-schedule'),
    path('api/calendar-events/', calendar_events_view, name='calendar-events'),

    # Pages
    path('', home, name='home'),  # root URL - landing page
    #path('home/', views.landing_authenticated_view, name='home'),
    path('authenticated-home/', landing_authenticated, name='authenticated-home'),

    path('calendar/', calendar_page, name='calendar'),

    # User auth
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),  # Use the imported callable directly

    # Dashboard
    path('dashboard/', dashboard_view, name='dashboard'),

    # User app routes
    path('users/', include('djangoapp.users.urls')),

    #path('api/toggle-completion/', toggle_completion, name='toggle_completion'),
     path('api/toggle-completion/', views.toggle_completion, name='toggle_completion'),

]
