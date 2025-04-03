from django.core.management.base import BaseCommand
from workouts.models import WorkoutPlan
import random

GOALS = [
    ("weight_loss", "Weight Loss & Fat Burn"),
    ("muscle_gain", "Muscle Gain & Strength Training"),
    ("endurance", "Endurance & Stamina Boost"),
    ("flexibility", "Flexibility & Mobility"),
    ("core_strength", "Core & Functional Strength"),
    ("balanced_fitness", "Balanced Fitness & Well-being"),
    ("athletic_performance", "Athletic Performance & Conditioning"),
    ("custom_wellness", "Customized & Holistic Wellness"),
]

INTENSITIES = [
    ("low", "Low"),
    ("moderate", "Moderate"),
    ("high", "High"),
]

class Command(BaseCommand):
    help = "Generate sample workout plans"

    def handle(self, *args, **kwargs):
        for goal_key, goal_name in GOALS:
            for intensity_key, _ in INTENSITIES:
                for i in range(2):  # Create 2 plans for each combo (8x3x2 = 48)
                    title = f"{goal_name} - {intensity_key.capitalize()} Plan {i+1}"
                    description = f"This is a {intensity_key} intensity workout for {goal_name}."
                    WorkoutPlan.objects.create(
                        name=title,
                        description=description,
                        goal=goal_key,
                        intensity=intensity_key,
                        duration_minutes=random.randint(30, 60),
                        is_active=True
                    )
        self.stdout.write(self.style.SUCCESS("✔ Successfully generated 48 workout plans."))