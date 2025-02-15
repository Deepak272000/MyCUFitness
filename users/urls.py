from django.urls import path
from . import views
from .views import (
    home, register_view, login_view, logout_view, dashboard_view,
    profile_view, about_view, contact_view, workout_plans_view,
    password_reset_request_view, password_reset_confirm_view, enable_2fa_view, api_user_profile, UserProfileView,
    email_verification_view, resend_verification_email
)

urlpatterns = [
    path("", home, name="home"),
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("profile/", profile_view, name="profile"),
   # path("api/users/profile/", api_user_profile, name="api-user-profile"),
    path("about-us/", about_view, name="about"),
    path("contact/", contact_view, name="contact"),
    path("password-reset/", password_reset_request_view, name="password_reset_request"),
    path("password-reset-confirm/<uidb64>/<token>/", password_reset_confirm_view, name="password_reset_confirm"),
    path('enable-2fa/', enable_2fa_view, name='enable_2fa'),
    path('api/users/enable-2fa/', enable_2fa_view, name='enable_2fa'),
    path('email-verification/', email_verification_view, name='email_verification'),
    path("workout-plans/", workout_plans_view, name="workout_plans"),
    path('resend-verification/', resend_verification_email, name='resend_verification_email'),

]
