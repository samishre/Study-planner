# users/views.py
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

def login_view(request):
    next_url = request.GET.get('next') 
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url if next_url else 'landing_authenticated')  # Redirect after login
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'users/login.html')


def landing(request):
    if request.user.is_authenticated:
        return redirect('auth_landing')
    return render(request, 'landing.html')


@login_required
def landing_authenticated(request):
    return render(request, 'landing_authenticated.html')


@login_required
def dashboard_view(request):
    return render(request, 'planner/dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login after logout
