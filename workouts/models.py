
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now, timedelta

User = get_user_model()

class Workout(models.Model):
    CATEGORY_CHOICES = [
        ("Strength", "Strength Training"),
        ("Fat Burn", "Fat Burn & Weight Loss"),
        ("Endurance", "Endurance & Stamina Boost"),
        ("Mobility", "Flexibility & Mobility"),
        ("Core", "Functional & Core Strength"),
        ("Personalized", "Personalized Workout & Meal Plan"),
    ]

    DIFFICULTY_CHOICES = [
        ("Beginner", "Beginner"),
        ("Intermediate", "Intermediate"),
        ("Advanced", "Advanced"),
    ]

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    duration_minutes = models.IntegerField()
    video_url = models.URLField(blank=True, null=True)
    description = models.TextField()
    calories_burned_estimate = models.IntegerField()

    def __str__(self):
        return f"{self.title} ({self.difficulty})"


class Exercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="exercises")
    exercise_name = models.CharField(max_length=255)
    sets = models.IntegerField()
    reps = models.IntegerField()
    rest_time_seconds = models.IntegerField()
    instruction_video = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.exercise_name} ({self.workout.title})"


class UserWorkoutTracking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workout_logs")
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    date_completed = models.DateTimeField(auto_now_add=True)
    duration_minutes = models.IntegerField()
    calories_burned = models.IntegerField()
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.workout.title} ({self.date_completed.date()})"

    @staticmethod
    def get_weekly_progress(user):
        last_week = now() - timedelta(days=7)
        return UserWorkoutTracking.objects.filter(user=user, date_completed__gte=last_week).aggregate(
            total_calories=models.Sum('calories_burned'),
            total_duration=models.Sum('duration_minutes')
        )


class Trainer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="trainer_profile")
    assigned_users = models.ManyToManyField(User, related_name="assigned_trainer", blank=True)
    expertise = models.CharField(max_length=255)
    certifications = models.TextField(blank=True, null=True)
    years_of_experience = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Trainer: {self.user.first_name} {self.user.last_name} - {self.expertise}"

class Reminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reminders")
    message = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Reminder for {self.user.username} on {self.date_time}"