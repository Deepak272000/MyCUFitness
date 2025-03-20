from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatbotInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatbot_interactions", null=True, blank=True)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat with {self.user.email if self.user else 'Anonymous'} at {self.timestamp}"

class FitnessProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fitness_progress")
    date = models.DateField(auto_now_add=True)
    weight = models.FloatField(null=True, blank=True)
    calories_burned = models.IntegerField(null=True, blank=True)
    workouts_completed = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.email} - {self.date}"

    def adjust_fitness_plan(self):
        """Adjusts workout and meal plan based on progress."""
        if self.calories_burned < 1500:  # Example threshold
            return "Increase cardio workouts and track calories more carefully."
        elif self.workouts_completed < 3:
            return "Increase workout frequency to at least 3 sessions per week."
        else:
            return "Good progress! Keep following the current plan."
