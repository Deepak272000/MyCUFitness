from django.db import models

class MealPlan(models.Model):
    name = models.CharField(max_length = 150)
    description = models.TextField()
    calories = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
