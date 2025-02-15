from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import home, about_view, contact_view, login_view, dashboard_view, enable_2fa_view

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin Panel
    path('auth/', include('social_django.urls', namespace='social')),
    path('', include('users.urls')),
    path('', home, name='home'),  # Home Page
    path("login/", login_view, name="login"),
    path("dashboard/", dashboard_view, name="dashboard"),  # Fixed dashboard path
    path('enable-2fa/', enable_2fa_view, name='enable_2fa'),
    path('about-us/', about_view, name='about'),  # About Us Page
    path('contact/', contact_view, name='contact'),  # Contact Page
    path('api/users/', include('users.urls')),  # User Authentication & Profile
    path('api/workouts/', include('workouts.urls')),  # Workout Management
    path('api/auth/', include('django.contrib.auth.urls')),  # Django Built-in Auth
    path('accounts/', include('allauth.urls')),  # Social Authentication

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
