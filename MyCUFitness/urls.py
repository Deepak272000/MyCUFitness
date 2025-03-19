from allauth.account.views import SignupView, LoginView
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from admin_panel.views import admin_dashboard_view
from users.views import home, about_view, contact_view, dashboard_view, enable_2fa_view, login_view
from users.views import CustomLoginView
urlpatterns = [
     path("admin-dashboard/", admin_dashboard_view, name="admin_dashboard"),  # Admin Dashboard
    path("admin_panel/", include("admin_panel.urls")),
    path('admin/', admin.site.urls),  # Admin Panel
    path('auth/', include('social_django.urls', namespace='social')),
    path('meal_plans/', include('meal_plans.urls')),
    path("", include("users.urls")),  # No namespace
    path('workouts/', include('workouts.urls')),
    path('chatbot/', include('chatbot.urls')),   #urls for chatbot
    path('', home, name='home'),  # Home Page
     path("login/", login_view, name="login"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("dashboard/", dashboard_view, name="dashboard"),  # Fixed dashboard path
    path('enable-2fa/', enable_2fa_view, name='enable_2fa'),
    path('about-us/', about_view, name='about'),  # About Us Page
    path('contact/', contact_view, name='contact'),  # Contact Page
    path('api/users/', include('users.urls')),  # User Authentication & Profile
    path('api/workouts/', include('workouts.urls')),  # Workout Management
    path('api/auth/', include('django.contrib.auth.urls')),  # Django Built-in Auth
    path('accounts/', include('allauth.urls')),  # Social Authentication
    path("social-login/", LoginView.as_view(template_name="socialaccount/login.html"), name="socialaccount_login"),
    path("social-signup/", SignupView.as_view(template_name="socialaccount/signup.html"), name="socialaccount_signup"),
    path("auth/login/", login_view, name="auth_login"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)