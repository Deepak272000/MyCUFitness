import requests
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from oauth2_provider.models import AccessToken
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
import uuid
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

User = get_user_model()
class ConcordiaSSOLoginView(generics.GenericAPIView):
    def post(self, request):
        token = request.data.get("token")
        # if not token:
        #     return Response({"error": "Token is required"}, status=400)
        #
        #     # Concordia SSO validation URL (Replace with actual URL)
        # sso_validation_url = "https://sso.concordia.ca/oauth2/tokeninfo"
        #
        # try:
        #     # Validate the token with Concordia’s OAuth provider
        #     headers = {"Authorization": f"Bearer {token}"}
        #     response = requests.get(sso_validation_url, headers=headers)
        #
        #     # Print the response to debug
        #     print(f"SSO Response Code: {response.status_code}, Body: {response.text}")
        #
        #     if response.status_code == 200:
        #         sso_user_data = response.json()
        #         email = sso_user_data.get("email")
        #
        #         if email:
        #             # Get or create a user in our system
        #             user, created = User.objects.get_or_create(email=email, defaults={"role": "student"})
        #
        #             return Response({"message": "Authenticated", "user": email}, status=200)
        #
        #     return Response({"error": "Invalid SSO token"}, status=401)
        #
        # except requests.RequestException as e:
        #     return Response({"error": f"Failed to connect to SSO service: {str(e)}"}, status=500)
        try:
            access_token = AccessToken.objects.get(token=token)
            user = authenticate(request, token=token)
            if user:
                return Response({'message': 'Authenticated', 'user': user.email})
        except AccessToken.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=400)

#i am creating this to allow users to create an account
class RegisterView(generics.CreateAPIView):  #basically this will automatically handles post requests for user registration
    queryset = User.objects.all()  #
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()  # Set user as inactive until verification
        #send_verification_email(user.email, user)
        if isinstance(user, dict):  # Check if serializer.save() returned a dict
            user = User.objects.get(email=user.get("email"))  # Retrieve the actual user object

        send_verification_email(user.email, user)
        return Response({'message': 'User registered successfully. Please verify your email.'},
                        status=status.HTTP_201_CREATED)
        #return Response({'message': 'User registered successfully. Please verify your email.'},
         #               status=status.HTTP_201_CREATED)

#now i am handling user authentication(login) with email and passwords
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

        return Response({"message": "Scan this QR code in Google Authenticator app to enable 2FA",
                         "qr_code": device.config_url,
         })

def send_verification_email(user_email, user):
    verification_token = str(uuid.uuid4())  # Generate a unique token
    user.verification_token = verification_token  # Save it to the user model
    user.save()

    subject = "Verify Your Email"
    verification_link = f"http://127.0.0.1:8000/api/users/verify-email/?token={verification_token}"
    message = f"Click the link to verify your email: {verification_link}"

    send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]  # Ensuring any user can access this

    def get(self, request):
        token = request.GET.get("token")
        user = get_object_or_404(User, verification_token=token)

        if user:
            user.is_active = True  # Activate the user
            user.verification_token = None  # Clear the token
            user.save()
            return Response({'message': 'Email verified successfully. You can now log in.'}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

#I am creating password reset feature here basically using this users will receive password reset link via email.
class passwdResetView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"http://127.0.0.1:8000/api/auth/password-reset-confirm/{uid}/{token}/"

            send_mail(
                "Password Reset Request",
                f"Click the link to reset your password: {reset_url}",
                settings.EMAIL_HOST_USER,
                [email],
            )
            return Response({"message": "Password reset link sent to email."}, status=status.HTTP_200_OK)

        return Response({"error": "User with this email not found."}, status=status.HTTP_400_BAD_REQUEST)
        #return Response({"message": "Password reset email sent if user exists."})

#Now i am creating mobile login view: allowing mobile login using email and password:
#so basically, mobile app users can now log in using JWT authentication.
class MobileLoginView(generics.GenericAPIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "email": user.email,
                    "role": user.role,
                }
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsTrainer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'trainer'

from rest_framework_simplejwt.tokens import RefreshToken

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
