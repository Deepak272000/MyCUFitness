from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User, WorkoutProgress, MealPlanReminder, UserProfile, FitnessStats
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "role", "fitness_goals",
            "dietary_preferences", "allergies", "phone_number", "dob",
            "profile_picture", "fitness_stats", "upcoming_reminders",
            "weekly_progress", "is_active", "date_joined"
        ]
        read_only_fields = ["email", "date_joined", "is_active"]

# User Profile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "first_name", "last_name", "phone_number", "dob",
            "fitness_goals", "dietary_preferences", "allergies",
            "profile_picture"
        ]

# User Profile Update Serializer
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "first_name", "last_name", "phone_number", "dob",
            "fitness_goals", "dietary_preferences", "allergies",
            "profile_picture"
        ]

# User Registration Serializer
class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'phone_number', 'password', 'password2',
            'profile_picture', 'role', 'fitness_goals', 'dietary_preferences', 'allergies'
        )

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        """Create user and return instance without sending email here"""
        validated_data.pop('password2')  # Remove password2 field
        profile_picture = validated_data.pop('profile_picture', None)

        user = User.objects.create_user(**validated_data)
        user.is_active = False  # Require email verification
        user.save()

        if profile_picture:
            user.profile_picture = profile_picture
            user.save()

        # ✅ Removed send_mail() from here to avoid duplicate emails
        return user

# User Login Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = User.objects.filter(email=data['email']).first()
        if user and user.check_password(data['password']):
            token = RefreshToken.for_user(user)
            return {'token': str(token.access_token), 'refresh': str(token)}
        raise serializers.ValidationError("Invalid Credentials")

# Fitness Stats Serializer
class FitnessStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FitnessStats
        fields = '__all__'

# Workout Progress Serializer
class WorkoutProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutProgress
        fields = '__all__'

# Meal Plan Reminder Serializer
class MealPlanReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPlanReminder
        fields = '__all__'