from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import generics
#from .serializers import RegisterSerializer


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'fitness_goals', 'dietary_preferences', 'allergies']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'role']

        def validate_email(self, value):
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    "A user with this email already exists. Please use a different email or reset your password.")
            return value

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data.pop('password')
        role = validated_data.get('role', 'student')
        user = User.objects.create(email=validated_data['email'], role=role)
        ser, created = User.objects.get_or_create(email=email, defaults={"role": role})
        #user = User.objects.create_user(**validated_data)
        #user = User(email=validated_data['email'], username=validated_data['username'], role=validated_data['role'])
        user.set_password(password)
        user.save()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verification_url = f"http://127.0.0.1:8000/api/users/verify-email/{uid}/{token}/"

        send_mail(
            "Verify Your Email - MyCUFitness",
            f"Click the link to verify your email: {verification_url}",
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        return {
            "message": "User registered successfully. Please verify your email.",
            "email": user.email,
            "verification_url": verification_url  # Optional, for testing
        }
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = User.objects.filter(email=data['email']).first()
        if user and user.check_password(data['password']):
            token = RefreshToken.for_user(user)
            return {'token': str(token.access_token), 'refresh': str(token)}
        raise serializers.ValidationError("Invalid Credentials")
