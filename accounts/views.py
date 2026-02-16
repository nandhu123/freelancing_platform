from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from .models import Profile





# Redirects to login when someone visits the home page
def home(request):
    return render(request, 'accounts/home.html')


# ✅ Login View (Use Only This)
class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('profile')  # After login go to profile



def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            # Pass the email and role back to template
            context = {'email': email, 'role': role, 'username': username}
            return render(request, 'accounts/register.html', context)

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user, role=role)
        login(request, user)
        return redirect('profile')

    return render(request, 'accounts/register.html')


 


@login_required
def profile(request):
    if request.method == "POST":
        profile = request.user.profile
        profile.role = request.POST['role']
        profile.save()
        return redirect('dashboard')

    return render(request, 'accounts/profile.html', {'profile': request.user.profile})


       
# ✅ Dashboard
@login_required
def dashboard(request):
    profile = request.user.profile
    return render(request, 'accounts/dashboard.html', {'profile': profile})


# ✅ Logout
def user_logout(request):
    logout(request)
    return redirect('home')
