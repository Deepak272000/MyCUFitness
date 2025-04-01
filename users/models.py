from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid
from datetime import date
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser, Group, Permission
from workouts.models import Trainer, WorkoutPlan

default_app_config = 'yourapp.apps.YourAppConfig'

def profile_picture_path(instance, filename):
    return f'profile_pics/{instance.user.username}_{filename}'

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required to create a user. Please enter a valid email address.")
        print(f"Creating user: {email}")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)  #
        extra_fields.setdefault("is_superuser", False)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        print(f"User {email} saved successfully.")  # Debugging line
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()  # Ensure this is here
    username = None
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    dob = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True,
                                        default='profile_pics/default-profile.png')
    two_factor_enabled = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, blank=True, null=True, unique=True)

    fitness_stats = models.JSONField(default=dict, blank=True, null=True)
    weekly_progress = models.JSONField(default=dict, blank=True, null=True)
    upcoming_reminders = models.JSONField(default=dict, blank=True, null=True)


    def save(self, *args, **kwargs):
        if not self.verification_token:
            self.verification_token = str(uuid.uuid4())
        super().save(*args, **kwargs)

    role_choices = [
        ('student', 'Student'),
        ('trainer', 'Trainer'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=role_choices, default='student')

    fitness_goals = models.JSONField(default=dict, blank=True, null=True)
    dietary_preferences = models.JSONField(default=dict, blank=True, null=True)
    allergies = models.JSONField(default=dict, blank=True, null=True)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class FitnessStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_calories_burned = models.IntegerField(default=0)
    workouts_completed = models.IntegerField(default=0)
    last_updated = models.DateField(auto_now=True)

class WorkoutProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout_type = models.CharField(max_length=100)
    duration_minutes = models.IntegerField()
    calories_burned = models.IntegerField()
    date = models.DateField(default=date.today)

class MealPlanReminder(models.Model):
    meal_name = models.CharField(max_length=255)
    scheduled_time = models.TimeField()
    date = models.DateField()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_staff = models.BooleanField(default=False)
    dob = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    bmi = models.FloatField(null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    secret_key = models.CharField(max_length=32, blank=True, null=True)
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.SET_NULL, null=True, blank=True)

    activity_level = models.CharField(
        max_length=20,
        choices=[
            ("low", "Low"),
            ("moderate", "Moderate"),
            ("high", "High"),
        ],
        blank=True,
    )
    assigned_trainer = models.ForeignKey(
        'workouts.Trainer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_students'
    )

    fitness_goals = models.CharField(
        max_length=50,
        choices=[
            ("weight_loss", "Weight Loss & Fat Burn"),
            ("muscle_gain", "Muscle Gain & Strength Training"),
            ("endurance", "Endurance & Stamina Boost"),
            ("flexibility", "Flexibility & Mobility"),
            ("core_strength", "Core & Functional Strength"),
            ("balanced_fitness", "Balanced Fitness & Well-being"),
            ("athletic_performance", "Athletic Performance & Conditioning"),
            ("custom_wellness", "Customized & Holistic Wellness"),
        ],
        blank=True,
        null=True,
        default="General Fitness",
    )

    dietary_preferences = models.CharField(
        max_length=50,
        choices=[
            ("vegetarian", "Vegetarian"),
            ("non-vegetarian", "Non-Vegetarian"),
            ("vegan", "Vegan"),
            ("keto", "Keto"),
            ("gluten_free", "Gluten Free"),
            ("none", "No Preference"),
        ],
        blank=True,
        null=True,
        default="None",
    )

    allergies = models.TextField(blank=True, null=True, default="None")


    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        blank=True,
        null=True,
        default="profile_pics/default.jpg"
    )

    def calculate_bmi(self):
        """Automatically calculate BMI before saving."""
        if self.weight and self.height:
            self.bmi = round(self.weight / ((self.height / 100) ** 2), 2)

    def save(self, *args, **kwargs):
        """Override save method to calculate BMI before saving."""
        self.calculate_bmi()
        super().save(*args, **kwargs)

    @property
    def trainer_profile(self):
        """Returns the associated Trainer profile, if it exists."""
        from workouts.models import Trainer
        return Trainer.objects.filter(user=self.user).first()

    @receiver(post_save, sender=User)
    def create_trainer_profile(sender, instance, created, **kwargs):
        """Automatically creates a Trainer profile if the user is a trainer."""
        from workouts.models import Trainer
        if created or instance.role == "trainer":  # Ensure trainer profile exists
            Trainer.objects.get_or_create(user=instance)

    def get_fitness_goals_display(self):
        """Returns user-friendly fitness goal display"""
        return dict(self._meta.get_field('fitness_goals').choices).get(self.fitness_goals, "No goal set")

    def get_dietary_preferences_display(self):
        """Returns user-friendly dietary preference display"""
        return dict(self._meta.get_field('dietary_preferences').choices).get(self.dietary_preferences, "Not specified")

    def get_allergies_display(self):
        """Returns user-friendly allergies display"""
        return self.allergies if self.allergies else "No known allergies"

    def __str__(self):
        return f"{self.user.email}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()