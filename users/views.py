import json
import logging
import pyotp
import qrcode
import io
import base64
from allauth.socialaccount.models import SocialAccount
from django.db.models import Sum
from django.http import JsonResponse

from meal_plans.models import MealPlan
from workouts.models import WorkoutPlan
from .serializers import UserProfileSerializer
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .forms import ProfileUpdateForm
from datetime import timedelta, date
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib import messages
from rest_framework.decorators import api_view, permission_classes
from .models import FitnessStats, WorkoutProgress, MealPlanReminder
from .serializers import FitnessStatsSerializer, WorkoutProgressSerializer, MealPlanReminderSerializer
from django.utils.timezone import now
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.contrib.auth import logout, login
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .models import User
from .serializers import RegisterSerializer, LoginSerializer
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        if isinstance(user, dict):
            user = User.objects.get(email=user.get("email"))
        send_verification_email(user.email, user)
        return Response({'message': 'User registered successfully. Please verify your email.'}, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class Enable2FAView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        device, created = TOTPDevice.objects.get_or_create(user=user, name='default')
        return Response({"message": "Scan this QR code in Google Authenticator app to enable 2FA", "qr_code": device.config_url})


def send_verification_email(user_email, user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verification_link = f"http://127.0.0.1:8000/api/users/email-verification/{uidb64}/{token}/"
    subject = "Verify Your Email - MyCUFitness"
    message = f"Hello {user.first_name},\n\nClick the link below to verify your email:\n{verification_link}\n\nThanks for using MyCUFitness!"
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email], fail_silently=False)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid verification link.'}, status=status.HTTP_400_BAD_REQUEST)

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.verification_token = None
            user.save()
            return redirect('/login/')  #
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class passwdResetView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"http://127.0.0.1:8000/api/auth/password-reset-confirm/{uid}/{token}/"
            send_mail("Password Reset Request", f"Click the link to reset your password: {reset_url}", settings.EMAIL_HOST_USER, [email])
            return Response({"message": "Password reset link sent to email."}, status=status.HTTP_200_OK)
        return Response({"error": "User with this email not found."}, status=status.HTTP_400_BAD_REQUEST)

class MobileLoginView(generics.GenericAPIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({"access": str(refresh.access_token), "refresh": str(refresh), "user": {"email": user.email, "role": user.role}}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully'}, status=200)
        except Exception:
            return Response({'error': 'Invalid token'}, status=400)

# ✅ Frontend Views (Newly Added)
@login_required
def profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
#I am suing this for currently logged in users profile
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
         #checking th submitted form data, any uploaded picture, updating the existing profile object.
        if form.is_valid():
            user_profile = form.save(commit=False) #without commiting saves the form
            user_profile.user = request.user  # Ensure correct user association

            if 'profile_picture' in request.FILES:
                user_profile.profile_picture = request.FILES['profile_picture']

                user_profile.phone_number = form.cleaned_data['phone_number']
                user_profile.weight = form.cleaned_data['weight']
                user_profile.height = form.cleaned_data['height']
                user_profile.activity_level = form.cleaned_data['activity_level']

                #  Automatically calculate BMI before saving i am fetching this thing from models.py userprofile
                user_profile.calculate_bmi()

            user_profile.save()
            request.user.refresh_from_db()
            messages.success(request, "Profile updated successfully!")
            return redirect("dashboard")  # Redirect immediately after update

    else:
        form = ProfileUpdateForm(instance=user_profile)

    return render(request, "profile.html", {
        "user_profile": user_profile,
        "form": form,
        "MEDIA_URL": settings.MEDIA_URL
    })

@login_required
def dashboard_view(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    # Debugging (Removing this later)
    print(f"Current Logged-in User: {user.email}")
    print(f"Fetched Profile: {user_profile}")
    print(f"Profile Picture Path: {user_profile.profile_picture}")
    print(
        f"Profile Picture URL: {user_profile.profile_picture.url if user_profile.profile_picture else 'No image found'}")  # URL check
    context = {
        "user": user,
        "user_profile": user_profile,
        "fitness_stats": getattr(user_profile, "fitness_stats", "No data available"),
        "weekly_progress": getattr(user_profile, "weekly_progress", {"calories_burned": 0, "workouts_completed": 0}),
        "upcoming_reminders": getattr(user_profile, "upcoming_reminders", []),
        "weight": user_profile.weight or "Not set",
        "height": user_profile.height or "Not set",
        "bmi": user_profile.bmi or "Not calculated",
        "activity_level": user_profile.get_activity_level_display() if hasattr(user_profile, 'get_activity_level_display') else "Not set",
        "fitness_goals": user_profile.get_fitness_goals_display() if hasattr(user_profile, 'get_fitness_goals_display') else "No goal set",
        "dietary_preferences": user_profile.get_dietary_preferences_display() if hasattr(user_profile, 'get_dietary_preferences_display') else "Not specified",
        "allergies": user_profile.get_allergies_display() if hasattr(user_profile, 'get_allergies_display') else "No known allergies",
        "MEDIA_URL": settings.MEDIA_URL,
        "profile_picture": user_profile.profile_picture.url if user_profile.profile_picture else None

    }

    return render(request, "dashboard.html", context)


def google_login(request):
    user = request.user

    if not user.is_authenticated:
        return redirect("login")

    social_account = SocialAccount.objects.filter(user=user, provider="google").first()

    if social_account:
        extra_data = social_account.extra_data

        user.first_name = extra_data.get("given_name", user.first_name)
        user.last_name = extra_data.get("family_name", user.last_name)
        user.phone_number = extra_data.get("phone", user.phone_number)
        user.save()

    user_profile, created = UserProfile.objects.get_or_create(user=user)

    login(request, user)
    messages.success(request, "Logged in successfully!")

    # ✅ Fix: Prompt Google users to set a password if they don’t have one
    if not user.has_usable_password():
        messages.info(request, "Please set a password for manual login.")
        return redirect("set_password")

    return redirect("dashboard")

def google_login_callback(request):
    user = request.user

    # Check if this is the user's first Google login and if they need to set a password
    if user.is_authenticated and not user.has_usable_password():
        return redirect("set_password")  # Redirect to password setup

    return redirect("dashboard")

@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def api_user_profile(request):
    user = request.user

    if not user.is_authenticated:
        return redirect("login")

        # ✅ Get user details from Google login
    social_account = SocialAccount.objects.filter(user=user, provider="google").first()

    if social_account:
        extra_data = social_account.extra_data  # Extract Google account details

        #  Save user first name, last name, and phone number
        user.first_name = extra_data.get("given_name", user.first_name)
        user.last_name = extra_data.get("family_name", user.last_name)
        user.phone_number = extra_data.get("phone", user.phone_number)
        user.save()

    #  Ensure profile exists for Google users
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    #  If user has no password, redirect to password reset
    if not user.has_usable_password():
        messages.info(request, "Please set a password for manual login.")
        return redirect("/accounts/password/reset/")

    #  Log in the user
    login(request, user)
    messages.success(request, "Logged in successfully!")

    # Redirect to dashboard
    return redirect("dashboard")

def calculate_bmi(self):
    if self.weight and self.height:
        self.bmi = round(self.weight / ((self.height / 100) ** 2), 2)
    else:
        self.bmi = None
    self.save()@csrf_protect

logger = logging.getLogger(__name__)
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        logger.info(f"Trying to authenticate user with email: {email}")
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)

            # Redirect based on user role
            if user.role == "admin":
                return redirect("/admin-dashboard/")
            elif user.role == "trainer":
                return redirect("/workouts/trainer-dashboard/")
            else:
                return redirect("dashboard")  # student dashboard

        else:
            messages.error(request, "Invalid email or password.")
            return render(request, "auth/login.html")

    return render(request, "auth/login.html")




def register_view(request):
    if request.method == "POST":
        form_data = {
            "email": request.POST["email"],
            "first_name": request.POST["first_name"],
            "last_name": request.POST["last_name"],
            "phone_number": request.POST["phone"],
            "password": request.POST["password1"],
            "password2": request.POST["password2"],
            "role": request.POST["role"],
            "fitness_goals": request.POST.get("fitness_goals", ""),
            "dietary_preferences": request.POST.get("dietary_preferences", ""),
            "allergies": request.POST.getlist("allergies"),
        }

        serializer = RegisterSerializer(data=form_data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = True  # Require email verification
            user.save()

            profile, created = UserProfile.objects.get_or_create(user=user)

            profile.first_name = user.first_name
            profile.last_name = user.last_name
            profile.phone_number = user.phone_number
            profile.fitness_goals = form_data["fitness_goals"]
            profile.dietary_preferences = form_data["dietary_preferences"]
            profile.allergies = ", ".join(form_data["allergies"]) if isinstance(form_data["allergies"], list) else \
            form_data["allergies"]
            profile.save()

            # ✅ Send only **one** email verification
            send_verification_email(user.email, user)

            messages.success(request, "Account created successfully! Please verify your email.")
            return redirect("verification_sent")

        return render(request, "auth/register.html", {"error": serializer.errors})

    return render(request, "auth/register.html")
def verification_sent_view(request):
    return render(request, "auth/email_verification.html")
@login_required
def set_password_view(request):
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("set_password")

        request.user.set_password(new_password)
        request.user.save()
        messages.success(request, "Password set successfully! You can now log in with email and password.")
        return redirect("dashboard")

    return render(request, "auth/set_password.html")


def password_reset_request_view(request):
    """Handle password reset email request."""
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"http://127.0.0.1:8000/password-reset-confirm/{uid}/{token}/"

            # Send email
            send_mail(
                "Password Reset Request",
                f"Click the link below to reset your password:\n{reset_url}",
                settings.EMAIL_HOST_USER,  # Ensure it's set up correctly
                [email],
                fail_silently=False,  # Keep False for debugging
            )

            messages.success(request, "Password reset link has been sent to your email.")
            return redirect("password_reset_done")  # Redirect to confirmation page

        else:
            messages.error(request, "User with this email not found.")
            return redirect("password_reset_request")

    return render(request, "auth/password_reset_request.html")


def password_reset_confirm_view(request, uidb64, token):
    """Handle password reset confirmation with custom UI."""

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Invalid password reset link.")
        return redirect("password_reset_request")

    if not default_token_generator.check_token(user, token):
        messages.error(request, "The password reset link is invalid or has expired.")
        return redirect("password_reset_request")

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
        else:
            user.set_password(new_password)  # Use Django's built-in function for security
            user.save()
            messages.success(request, "Your password has been successfully reset. You can now log in.")
            return redirect("auth/login")

    return render(request, "auth/password_reset_confirm.html", {"valid_link": True})

@api_view(["GET"])
def user_dashboard(request):
    user = request.user

    # Fetch fitness stats
    stats = FitnessStats.objects.filter(user=user).first()
    stats_data = {
        "calories_burned": stats.total_calories_burned if stats else 0,  # Corrected field name
    "workouts_completed": stats.workouts_completed if stats else 0,  # This field exists

    }

    # Fetch workout history (Last 7 days)
    workouts = WorkoutProgress.objects.filter(user=user, date__gte=now().date() - timedelta(days=7))
    workouts_data = [{"title": w.workout_type, "date": w.date} for w in workouts]

    # Fetch upcoming meal plan reminders
    reminders = MealPlanReminder.objects.filter(user=user, date__gte=now().date()).order_by("scheduled_time")
    # reminders_data = [{"message": r.message, "scheduled_time": r.scheduled_time} for r in reminders]

    return Response({
        "fitness_stats": stats_data,
        "weekly_workouts": workouts_data,
        # "upcoming_meals": reminders_data,
    })


@login_required
def enable_2fa_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Generate a new TOTP secret key if not already generated
    if not user_profile.secret_key:
        user_profile.secret_key = pyotp.random_base32()
        user_profile.save()

    # Generate OTP auth URL
    totp = pyotp.TOTP(user_profile.secret_key)
    otp_auth_url = totp.provisioning_uri(name=request.user.email, issuer_name="MyCUFitness")

    # Generate QR Code
    qr = qrcode.make(otp_auth_url)
    qr_io = io.BytesIO()
    qr.save(qr_io, format='PNG')
    qr_base64 = base64.b64encode(qr_io.getvalue()).decode('utf-8')

    # Return QR Code to frontend
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'qr_code': qr_base64})

    return render(request, 'auth/enable_2fa.html', {'qr_code': qr_base64})
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("/login/")



def email_verification_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True  # Activate the user
        user.save()
        messages.success(request, "Your email has been verified successfully!")
        return redirect("login")
    else:
        messages.error(request, "Invalid or expired verification link.")
        return render(request, "auth/email_verification.html", {"user": user})

@login_required
def resend_verification_email(request):
    user = request.user

    if user.is_active:
        messages.info(request, "Your email is already verified.")
        return redirect("dashboard")

    # ✅ Pass user.email and user object correctly
    send_verification_email(user.email, user)

    messages.success(request, "Verification email has been resent. Please check your inbox.")
    return redirect("login")


def home(request):
    """Render the homepage"""
    return render(request, "index.html")

def about_view(request):
    return render(request, "about.html")

def contact_view(request):
    return render(request, "contact.html")
def workout_plans_view(request):
    return render(request, "workout_plans.html")

class CustomLoginView(LoginView):
    template_name = "auth/login.html"



@api_view(['GET'])
def dashboard_data_view(request):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication required."}, status=401)

    user = request.user
    # Fetch fitness stats for the logged-in user
    fitness_stats = FitnessStats.objects.filter(user=user).first()
    calories_burned = fitness_stats.total_calories_burned if fitness_stats else 0
    workouts_completed = fitness_stats.workouts_completed if fitness_stats else 0

    # Get upcoming reminders
    today = date.today()
    upcoming_reminders = list(MealPlanReminder.objects.filter(date__gte=today).values('meal_name', 'scheduled_time', 'date'))

    return Response({
        'calories_burned': calories_burned,
        'workouts_completed': workouts_completed,
        'upcoming_reminders': upcoming_reminders
    })

