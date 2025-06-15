from django.urls import path
#from .views import signup_view, login_view, logout_view
from users import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    #path('dashboard/', views.dashboard_view, name='landing'),  # 'landing' points to dashboard
     path('logout/', LogoutView.as_view(next_page='guest_landing'), name='logout'),
     path('landing-auth/', views.landing_authenticated, name='landing_authenticated'),

]






