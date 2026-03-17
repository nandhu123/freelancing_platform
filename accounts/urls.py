# accounts/urls.py

from django.urls import path
from . import views
from django.contrib.auth.views import LoginView

from .views import (
    RegisterView,
    ProfileView,
    LogoutView,
    FreelancerDashboardView,
    FreelancerStatsAPIView,
    JobListAPIView,
    ApplyJobAPIView,
    MyApplicationsAPIView,
    FreelancerInterviewsAPIView
)
# JWT views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [

    # 🌐 Website URLs
    path('', views.home, name='home'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),

    path('dashboard/find-jobs/', views.find_jobs, name='find_jobs'),
    path('dashboard/my-applications/', views.my_applications, name='my_applications'),

    path('recruiter-dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),

    path('apply-job/', views.apply_job, name='apply_job_page'),
    path("apply-job/<int:job_id>/", views.apply_job, name="apply_job"),

    path("post-job/", views.post_job, name="post_job"),

    path("manage-jobs/", views.manage_jobs, name="manage_jobs"),

    path("applicants/<int:job_id>/", views.view_applicants, name="view_applicants"),

    path("close-job/<int:job_id>/", views.close_job, name="close_job"),

    path("schedule-interview/<int:application_id>/", views.schedule_interview, name="schedule_interview"),

    path("accept/<int:app_id>/", views.accept_application, name="accept_application"),

    path("reject/<int:app_id>/", views.reject_application, name="reject_application"),

    # Dashboard Extra Pages
    path('dashboard/messages/', views.messages_view, name='messages'),
    path('dashboard/messages/<int:user_id>/', views.messages_view, name='messages'),
    path('dashboard/notifications/', views.notifications, name='notifications'),
    path('dashboard/payments/', views.payments, name='payments'),
    path('dashboard/wishlist/', views.wishlist, name='wishlist'),
    path('dashboard/schedule/', views.schedule, name='schedule'),
    path('dashboard/settings/', views.settings, name='settings'),
    path('dashboard/profile/', views.dashboard_profile, name='dashboard_profile'),
    path("interviews/", views.freelancer_interviews, name="freelancer_interviews"),
    path('support/', views.support, name='support'),

    # 🔐 API URLs
    path('api/register/', RegisterView.as_view(), name='api_register'),
    path('api/profile/', ProfileView.as_view(), name='api_profile'),
    path('api/logout/', LogoutView.as_view(), name='api_logout'),

    # JWT Authentication
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Freelancer APIs
    path('api/freelancer-dashboard/', FreelancerDashboardView.as_view(), name='freelancer_dashboard'),
    path('api/freelancer/stats/', FreelancerStatsAPIView.as_view(), name='freelancer_stats'),

    # Job APIs
    path('api/jobs/', JobListAPIView.as_view(), name='job_list'),
    path('api/jobs/apply/', ApplyJobAPIView.as_view(), name='apply_job_api'),
    path('api/jobs/my/', MyApplicationsAPIView.as_view(), name='my_applications_api'),
    path('api/interviews/', FreelancerInterviewsAPIView.as_view(), name='freelancer_interviews_api'),
    path('api/', views.api_root, name='api_root'),


]