# ======================================
# 🔹 DJANGO IMPORTS
# ======================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.db.models import Sum, Q

# ======================================
# 🔹 MODELS
# ======================================

from .models import Profile, Job, Application, Notification
from .models import Job, Application, Interview


# ======================================
# 🔹 SERIALIZERS
# ======================================

from .serializers import (
    RegisterSerializer,
    FreelancerDashboardSerializer,
    ApplicationSerializer,
    JobSerializer,
)

# ======================================
# 🔹 DRF IMPORTS
# ======================================

from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken


# =====================================================
# 🌐 HOME
# =====================================================

def home(request):
    return render(request, "accounts/home.html")


# ======================================
# 🔐 LOGIN
# ======================================

class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.profile.role == "client":
            return reverse_lazy("recruiter_dashboard")
        return reverse_lazy("dashboard")


# ======================================
# 📝 REGISTER
# ======================================

def register(request):

    if request.method == "POST":

        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        role = request.POST["role"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        Profile.objects.create(user=user, role=role)

        login(request, user)

        return redirect("profile")

    return render(request, "accounts/register.html")


# ======================================
# 👤 PROFILE
# ======================================

@login_required
def profile(request):

    profile = request.user.profile

    if request.method == "POST":

        profile.role = request.POST["role"]
        profile.save()

        if profile.role == "client":
            return redirect("recruiter_dashboard")

        return redirect("dashboard")

    return render(request, "accounts/profile.html", {"profile": profile})


# ======================================
# 👨‍💻 FREELANCER DASHBOARD
# ======================================

@login_required

def dashboard(request):

    if request.user.profile.role != "freelancer":
        return redirect("recruiter_dashboard")

    profile = request.user.profile

    applications = Application.objects.filter(
        freelancer=request.user
    ).order_by("-applied_at")

    jobs = Job.objects.all().order_by("-created_at")

    interviews = Interview.objects.filter(
        freelancer=request.user
    ).order_by("interview_date")

    jobs_applied = applications.count()

    jobs_completed = applications.filter(status="completed").count()

    active_projects = applications.filter(status="accepted").count()

    total_earnings = applications.filter(
        status="completed"
    ).aggregate(total=Sum("job__salary"))["total"] or 0

    applied_job_ids = applications.values_list("job_id", flat=True)

    context = {
        "profile": profile,
        "applications": applications,
        "jobs": jobs,
        "jobs_applied": jobs_applied,
        "jobs_completed": jobs_completed,
        "active_projects": active_projects,
        "total_earnings": total_earnings,
        "applied_job_ids": applied_job_ids,
        "interviews": interviews,
    }

    return render(request, "accounts/dashboard.html", context)


# ======================================
# 🔎 FIND JOBS
# ======================================

@login_required
def find_jobs(request):

    query = request.GET.get("q", "")

    jobs = Job.objects.all().order_by("-created_at")

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    applied_jobs = Application.objects.filter(
        freelancer=request.user
    ).values_list("job_id", flat=True)

    return render(request, "accounts/find_jobs.html", {
        "jobs": jobs,
        "query": query,
        "applied_jobs": list(applied_jobs),
    })


# ======================================
# 📩 APPLY JOB
# ======================================

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Job, Application

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

@login_required
def apply_job(request, job_id):

    job = get_object_or_404(Job, id=job_id)

    Application.objects.get_or_create(
        job=job,
        freelancer=request.user
    )

    messages.success(request, "Application submitted successfully!")

    return redirect("find_jobs")


# ======================================
# 📄 MY APPLICATIONS
# ======================================

@login_required
def my_applications(request):

    applications = Application.objects.filter(
        freelancer=request.user
    ).order_by("-applied_at")

    return render(request, "accounts/my_applications.html", {
        "applications": applications
    })


# ======================================
# 🔔 NOTIFICATIONS
# ======================================

@login_required
def notifications(request):

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return render(request, "accounts/notifications.html", {
        "notifications": notifications,
        "unread_count": unread_count
    })


# ======================================
# 💬 MESSAGES
# ======================================
# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import Message, UserProfile
from django.contrib.auth.models import User

@login_required
def messages_view(request):
    user = request.user
    # List all contacts (opposite role users)
    if hasattr(user, 'userprofile'):
        role = user.userprofile.role
    else:
        role = 'freelancer'  # default if missing

    if role == 'freelancer':
        contacts = UserProfile.objects.filter(role='recruiter')
    else:
        contacts = UserProfile.objects.filter(role='freelancer')

    selected_contact_id = request.GET.get('contact')
    selected_contact = None
    messages = []

    if selected_contact_id:
        selected_contact = User.objects.get(id=selected_contact_id)
        messages = Message.objects.filter(
            sender__in=[user, selected_contact],
            receiver__in=[user, selected_contact]
        ).order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('message')
        receiver_id = request.POST.get('receiver_id')
        if content and receiver_id:
            receiver = User.objects.get(id=receiver_id)
            Message.objects.create(sender=user, receiver=receiver, content=content)
            return redirect(f'/dashboard/messages/?contact={receiver.id}')

    return render(request, 'accounts/messages.html', {
        'contacts': contacts,
        'selected_contact': selected_contact,
        'messages': messages
    })
   
# ======================================
# 🧑‍💼 RECRUITER DASHBOARD
# ======================================

@login_required
def recruiter_dashboard(request):

    jobs = Job.objects.filter(posted_by=request.user)

    applications = Application.objects.filter(
        job__posted_by=request.user
    )

    hired_count = applications.filter(status="accepted").count()

    active_jobs = jobs.filter(status="open").count()

    context = {
        "jobs": jobs,
        "applications": applications,
        "hired_count": hired_count,
        "active_jobs": active_jobs
    }

    return render(request, "accounts/recruiter_dashboard.html", context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Application, Interview

@login_required
def schedule_interview(request, application_id):

    application = get_object_or_404(Application, id=application_id)

    if request.method == "POST":

        interview_date = request.POST.get("interview_date")
        meeting_link = request.POST.get("meeting_link")

        Interview.objects.create(
            freelancer=application.freelancer,
            job=application.job,
            recruiter=request.user,   # ⭐ THIS FIXES THE ERROR
            interview_date=interview_date,
            meeting_link=meeting_link
        )

        return redirect("view_applicants", job_id=application.job.id)

    return render(request, "accounts/schedule_interview.html", {
        "application": application
    })

# ======================================
# 📢 POST JOB
# ======================================

@login_required
def post_job(request):

    if request.method == "POST":

        title = request.POST.get("title")
        description = request.POST.get("description")
        salary = request.POST.get("salary")
        deadline = request.POST.get("deadline")

        Job.objects.create(
            posted_by=request.user,
            title=title,
            description=description,
            salary=salary,
            deadline=deadline
        )

        return redirect("recruiter_dashboard")

    return render(request, "accounts/post_job.html")


# ======================================
# 🧾 MANAGE JOBS
# ======================================

@login_required
def manage_jobs(request):

    jobs = Job.objects.filter(posted_by=request.user)

    return render(request, "accounts/manage_jobs.html", {
        "jobs": jobs
    })


# ======================================
# 👥 VIEW APPLICANTS
# ======================================

from .models import Interview

@login_required
def view_applicants(request, job_id):

    job = get_object_or_404(Job, id=job_id)

    applications = Application.objects.filter(job=job)

    interviews = Interview.objects.filter(job=job)

    # get freelancer ids who already got interview scheduled
    interviewed_freelancers = interviews.values_list("freelancer_id", flat=True)

    return render(request, "accounts/applicants.html", {
        "applications": applications,
        "job": job,
        "interviews": interviews,
        "interviewed_freelancers": interviewed_freelancers
    })


# ======================================
# ✅ ACCEPT APPLICATION
# ======================================
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Application

@login_required
def accept_application(request, app_id):

    application = get_object_or_404(Application, id=app_id)

    if request.method == "POST":
        application.status = "accepted"
        application.save()

    return redirect("view_applicants", job_id=application.job.id)

# ======================================
# ❌ REJECT APPLICATION
# ======================================
@login_required
def reject_application(request, app_id):

    application = get_object_or_404(Application, id=app_id)

    if request.method == "POST":
        application.status = "rejected"
        application.save()

    return redirect("view_applicants", job_id=application.job.id)




# ======================================
# 🔒 CLOSE JOB
# ======================================

@login_required
def close_job(request, job_id):

    job = get_object_or_404(Job, id=job_id)

    job.status = "closed"
    job.save()

    return redirect("manage_jobs")


# ======================================
# 👤 DASHBOARD PROFILE
# ======================================

@login_required
def dashboard_profile(request):

    profile = request.user.profile

    if request.method == "POST":

        profile.bio = request.POST.get("bio")
        profile.experience = request.POST.get("experience")
        profile.save()

    return render(request, "accounts/dashboard_profile.html", {
        "profile": profile
    })


# ======================================
# 🚪 LOGOUT
# ======================================

def user_logout(request):

    logout(request)

    return redirect("home")


# ======================================
# 🔧 PLACEHOLDER PAGES
# ======================================

@login_required
def payments(request):
    return render(request, "accounts/payments.html")


@login_required
def wishlist(request):
    return render(request, "accounts/wishlist.html")


@login_required
def schedule(request):
    return render(request, "accounts/schedule.html")


@login_required
def settings(request):
    return render(request, "accounts/settings.html")


@login_required
def interviews(request):
    return render(request, "accounts/interviews.html")

@login_required
def freelancer_interviews(request):
    # Only freelancers should access this
    if request.user.profile.role != "freelancer":
        return redirect("recruiter_dashboard")

    # Fetch all interviews assigned to this freelancer
    interviews = Interview.objects.filter(
        freelancer=request.user
    ).order_by("interview_date")

    return render(request, "accounts/interviews.html", {  # Keep your template name
        "interviews": interviews
    })


@login_required
def support(request):
    return render(request, "accounts/support.html")


# =====================================================
# 🔐 AUTH APIs
# =====================================================

class RegisterView(generics.CreateAPIView):

    queryset = User.objects.all()

    serializer_class = RegisterSerializer

    permission_classes = [permissions.AllowAny]


class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email
        })


class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:

            refresh_token = request.data["refresh"]

            token = RefreshToken(refresh_token)

            token.blacklist()

            return Response({"message": "Logout successful"})

        except Exception:

            return Response({"error": "Invalid token"})


# =====================================================
# 👨‍💻 FREELANCER API
# =====================================================

class FreelancerDashboardView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        profile, _ = Profile.objects.get_or_create(user=request.user)

        serializer = FreelancerDashboardSerializer(profile)

        return Response(serializer.data)


class FreelancerStatsAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        total_applied = Application.objects.filter(
            freelancer=request.user
        ).count()

        total_completed = Application.objects.filter(
            freelancer=request.user,
            status="completed"
        ).count()

        return Response({
            "jobs_applied": total_applied,
            "jobs_completed": total_completed
        })


# =====================================================
# 💼 JOB APIs
# =====================================================

class JobListAPIView(generics.ListAPIView):

    queryset = Job.objects.all()

    serializer_class = JobSerializer

    permission_classes = [IsAuthenticated]


class ApplyJobAPIView(generics.CreateAPIView):

    serializer_class = ApplicationSerializer

    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        serializer.save(freelancer=self.request.user)


class MyApplicationsAPIView(generics.ListAPIView):

    serializer_class = ApplicationSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Application.objects.filter(
            freelancer=self.request.user
        ).order_by("-applied_at")

from .models import Interview        
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class FreelancerInterviewsAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        interviews = Interview.objects.filter(
            freelancer=request.user
        ).order_by("interview_date")

        data = []

        for interview in interviews:
            data.append({
                "job": interview.job.title,
                "recruiter": interview.recruiter.username,
                "date": interview.interview_date,
                "meeting_link": interview.meeting_link
            })

        return Response(data)
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def api_root(request):
    return Response({
        "register": "/api/register/",
        "login": "/api/login/",
        "profile": "/api/profile/",
        "jobs": "/api/jobs/",
        "apply_job": "/api/jobs/apply/",
        "my_applications": "/api/jobs/my/",
        "freelancer_stats": "/api/freelancer/stats/",
        "interviews": "/api/interviews/"
    })