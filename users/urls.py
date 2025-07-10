from django.urls import path
#from .views import signup_view, login_view, logout_view
from djangoapp.users import views
from django.contrib.auth.views import LogoutView
from .views import signup_view


urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    #path('dashboard/', views.dashboard_view, name='landing'),  # 'landing' points to dashboard
     path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
     path('landing-auth/', views.landing_authenticated, name='landing_authenticated'),
    

]






