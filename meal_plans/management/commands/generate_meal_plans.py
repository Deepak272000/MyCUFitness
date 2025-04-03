from django.core.management.base import BaseCommand
from meal_plans.models import Meal, MealPlan
import random

# Define preferences and categories
dietary_prefs = [
    "vegetarian", "non-vegetarian", "vegan", "keto", "gluten_free", "none"
]

fitness_goals = [
    "weight_loss", "muscle_gain", "endurance", "flexibility",
    "core_strength", "balanced_fitness", "athletic_performance", "custom_wellness"
]

intensity_levels = ["low", "moderate", "high"]
meal_categories = ["Breakfast", "Lunch", "Dinner", "Snack"]

# Macros based on goal
def get_macros(goal, intensity):
    base = {"low": 300, "moderate": 500, "high": 700}[intensity]
    calories = base + random.randint(50, 100)

    if goal == "weight_loss":
        protein = round(0.3 * calories / 4, 1)
        carbs = round(0.4 * calories / 4, 1)
        fats = round(0.3 * calories / 9, 1)
    elif goal == "muscle_gain":
        protein = round(0.4 * calories / 4, 1)
        carbs = round(0.4 * calories / 4, 1)
        fats = round(0.2 * calories / 9, 1)
    else:
        protein = round(0.3 * calories / 4, 1)
        carbs = round(0.5 * calories / 4, 1)
        fats = round(0.2 * calories / 9, 1)

    return calories, protein, carbs, fats

class Command(BaseCommand):
    help = 'Generate 50 meal plans with meals based on dietary preferences and goals'

    def handle(self, *args, **kwargs):
        MealPlan.objects.all().delete()
        Meal.objects.all().delete()

        for i in range(50):
            dp = random.choice(dietary_prefs)
            goal = random.choice(fitness_goals)
            intensity = random.choice(intensity_levels)

            plan_name = f"{goal.replace('_', ' ').title()} - {dp.title()} - {intensity.title()}"
            plan = MealPlan.objects.create(name=plan_name)

            for category in meal_categories:
                cals, p, c, f = get_macros(goal, intensity)
                meal = Meal.objects.create(
                    name=f"{category} {i+1}",
                    calories=cals,
                    protein=p,
                    carbs=c,
                    fats=f,
                    category=category
                )
                plan.meals.add(meal)

            self.stdout.write(self.style.SUCCESS(f"✅ Created: {plan_name}"))

        self.stdout.write(self.style.SUCCESS("✅ All 50 meal plans created successfully!"))
