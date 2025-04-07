
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.urls import path
from users.views import (
    home, register_view, login_view, logout_view, dashboard_view,
    profile_view, about_view, contact_view, workout_plans_view,
    password_reset_request_view, password_reset_confirm_view, enable_2fa_view,
    api_user_profile, UserProfileView, email_verification_view,
    resend_verification_email, set_password_view, verification_sent_view, google_login_callback,
    CustomLoginView, dashboard_data_view
)

urlpatterns = [
    path("", home, name="home"),
    path("register/", register_view, name="register"),
     path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("profile/", profile_view, name="profile"),
    path("about-us/", about_view, name="about"),
    path("contact/", contact_view, name="contact"),
    path("password-reset/", password_reset_request_view, name="password_reset_request"),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), name='password_reset_done'),
    path("password-reset-confirm/<uidb64>/<token>/", password_reset_confirm_view, name="password_reset_confirm"),
    path("password-reset-complete/", lambda request: render(request, "auth/password_reset_complete.html"), name="password_reset_complete"),
    path("enable-2fa/", enable_2fa_view, name="enable_2fa"),
    path("api/users/enable-2fa/", enable_2fa_view, name="enable_2fa"),
    path('api/users/email-verification/<str:uidb64>/<str:token>/', email_verification_view, name='email_verification'),
    path("workout-plans/", workout_plans_view, name="workout_plans"),
    path("set-password/", set_password_view, name="set_password"),
    path("resend-verification/", resend_verification_email, name="resend_verification_email"),
    path("verification-sent/", verification_sent_view, name="verification_sent"),
    path("google/callback/", google_login_callback, name="google_callback"),
    path("google-login/", google_login_callback, name="google_login"),
    path('dashboard-data/', dashboard_data_view, name='dashboard_data'),

]
