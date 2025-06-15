from django.urls import path
#from .views import signup_view, login_view, logout_view
from users import views


urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    #path('dashboard/', views.dashboard_view, name='landing'),  # 'landing' points to dashboard
]
