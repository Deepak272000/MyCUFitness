from django.urls import path, include
from .views import RegisterView, LoginView, UserProfileView, VerifyEmailView, passwdResetView, Enable2FAView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LogoutView, ConcordiaSSOLoginView
)


urlpatterns = [

    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path("password-reset/", passwdResetView.as_view(), name="password-reset"),
    path("password-reset-confirm/<uidb64>/<token>/", passwdResetView.as_view(), name="password-reset-confirm"),
    path('enable-2fa/', Enable2FAView.as_view(), name='enable-2fa'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/concordia/', ConcordiaSSOLoginView.as_view(), name='concordia_login'),
    path('api/concordia-sso/', ConcordiaSSOLoginView.as_view(), name='concordia_sso'),

]
