from django.db import models

# Define Meal Model
class Meal(models.Model):
    name = models.CharField(max_length=100)
    calories = models.IntegerField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fats = models.FloatField()
    category = models.CharField(max_length=50)  # Example: Breakfast, Lunch, Dinner

    def __str__(self):
        return self.name

# Define MealPlan Model
class MealPlan(models.Model):
    name = models.CharField(max_length=100)
    meals = models.ManyToManyField(Meal)  # ✅ Reference the Meal model
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
